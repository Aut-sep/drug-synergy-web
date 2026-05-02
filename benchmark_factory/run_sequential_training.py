import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run DualSyn, MFSynDCP, MVCASyn and MTLSynergy sequentially."
    )
    parser.add_argument(
        "--qy-root",
        default="~/文档/undergraduate/2022/QY",
        help="Project root on the training machine.",
    )
    parser.add_argument(
        "--python",
        default="python",
        help="Python executable used to launch child scripts.",
    )
    parser.add_argument(
        "--conda-exe",
        default="conda",
        help="Conda executable used for 'conda run -n ...'.",
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Short experiment tag, used to derive result names.",
    )
    parser.add_argument(
        "--dualsyn-result-name",
        default=None,
        help="Override result name passed to DualSyn/train_transductive.py.",
    )
    parser.add_argument(
        "--dualsyn-env",
        default=None,
        help="Conda environment name used for DualSyn stage.",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Wrap each stage with monitor_training_resources.py.",
    )
    parser.add_argument(
        "--monitor-script",
        default="monitor_training_resources.py",
        help="Path to monitor_training_resources.py, relative to qy-root if not absolute.",
    )
    parser.add_argument(
        "--resource-output-dir",
        default="result_summary/resource_logs",
        help="Directory for resource monitoring outputs, relative to qy-root if not absolute.",
    )
    parser.add_argument(
        "--monitor-interval",
        type=float,
        default=5.0,
        help="Sampling interval in seconds for the monitor.",
    )
    parser.add_argument(
        "--stdout-log",
        action="store_true",
        help="When monitor is enabled, also tee child stdout to log files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the resolved stage commands without executing them.",
    )
    parser.add_argument(
        "--save-models",
        action="store_true",
        help="Keep model checkpoints for MFSynDCP and MVCASyn. By default only metrics are kept.",
    )
    parser.add_argument(
        "--skip-dualsyn",
        action="store_true",
        help="Skip DualSyn stage.",
    )
    parser.add_argument(
        "--skip-mfsyndcp-creat-data",
        action="store_true",
        help="Skip MFSynDCP creat_data.py preprocessing stage.",
    )
    parser.add_argument(
        "--skip-mfsyndcp",
        action="store_true",
        help="Skip MFSynDCP stage.",
    )
    parser.add_argument(
        "--mfsyndcp-result-prefix",
        default=None,
        help="Override result prefix passed to MFSynDCP/training.py.",
    )
    parser.add_argument(
        "--mfsyndcp-env",
        default=None,
        help="Conda environment name used for MFSynDCP stages.",
    )
    parser.add_argument(
        "--mfsyndcp-result-tag",
        default=None,
        help="Override result tag passed to MFSynDCP/training.py.",
    )
    parser.add_argument(
        "--mvcasyn-result-name",
        default=None,
        help="Override result name passed to MVCASyn/cv_train.py.",
    )
    parser.add_argument(
        "--mvcasyn-env",
        default=None,
        help="Conda environment name used for MVCASyn stage.",
    )
    parser.add_argument(
        "--mtlsynergy-env",
        default=None,
        help="Conda environment name used for MTLSynergy stages.",
    )
    parser.add_argument(
        "--skip-mvcasyn",
        action="store_true",
        help="Skip MVCASyn stage.",
    )
    parser.add_argument(
        "--skip-aetrain",
        action="store_true",
        help="Skip MTLSynergy AEtrain stage.",
    )
    parser.add_argument(
        "--skip-mtlsynergy",
        action="store_true",
        help="Skip MTLSynergytrain stage.",
    )
    return parser


def resolve_under_root(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (root / path).resolve()


def resolve_project_dir(root: Path, *candidates: str) -> Path:
    for candidate in candidates:
        path = (root / candidate).resolve()
        if path.exists():
            return path
    candidate_text = ", ".join(candidates)
    raise FileNotFoundError(f"None of the expected project directories exist under {root}: {candidate_text}")


def command_to_pretty(command: List[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def build_python_command(args: argparse.Namespace, env_name: str, script: Path, extra: List[str]) -> List[str]:
    if env_name:
        return [args.conda_exe, "run", "-n", env_name, args.python, str(script), *extra]
    return [args.python, str(script), *extra]


def wrap_with_monitor(
    args: argparse.Namespace,
    qy_root: Path,
    stage_tag: str,
    workdir: Path,
    inner_command: List[str],
) -> List[str]:
    monitor_script = resolve_under_root(qy_root, args.monitor_script)
    resource_output_dir = resolve_under_root(qy_root, args.resource_output_dir)
    command = [
        args.python,
        str(monitor_script),
        "--tag",
        stage_tag,
        "--output-dir",
        str(resource_output_dir),
        "--interval",
        str(args.monitor_interval),
        "--workdir",
        str(workdir),
    ]
    if args.stdout_log:
        command.append("--stdout-log")
    command.append("--")
    command.extend(inner_command)
    return command


def run_stage(
    label: str,
    command: List[str],
    workdir: Path,
    dry_run: bool = False,
) -> None:
    print("\n" + "=" * 80)
    print(f"[START] {label}")
    print(f"[WORKDIR] {workdir}")
    print(f"[COMMAND] {command_to_pretty(command)}")
    print("=" * 80)
    if dry_run:
        print(f"[DRY-RUN] {label} not executed.")
        return
    completed = subprocess.run(command, cwd=str(workdir))
    if completed.returncode != 0:
        raise SystemExit(f"{label} failed with return code {completed.returncode}")
    print(f"[DONE] {label}")


def main() -> None:
    args = build_parser().parse_args()
    qy_root = Path(args.qy_root).expanduser().resolve()

    dualsyn_result_name = args.dualsyn_result_name or f"DualSyn_{args.tag}"
    mfsyndcp_prefix = args.mfsyndcp_result_prefix or f"MFSynDCP_{args.tag}"
    mfsyndcp_tag = args.mfsyndcp_result_tag or args.tag
    mvcasyn_result_name = args.mvcasyn_result_name or args.tag

    stages: List[Tuple[str, Path, List[str], str]] = []

    if not args.skip_dualsyn:
        workdir = (qy_root / "DualSyn" / "DualSyn").resolve()
        inner_command = build_python_command(
            args,
            args.dualsyn_env,
            workdir / "train_transductive.py",
            ["--result-name", dualsyn_result_name],
        )
        if not args.save_models:
            inner_command.append("--no-save-models")
        stages.append(("DualSyn", workdir, inner_command, f"dualsyn_{args.tag}"))

    if not args.skip_mfsyndcp:
        workdir = (qy_root / "MFSynDCP" / "MFSynDCP").resolve()
        if not args.skip_mfsyndcp_creat_data:
            inner_command = build_python_command(args, args.mfsyndcp_env, workdir / "creat_data.py", [])
            stages.append(("MFSynDCP_creat_data", workdir, inner_command, f"mfsyndcp_creat_data_{args.tag}"))
        inner_command = build_python_command(args, args.mfsyndcp_env, workdir / "training.py", [
            "--result-prefix",
            mfsyndcp_prefix,
            "--result-tag",
            mfsyndcp_tag,
        ])
        if not args.save_models:
            inner_command.append("--no-save-models")
        stages.append(("MFSynDCP", workdir, inner_command, f"mfsyndcp_{args.tag}"))

    if not args.skip_mvcasyn:
        workdir = (qy_root / "MVCASyn").resolve()
        inner_command = build_python_command(args, args.mvcasyn_env, workdir / "cv_train.py", [
            "--result-name",
            mvcasyn_result_name,
        ])
        if not args.save_models:
            inner_command.append("--no-save-models")
        stages.append(("MVCASyn", workdir, inner_command, f"mvcasyn_{args.tag}"))

    if not args.skip_aetrain:
        workdir = resolve_project_dir(qy_root, "MTLSynergy", "MTLSynergy-main")
        inner_command = build_python_command(args, args.mtlsynergy_env, workdir / "AEtrain.py", [])
        stages.append(("MTLSynergy_AEtrain", workdir, inner_command, f"mtlsynergy_ae_{args.tag}"))

    if not args.skip_mtlsynergy:
        workdir = resolve_project_dir(qy_root, "MTLSynergy", "MTLSynergy-main")
        inner_command = build_python_command(args, args.mtlsynergy_env, workdir / "MTLSynergytrain.py", [])
        stages.append(("MTLSynergytrain", workdir, inner_command, f"mtlsynergy_main_{args.tag}"))

    if not stages:
        raise SystemExit("No stages selected. Remove skip flags or choose at least one stage.")

    for label, workdir, inner_command, stage_tag in stages:
        command = (
            wrap_with_monitor(args, qy_root, stage_tag, workdir, inner_command)
            if args.monitor
            else inner_command
        )
        run_stage(label, command, workdir, dry_run=args.dry_run)

    if args.dry_run:
        print("\nDry-run finished. No stage was executed.")
    else:
        print("\nAll selected stages finished successfully.")


if __name__ == "__main__":
    main()
