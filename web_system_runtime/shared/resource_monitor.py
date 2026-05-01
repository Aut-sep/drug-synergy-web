from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover - optional dependency at runtime
    psutil = None  # type: ignore[assignment]


def _iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _safe_call(fn, default):
    try:
        return fn()
    except Exception:
        return default


def _get_descendant_processes(root_pid: int) -> list[Any]:
    if psutil is None:
        return []
    try:
        root = psutil.Process(root_pid)
    except psutil.Error:
        return []
    try:
        return [root] + root.children(recursive=True)
    except psutil.Error:
        return [root]


def _prime_cpu_counters(root_pid: int) -> None:
    if psutil is None:
        return
    processes = _get_descendant_processes(root_pid)
    for proc in processes:
        _safe_call(lambda p=proc: p.cpu_percent(interval=None), 0.0)
    _safe_call(lambda: psutil.cpu_percent(interval=None), 0.0)


def _read_system_metrics() -> dict[str, float]:
    if psutil is None:
        return {
            "system_cpu_percent": 0.0,
            "system_mem_percent": 0.0,
            "system_mem_used_gb": 0.0,
            "system_mem_total_gb": 0.0,
        }
    vm = psutil.virtual_memory()
    return {
        "system_cpu_percent": _safe_call(lambda: psutil.cpu_percent(interval=None), 0.0),
        "system_mem_percent": vm.percent,
        "system_mem_used_gb": vm.used / (1024 ** 3),
        "system_mem_total_gb": vm.total / (1024 ** 3),
    }


def _read_process_metrics(root_pid: int) -> dict[str, float]:
    if psutil is None:
        return {
            "process_cpu_percent": 0.0,
            "process_rss_mb": 0.0,
            "process_vms_mb": 0.0,
            "process_count": 0.0,
        }

    processes = _get_descendant_processes(root_pid)
    cpu = 0.0
    rss = 0
    vms = 0
    proc_count = 0
    for proc in processes:
        try:
            cpu += proc.cpu_percent(interval=None)
            mem = proc.memory_info()
            rss += mem.rss
            vms += mem.vms
            proc_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {
        "process_cpu_percent": cpu,
        "process_rss_mb": rss / (1024 ** 2),
        "process_vms_mb": vms / (1024 ** 2),
        "process_count": float(proc_count),
    }


def _round_number(value: float, digits: int = 2) -> float:
    return round(float(value), digits)


def _series_stats(samples: list[dict[str, float]], key: str) -> tuple[float, float]:
    values = [float(sample.get(key, 0.0) or 0.0) for sample in samples]
    if not values:
        return 0.0, 0.0
    return sum(values) / len(values), max(values)


def summarize_resource_samples(samples: list[dict[str, float]]) -> dict[str, float]:
    if not samples:
        return {
            "duration_sec": 0.0,
            "process_cpu_percent_avg": 0.0,
            "process_cpu_percent_max": 0.0,
            "process_rss_mb_avg": 0.0,
            "process_rss_mb_max": 0.0,
            "process_vms_mb_avg": 0.0,
            "process_vms_mb_max": 0.0,
            "process_count_max": 0.0,
            "system_cpu_percent_avg": 0.0,
            "system_cpu_percent_max": 0.0,
            "system_mem_percent_avg": 0.0,
            "system_mem_percent_max": 0.0,
            "system_mem_used_gb_avg": 0.0,
            "system_mem_used_gb_max": 0.0,
        }

    process_cpu_avg, process_cpu_max = _series_stats(samples, "process_cpu_percent")
    process_rss_avg, process_rss_max = _series_stats(samples, "process_rss_mb")
    process_vms_avg, process_vms_max = _series_stats(samples, "process_vms_mb")
    process_count_avg, process_count_max = _series_stats(samples, "process_count")
    system_cpu_avg, system_cpu_max = _series_stats(samples, "system_cpu_percent")
    system_mem_avg, system_mem_max = _series_stats(samples, "system_mem_percent")
    system_mem_used_avg, system_mem_used_max = _series_stats(samples, "system_mem_used_gb")
    duration_sec = max(float(sample.get("elapsed_sec", 0.0) or 0.0) for sample in samples)

    return {
        "duration_sec": _round_number(duration_sec),
        "process_cpu_percent_avg": _round_number(process_cpu_avg),
        "process_cpu_percent_max": _round_number(process_cpu_max),
        "process_rss_mb_avg": _round_number(process_rss_avg),
        "process_rss_mb_max": _round_number(process_rss_max),
        "process_vms_mb_avg": _round_number(process_vms_avg),
        "process_vms_mb_max": _round_number(process_vms_max),
        "process_count_avg": _round_number(process_count_avg),
        "process_count_max": _round_number(process_count_max),
        "system_cpu_percent_avg": _round_number(system_cpu_avg),
        "system_cpu_percent_max": _round_number(system_cpu_max),
        "system_mem_percent_avg": _round_number(system_mem_avg),
        "system_mem_percent_max": _round_number(system_mem_max),
        "system_mem_used_gb_avg": _round_number(system_mem_used_avg),
        "system_mem_used_gb_max": _round_number(system_mem_used_max),
    }


class ProcessResourceMonitor:
    def __init__(self, root_pid: int, interval_sec: float = 1.0) -> None:
        self.root_pid = int(root_pid)
        self.interval_sec = max(0.2, float(interval_sec))
        self._samples: list[dict[str, float | str]] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._started_at = 0.0
        self._started = False

    def start(self) -> None:
        if psutil is None or self._started:
            return
        self._started = True
        self._started_at = time.time()
        _prime_cpu_counters(self.root_pid)
        self.capture_once()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        while not self._stop_event.wait(self.interval_sec):
            self.capture_once()

    def capture_once(self) -> None:
        if psutil is None or not self._started:
            return
        row = {
            "timestamp": _iso_now(),
            "elapsed_sec": _round_number(time.time() - self._started_at),
            **_read_system_metrics(),
            **_read_process_metrics(self.root_pid),
        }
        with self._lock:
            self._samples.append(row)

    def stop(self, returncode: int | None = None) -> dict[str, object]:
        if psutil is None:
            return {
                "monitoring_available": False,
                "detail": "psutil is not installed.",
                "interval_sec": self.interval_sec,
                "sample_count": 0,
                "samples": [],
                "returncode": returncode,
                **summarize_resource_samples([]),
            }

        if not self._started:
            return {
                "monitoring_available": False,
                "detail": "resource monitor was not started.",
                "interval_sec": self.interval_sec,
                "sample_count": 0,
                "samples": [],
                "returncode": returncode,
                **summarize_resource_samples([]),
            }

        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval_sec + 1.0)
        self.capture_once()

        with self._lock:
            samples = [
                {
                    key: (_round_number(value) if isinstance(value, float) else value)
                    for key, value in sample.items()
                }
                for sample in self._samples
            ]

        return {
            "monitoring_available": True,
            "detail": "",
            "interval_sec": self.interval_sec,
            "sample_count": len(samples),
            "samples": samples,
            "returncode": returncode,
            **summarize_resource_samples(samples),
        }
