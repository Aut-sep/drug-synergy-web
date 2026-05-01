from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd


MODEL_LABEL_THRESHOLD = {
    "DualSyn": 0.5,
    "MFSynDCP": 0.5,
    "MVCASyn": 0.5,
    "MTLSynergy": 0.5,
}

PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"
AGREEMENT_FULL = "Full agreement"
AGREEMENT_MIXED = "Mixed vote"
CONSENSUS_STABLE = "Stable"
CONSENSUS_DIVERGENT = "Divergent"


def priority_label(score: float) -> str:
    if score >= 0.70:
        return PRIORITY_HIGH
    if score >= 0.50:
        return PRIORITY_MEDIUM
    return PRIORITY_LOW


def finalize_result_table(result_df: pd.DataFrame, selected_models: List[str], run_mode: str) -> pd.DataFrame:
    score_columns = [f"{model_name}_score" for model_name in selected_models if f"{model_name}_score" in result_df.columns]
    label_columns = [f"{model_name}_label" for model_name in selected_models if f"{model_name}_label" in result_df.columns]
    if not score_columns or not label_columns:
        raise ValueError("No model score/label columns were produced for the selected models.")

    result_df = result_df.copy()
    result_df["ensemble_score"] = result_df[score_columns].mean(axis=1).round(4)
    result_df["ensemble_label"] = (result_df["ensemble_score"] >= 0.5).astype(int)
    result_df["score_std"] = result_df[score_columns].std(axis=1).fillna(0.0).round(4)
    result_df["max_model_score"] = result_df[score_columns].max(axis=1).round(4)
    result_df["min_model_score"] = result_df[score_columns].min(axis=1).round(4)
    result_df["top_model"] = result_df[score_columns].idxmax(axis=1).str.replace("_score", "", regex=False)
    result_df["positive_vote_count"] = result_df[label_columns].sum(axis=1).astype(int)
    result_df["model_agreement"] = result_df["positive_vote_count"].map(
        lambda count: AGREEMENT_FULL if count in (0, len(label_columns)) else AGREEMENT_MIXED
    )
    result_df["priority_level"] = result_df["ensemble_score"].map(priority_label)
    result_df["consensus_note"] = result_df["score_std"].apply(
        lambda value: CONSENSUS_STABLE if value <= 0.08 else CONSENSUS_DIVERGENT
    )
    result_df["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_df["run_mode"] = run_mode
    result_df = result_df.sort_values(by=["ensemble_score", "max_model_score"], ascending=[False, False]).reset_index(
        drop=True
    )
    result_df.insert(0, "rank", result_df.index + 1)
    return result_df


def build_run_summary(result_df: pd.DataFrame, selected_models: List[str], result_path: Path) -> Dict[str, object]:
    return {
        "result_path": str(result_path),
        "row_count": len(result_df),
        "selected_models": selected_models,
        "high_priority_count": int((result_df["priority_level"] == PRIORITY_HIGH).sum()),
        "medium_priority_count": int((result_df["priority_level"] == PRIORITY_MEDIUM).sum()),
        "low_priority_count": int((result_df["priority_level"] == PRIORITY_LOW).sum()),
        "ensemble_score_mean": float(result_df["ensemble_score"].mean().round(4)),
        "ensemble_positive_count": int(result_df["ensemble_label"].sum()),
    }
