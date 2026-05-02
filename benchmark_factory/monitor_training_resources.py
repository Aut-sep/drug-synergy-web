import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

try:
    import psutil
except ImportError as exc:
    raise SystemExit(
        "psutil is required for monitor_training_resources.py. "
        "Install it with: pip install psutil"
    ) from exc


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_call(fn, default):
    try:
        return fn()
    except Exception:
        return default


def get_descendant_processes(root_pid: int) -> List[psutil.Process]:
    try:
        root = psutil.Process(root_pid)
    except psutil.Error:
        return []
    try:
        return [root] + root.children(recursive=True)
    except psutil.Error:
        return [root]


def prime_cpu_counters(processes: Iterable[psutil.Process]) -> None:
    for proc in processes:
        safe_call(lambda p=proc: p.cpu_percent(interval=None), 0.0)
    psutil.cpu_percent(interval=None)


def read_system_metrics() -> Dict[str, float]:
    vm = psutil.virtual_memory()
    return {
        "system_cpu_percent": safe_call(lambda: psutil.cpu_percent(interval=None), 0.0),
        "system_mem_percent": vm.percent,
        "system_mem_used_gb": vm.used / (1024 ** 3),
        "system_mem_total_gb": vm.total / (1024 ** 3),
    }


def read_process_metrics(root_pid: int) -> Dict[str, float]:
    processes = get_descendant_processes(root_pid)
    cpu = 0.0
    rss = 0
    vms = 0
    proc_count = 0
    pids: List[int] = []
    for proc in processes:
        try:
            cpu += proc.cpu_percent(interval=None)
            mem = proc.memory_info()
            rss += mem.rss
            vms += mem.vms
            proc_count += 1
            pids.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {
        "process_cpu_percent": cpu,
        "process_rss_mb": rss / (1024 ** 2),
        "process_vms_mb": vms / (1024 ** 2),
        "process_count": proc_count,
        "process_pids": pids,
    }


def has_nvidia_smi() -> bool:
    try:
        completed = subprocess.run(
            ["nvidia-smi", "--help"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return completed.returncode == 0
    except OSError:
        return False


def query_gpu_overview() -> List[Dict[str, object]]:
    cmd = [
        "nvidia-smi",
        "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
        "--format=csv,noheader,nounits",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return []
    rows: List[Dict[str, object]] = []
    for line in completed.stdout.strip().splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 7:
            continue
        rows.append(
            {
                "gpu_index": int(parts[0]),
                "gpu_name": parts[1],
                "gpu_util_percent": float(parts[2]),
                "gpu_mem_used_mb": float(parts[3]),
                "gpu_mem_total_mb": float(parts[4]),
                "gpu_temp_c": float(parts[5]) if parts[5] not in {"[N/A]", "N/A"} else None,
                "gpu_power_w": float(parts[6]) if parts[6] not in {"[N/A]", "N/A"} else None,
            }
        )
    return rows


def query_gpu_process_memory() -> Dict[int, float]:
    cmd = [
        "nvidia-smi",
        "--query-compute-apps=pid,used_memory",
        "--format=csv,noheader,nounits",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return {}
    pid_to_mem: Dict[int, float] = {}
    for line in completed.stdout.strip().splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2:
            continue
        try:
            pid_to_mem[int(parts[0])] = float(parts[1])
        except ValueError:
            continue
    return pid_to_mem


def read_gpu_metrics(root_pid: int) -> Dict[str, object]:
    if not has_nvidia_smi():
        return {
            "gpu_available": False,
            "gpu_count": 0,
            "gpu_util_percent_max": 0.0,
            "gpu_mem_used_mb_max": 0.0,
            "gpu_mem_total_mb_max": 0.0,
            "target_gpu_mem_mb": 0.0,
            "target_gpu_process_count": 0,
            "gpu_snapshot": [],
        }

    gpu_rows = query_gpu_overview()
    gpu_pid_mem = query_gpu_process_memory()
    process_pids = set(read_process_metrics(root_pid)["process_pids"])
    target_gpu_mem_mb = sum(mem for pid, mem in gpu_pid_mem.items() if pid in process_pids)
    return {
        "gpu_available": True,
        "gpu_count": len(gpu_rows),
        "gpu_util_percent_max": max((row["gpu_util_percent"] for row in gpu_rows), default=0.0),
        "gpu_mem_used_mb_max": max((row["gpu_mem_used_mb"] for row in gpu_rows), default=0.0),
        "gpu_mem_total_mb_max": max((row["gpu_mem_total_mb"] for row in gpu_rows), default=0.0),
        "target_gpu_mem_mb": target_gpu_mem_mb,
        "target_gpu_process_count": sum(1 for pid in gpu_pid_mem if pid in process_pids),
        "gpu_snapshot": gpu_rows,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Launch a training command and record CPU/GPU/memory usage to CSV."
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Short run name, used in output filenames.",
    )
    parser.add_argument(
        "--output-dir",
        default="result_summary/resource_logs",
        help="Directory where CSV/JSON/log files will be written.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Sampling interval in seconds.",
    )
    parser.add_argument(
        "--workdir",
        default=".",
        help="Working directory used to launch the training command.",
    )
    parser.add_argument(
        "--stdout-log",
        action="store_true",
        help="Also capture child stdout/stderr to a log file under output-dir.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Training command to execute. Use '--' before the command.",
    )
    return parser


def strip_command_prefix(command: List[str]) -> List[str]:
    if command and command[0] == "--":
        return command[1:]
    return command


def stream_output(pipe, log_handle) -> None:
    try:
        for raw_line in iter(pipe.readline, b""):
            if not raw_line:
                break
            text = raw_line.decode(errors="replace")
            sys.stdout.write(text)
            sys.stdout.flush()
            if log_handle is not None:
                log_handle.write(text)
                log_handle.flush()
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def main() -> None:
    args = build_parser().parse_args()
    command = strip_command_prefix(args.command)
    if not command:
        raise SystemExit("No training command was provided. Example: -- python train.py")

    output_dir = Path(args.output_dir).resolve()
    ensure_dir(output_dir)
    workdir = Path(args.workdir).resolve()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_tag = args.tag.replace(" ", "_")
    csv_path = output_dir / f"{safe_tag}_{timestamp}_resource_log.csv"
    meta_path = output_dir / f"{safe_tag}_{timestamp}_meta.json"
    child_log_path = output_dir / f"{safe_tag}_{timestamp}_stdout.log"

    stdout_handle = None
    stderr_handle = None
    tee_thread = None
    if args.stdout_log:
        stdout_handle = child_log_path.open("w", encoding="utf-8")
        stderr_handle = subprocess.STDOUT

    start_time = time.time()
    child = subprocess.Popen(
        command,
        cwd=str(workdir),
        stdout=subprocess.PIPE if args.stdout_log else None,
        stderr=stderr_handle,
        text=False,
    )

    if args.stdout_log and child.stdout is not None:
        tee_thread = threading.Thread(
            target=stream_output,
            args=(child.stdout, stdout_handle),
            daemon=True,
        )
        tee_thread.start()

    metadata = {
        "tag": args.tag,
        "started_at": iso_now(),
        "command": command,
        "workdir": str(workdir),
        "interval_sec": args.interval,
        "pid": child.pid,
        "stdout_log": str(child_log_path) if args.stdout_log else None,
    }
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "timestamp",
        "elapsed_sec",
        "pid",
        "returncode",
        "system_cpu_percent",
        "system_mem_percent",
        "system_mem_used_gb",
        "system_mem_total_gb",
        "process_cpu_percent",
        "process_rss_mb",
        "process_vms_mb",
        "process_count",
        "gpu_available",
        "gpu_count",
        "gpu_util_percent_max",
        "gpu_mem_used_mb_max",
        "gpu_mem_total_mb_max",
        "target_gpu_mem_mb",
        "target_gpu_process_count",
    ]

    prime_cpu_counters(get_descendant_processes(child.pid))

    try:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            while True:
                elapsed = time.time() - start_time
                process_metrics = read_process_metrics(child.pid)
                system_metrics = read_system_metrics()
                gpu_metrics = read_gpu_metrics(child.pid)
                row = {
                    "timestamp": iso_now(),
                    "elapsed_sec": round(elapsed, 2),
                    "pid": child.pid,
                    "returncode": "" if child.poll() is None else child.returncode,
                    **system_metrics,
                    **{k: v for k, v in process_metrics.items() if k != "process_pids"},
                    **{k: v for k, v in gpu_metrics.items() if k != "gpu_snapshot"},
                }
                writer.writerow(row)
                f.flush()

                if child.poll() is not None:
                    break
                time.sleep(args.interval)
    except KeyboardInterrupt:
        try:
            child.send_signal(signal.SIGINT)
        except Exception:
            pass
        raise
    finally:
        if tee_thread is not None:
            tee_thread.join(timeout=2)
        if stdout_handle is not None:
            stdout_handle.close()

    metadata.update(
        {
            "ended_at": iso_now(),
            "returncode": child.returncode,
            "resource_csv": str(csv_path),
        }
    )
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Training command finished with return code {child.returncode}")
    print(f"Resource log saved to: {csv_path}")
    print(f"Metadata saved to: {meta_path}")
    if args.stdout_log:
        print(f"Child stdout/stderr log saved to: {child_log_path}")


if __name__ == "__main__":
    main()
