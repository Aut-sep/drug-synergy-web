from __future__ import annotations

import argparse
from collections import OrderedDict
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

import pandas as pd
import torch


def load_compatible_state_dict(model: torch.nn.Module, model_path: Path, device: torch.device) -> None:
    state_dict = torch.load(model_path, map_location=device)
    if any(key.endswith(".lin.weight") for key in state_dict.keys()) and not any(
        key.endswith(".lin_src.weight") for key in state_dict.keys()
    ):
        remapped = OrderedDict()
        for key, value in state_dict.items():
            if key.endswith(".lin.weight"):
                prefix = key[: -len(".lin.weight")]
                remapped[f"{prefix}.lin_src.weight"] = value
                remapped[f"{prefix}.lin_dst.weight"] = value.clone()
            else:
                remapped[key] = value
        state_dict = remapped
    model.load_state_dict(state_dict, strict=True)


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--samples-csv", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--artifact-root", default="")
    return parser


def main() -> None:
    args = build_argparser().parse_args()
    project_root = Path(args.project_root).resolve()
    samples_csv = Path(args.samples_csv).resolve()
    output_csv = Path(args.output_csv).resolve()
    artifact_root = Path(args.artifact_root).resolve() if args.artifact_root else project_root

    sys.path.insert(0, str(project_root))
    import os

    os.chdir(project_root)

    from creat_data import creat_data
    from models.MFSynDCP import MFSynDCP
    from utils_test import DataLoader, TestbedDataset

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data_dir = project_root / "data"

    smiles_df = pd.read_csv(data_dir / "smiles.csv")
    name_to_smile = dict(zip(smiles_df["name"], smiles_df["smile"]))

    base_df = pd.read_csv(samples_csv).copy()
    missing_drugs = sorted(
        {drug for drug in pd.concat([base_df["drug_a_name"], base_df["drug_b_name"]]).unique() if drug not in name_to_smile}
    )
    if missing_drugs:
        raise ValueError(f"MFSynDCP 缺少药物 SMILES 映射: {missing_drugs[:10]}")

    temp_token = f"streamlit_mfsyndcp_{uuid.uuid4().hex[:8]}"
    runtime_root = Path(tempfile.mkdtemp(prefix=f"{temp_token}_"))
    runtime_data_dir = runtime_root / "data"
    runtime_data_dir.mkdir(parents=True, exist_ok=True)
    temp_csv = runtime_data_dir / f"{temp_token}.csv"
    temp_df = pd.DataFrame(
        {
            "drug1": base_df["drug_a_name"].map(name_to_smile),
            "drug2": base_df["drug_b_name"].map(name_to_smile),
            "cell": base_df["cell_line"],
            "label": 0,
        }
    )
    temp_df.to_csv(temp_csv, index=False)

    temp_datasets = [f"{temp_token}_drug1", f"{temp_token}_drug2"]
    shutil.copy2(data_dir / "smiles.csv", runtime_data_dir / "smiles.csv")
    shutil.copy2(data_dir / "cell_features.csv", runtime_data_dir / "cell_features.csv")

    try:
        os.chdir(runtime_root)
        creat_data(temp_token, str(runtime_data_dir / "cell_features.csv"), csv_path=str(temp_csv))
        drug1_data = TestbedDataset(root="data", dataset=temp_datasets[0])
        drug2_data = TestbedDataset(root="data", dataset=temp_datasets[1])
        loader1 = DataLoader(drug1_data, batch_size=128, shuffle=False)
        loader2 = DataLoader(drug2_data, batch_size=128, shuffle=False)

        def predict_once(model_path: Path):
            model = MFSynDCP().to(device)
            load_compatible_state_dict(model, model_path, device)
            model.eval()
            total_preds = torch.Tensor()
            with torch.no_grad():
                for data in zip(loader1, loader2):
                    data1 = data[0].to(device)
                    data2 = data[1].to(device)
                    output = model(data1, data2)
                    ys = torch.softmax(output, 1).detach().cpu().numpy()
                    total_preds = torch.cat((total_preds, torch.Tensor(ys[:, 1])), 0)
            return total_preds.numpy().flatten()

        fold_scores = []
        result_dir = artifact_root / "result"
        for fold in range(5):
            model_path = result_dir / f"MFSynDCP_fold{fold}.model"
            if not model_path.exists():
                raise FileNotFoundError(f"未找到 MFSynDCP 模型文件: {model_path}")
            fold_scores.append(predict_once(model_path))

        score_matrix = pd.DataFrame(fold_scores).T
        final_score = score_matrix.mean(axis=1).round(6)
        result_df = pd.DataFrame(
            {
                "sample_id": base_df["sample_id"],
                "MFSynDCP_score": final_score,
                "MFSynDCP_label": (final_score >= 0.5).astype(int),
            }
        )
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    finally:
        os.chdir(project_root)
        shutil.rmtree(runtime_root, ignore_errors=True)


if __name__ == "__main__":
    main()
