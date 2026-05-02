import ast
import re
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr
from sklearn.metrics import (
    accuracy_score,
    auc,
    balanced_accuracy_score,
    cohen_kappa_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from torch.nn import MSELoss
from torch.utils.data import DataLoader

from Dataset import MTLSynergyDataset
from Models import CellLineAE, DrugAE, MTLSynergy
from static.constant import CellAE_OutputDim, DrugAE_OutputDim, Fold
from utils.tools import CategoricalCrossEntropyLoss, set_seed


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DEFAULT_HIDDEN_NEURONS = [8192, 4096, 4096, 2048]


def parse_best_hparams(result_path: Path) -> Dict[int, dict]:
    text = result_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"Test Fold (\d+).*?Best parameters:\s*(\{.*?\})\s*-+",
        re.S,
    )
    parsed = {}
    for fold_text, hp_text in pattern.findall(text):
        parsed[int(fold_text)] = ast.literal_eval(hp_text)
    return parsed


def load_encoders(base_dir: Path):
    drug_ae = DrugAE(output_dim=DrugAE_OutputDim).to(DEVICE)
    cell_ae = CellLineAE(output_dim=CellAE_OutputDim).to(DEVICE)

    drug_path = base_dir / "save" / "AutoEncoder" / f"DrugAE_{DrugAE_OutputDim}.pth"
    cell_path = base_dir / "save" / "AutoEncoder" / f"CellLineAE_{CellAE_OutputDim}.pth"

    drug_ae.load_state_dict(torch.load(drug_path, map_location=DEVICE))
    cell_ae.load_state_dict(torch.load(cell_path, map_location=DEVICE))
    drug_ae.eval()
    cell_ae.eval()
    return drug_ae, cell_ae


def evaluate_fold(
    model: MTLSynergy,
    drug_encoder,
    cell_encoder,
    dataloader: DataLoader,
    test_num: int,
    mse,
    cce,
    fold_test: int,
):
    model.eval()
    y_true1 = torch.Tensor().to(DEVICE)
    y_pred1 = torch.Tensor().to(DEVICE)
    y_true3 = torch.Tensor().long().to(DEVICE)
    y_pred3 = torch.Tensor().to(DEVICE)

    with torch.no_grad():
        for x, y in dataloader:
            d1_features, d2_features, c_features, _sen_fold = x
            d1_features = d1_features.float().to(DEVICE)
            d2_features = d2_features.float().to(DEVICE)
            c_features = c_features.float().to(DEVICE)

            y1, _y2, y3, _y4 = y
            y1 = y1.float().to(DEVICE)
            y3 = y3.long().to(DEVICE)

            y_true1 = torch.cat((y_true1, y1), 0)
            y_true3 = torch.cat((y_true3, y3), 0)

            d1_encoder = drug_encoder(d1_features)
            d2_encoder = drug_encoder(d2_features)
            c_encoder = cell_encoder(c_features)
            out1, _out2, out3, _out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred1 = torch.cat((y_pred1, out1), 0)
            y_pred3 = torch.cat((y_pred3, out3), 0)

    n = test_num // 2
    y_true1 = y_true1[0:n]
    y_true3 = y_true3[0:n]
    y_pred1 = (y_pred1[0:n] + y_pred1[n:]) / 2
    y_pred3 = (y_pred3[0:n, ] + y_pred3[n:, ]) / 2

    test_loss1 = mse(y_pred1, y_true1).item()
    synergy_result = {
        "MSE": test_loss1,
        "RMSE": float(np.sqrt(test_loss1)),
        "Pearsonr": float(pearsonr(y_true1.cpu(), y_pred1.cpu())[0]),
        "CCE": float(cce(y_pred3, y_true3).item()),
    }

    y_true3 = y_true3.cpu()
    y_pred3 = y_pred3.cpu()
    y_pred3_prob = y_pred3[:, 1]
    y_pred3_label = y_pred3.argmax(axis=1)
    y_pred3_prec, y_pred3_recall, _ = precision_recall_curve(y_true3, y_pred3_prob)

    synergy_result["ROC AUC"] = float(roc_auc_score(y_true3, y_pred3_prob))
    synergy_result["PR AUC"] = float(auc(y_pred3_recall, y_pred3_prec))
    synergy_result["ACC"] = float(accuracy_score(y_true3, y_pred3_label))
    synergy_result["PREC"] = float(precision_score(y_true3, y_pred3_label, zero_division=0))
    synergy_result["Recall"] = float(recall_score(y_true3, y_pred3_label, zero_division=0))
    synergy_result["BACC"] = float(balanced_accuracy_score(y_true3, y_pred3_label))
    synergy_result["Kappa"] = float(cohen_kappa_score(y_true3, y_pred3_label))
    return synergy_result


def summarize(per_fold_results: List[dict]) -> Dict[str, List[float]]:
    keys = per_fold_results[0].keys()
    result = {}
    for key in keys:
        values = [row[key] for row in per_fold_results]
        result[key] = [float(np.mean(values)), float(np.std(values))]
    return result


def main():
    base_dir = Path(__file__).resolve().parent
    result_path = base_dir / "result" / "MTLSynergy_result.txt"
    output_path = base_dir / "result" / "MTLSynergy_eval_metrics.txt"

    best_hparams = parse_best_hparams(result_path)
    drugs = pd.read_csv(base_dir / "data" / "drug_features.csv")
    cell_lines = pd.read_csv(base_dir / "data" / "cell_line_features.csv")
    summary = pd.read_csv(base_dir / "data" / "oneil_summary_idx.csv")

    drug_ae, cell_ae = load_encoders(base_dir)
    mse = MSELoss(reduction="mean").to(DEVICE)
    cce = CategoricalCrossEntropyLoss().to(DEVICE)

    output_lines = [
        f"device={DEVICE}",
        f"drug_features_shape={tuple(drugs.shape)}",
        f"cell_line_features_shape={tuple(cell_lines.shape)}",
        f"summary_shape={tuple(summary.shape)}",
        "",
    ]

    per_fold_results = []
    for fold_test in range(Fold):
        set_seed(1)
        test_summary = summary.loc[summary["syn_fold"] == fold_test]
        test_dataset = MTLSynergyDataset(drugs, cell_lines, test_summary)
        test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)
        hp = best_hparams.get(
            fold_test,
            {"learning_rate": 0.0001, "hidden_neurons": DEFAULT_HIDDEN_NEURONS},
        )
        model = MTLSynergy(hp["hidden_neurons"], DrugAE_OutputDim + CellAE_OutputDim).to(DEVICE)
        model_path = base_dir / "save" / "MTLSynergy" / f"fold_{fold_test}.pth"
        model.load_state_dict(torch.load(model_path, map_location=DEVICE))

        fold_result = evaluate_fold(
            model,
            drug_ae.encoder,
            cell_ae.encoder,
            test_loader,
            len(test_dataset),
            mse,
            cce,
            fold_test,
        )
        per_fold_results.append(fold_result)
        output_lines.append(f"fold_{fold_test}: {fold_result}")

    summary_result = summarize(per_fold_results)
    output_lines.extend(["", f"summary: {summary_result}", ""])
    output_path.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
