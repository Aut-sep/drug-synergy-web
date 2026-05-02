from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

import pandas as pd
import torch
from torch.nn import MSELoss
from torch.utils.data import DataLoader


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

    from Dataset import MTLSynergyDataset
    from Models import CellLineAE, DrugAE, MTLSynergy
    from static.constant import CellAE_OutputDim, DrugAE_OutputDim
    from utils.tools import CategoricalCrossEntropyLoss

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    data_dir = project_root / "data"
    save_dir = artifact_root / "save"
    base_df = pd.read_csv(samples_csv).copy()
    drugs = pd.read_csv(data_dir / "drug_features.csv")
    cell_lines = pd.read_csv(data_dir / "cell_line_features.csv")
    drug_index = pd.read_csv(data_dir / "drugs.csv")
    cell_index = pd.read_csv(data_dir / "cell_lines.csv")

    drug_name_to_idx = dict(zip(drug_index["name"], drug_index["id"]))
    cell_name_to_idx = dict(zip(cell_index["name"], cell_index["id"]))

    missing_drugs = sorted(
        {drug for drug in pd.concat([base_df["drug_a_name"], base_df["drug_b_name"]]).unique() if drug not in drug_name_to_idx}
    )
    missing_cells = sorted({cell for cell in base_df["cell_line"].unique() if cell not in cell_name_to_idx})
    if missing_drugs:
        raise ValueError(f"MTLSynergy 缺少药物索引映射: {missing_drugs[:10]}")
    if missing_cells:
        raise ValueError(f"MTLSynergy 缺少细胞索引映射: {missing_cells[:10]}")

    summary = pd.DataFrame(
        {
            "drug_row_idx": base_df["drug_a_name"].map(drug_name_to_idx),
            "drug_col_idx": base_df["drug_b_name"].map(drug_name_to_idx),
            "cell_line_idx": base_df["cell_line"].map(cell_name_to_idx),
            "ri_row": 0.0,
            "ri_col": 0.0,
            "synergy_loewe": 0.0,
            "syn_fold": 0,
            "sen_fold_1": 0,
            "sen_fold_2": 0,
        }
    )
    dataset = MTLSynergyDataset(drugs, cell_lines, summary)
    loader = DataLoader(dataset, batch_size=256, shuffle=False)

    drug_ae = DrugAE(output_dim=DrugAE_OutputDim).to(device)
    cell_ae = CellLineAE(output_dim=CellAE_OutputDim).to(device)
    drug_ae.load_state_dict(torch.load(save_dir / "AutoEncoder" / f"DrugAE_{DrugAE_OutputDim}.pth", map_location=device))
    cell_ae.load_state_dict(torch.load(save_dir / "AutoEncoder" / f"CellLineAE_{CellAE_OutputDim}.pth", map_location=device))
    drug_ae.eval()
    cell_ae.eval()

    result_text_path = artifact_root / "result" / "MTLSynergy_result.txt"
    best_hparams = {}
    if result_text_path.exists():
        text = result_text_path.read_text(encoding="utf-8", errors="ignore")
        pattern = re.compile(r"Test Fold (\d+).*?Best parameters:\s*(\{.*?\})\s*-+", re.S)
        for fold_text, hp_text in pattern.findall(text):
            best_hparams[int(fold_text)] = ast.literal_eval(hp_text)

    mse = MSELoss(reduction="mean").to(device)
    cce = CategoricalCrossEntropyLoss().to(device)
    _ = mse, cce  # keep parity with model env; not used directly

    def predict_once(model_path: Path, fold: int):
        hp = best_hparams.get(fold, {"hidden_neurons": [8192, 4096, 4096, 2048]})
        model = MTLSynergy(hp["hidden_neurons"], DrugAE_OutputDim + CellAE_OutputDim).to(device)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()

        syn_probs = torch.Tensor().to(device)
        with torch.no_grad():
            for x, _y in loader:
                d1_features, d2_features, c_features, _sen_fold = x
                d1_features = d1_features.float().to(device)
                d2_features = d2_features.float().to(device)
                c_features = c_features.float().to(device)
                d1_encoder = drug_ae.encoder(d1_features)
                d2_encoder = drug_ae.encoder(d2_features)
                c_encoder = cell_ae.encoder(c_features)
                _syn_out_1, _d1_sen_out_1, syn_out_2, _d1_sen_out_2 = model(d1_encoder, d2_encoder, c_encoder)
                syn_probs = torch.cat((syn_probs, syn_out_2[:, 1]), 0)

        n = len(dataset) // 2
        merged = (syn_probs[:n] + syn_probs[n:]) / 2
        return merged.detach().cpu().numpy().flatten()

    fold_scores = []
    for fold in range(5):
        model_path = save_dir / "MTLSynergy" / f"fold_{fold}.pth"
        if not model_path.exists():
            raise FileNotFoundError(f"未找到 MTLSynergy 模型文件: {model_path}")
        fold_scores.append(predict_once(model_path, fold))

    score_matrix = pd.DataFrame(fold_scores).T
    final_score = score_matrix.mean(axis=1).round(6)
    result_df = pd.DataFrame(
        {
            "sample_id": base_df["sample_id"],
            "MTLSynergy_score": final_score,
            "MTLSynergy_label": (final_score >= 0.5).astype(int),
        }
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_csv, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
