from __future__ import annotations

import argparse
import sys
import functools
from pathlib import Path
import weakref

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from torch_geometric.data import Batch, Data
from torch_geometric.nn.conv import MessagePassing


def ensure_wrapped_hook_compat() -> None:
    module_mod = torch.nn.modules.module
    if hasattr(module_mod, "_WrappedHook"):
        return

    class _WrappedHook:
        def __init__(self, hook, module=None):
            self.hook = hook
            self.with_module = module is not None
            if module is not None:
                self.module = weakref.ref(module)
            functools.update_wrapper(self, hook)

        def __call__(self, *args, **kwargs):
            if self.with_module:
                module = self.module()
                if module is None:
                    raise RuntimeError("You are trying to call the hook of a dead Module!")
                return self.hook(module, *args, **kwargs)
            return self.hook(*args, **kwargs)

        def __getstate__(self):
            result = {"hook": self.hook, "with_module": self.with_module}
            if self.with_module:
                result["module"] = self.module()
            return result

        def __setstate__(self, state):
            self.hook = state["hook"]
            self.with_module = state.get("with_module", False)
            if self.with_module:
                module = state.get("module")
                if module is None:
                    raise RuntimeError("You are trying to revive the hook of a dead Module!")
                self.module = weakref.ref(module)
            functools.update_wrapper(self, self.hook)

    module_mod._WrappedHook = _WrappedHook


def ensure_numpy_pickle_compat() -> None:
    sys.modules.setdefault("numpy._core", np.core)
    sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)


def hydrate_message_passing_modules(model: torch.nn.Module) -> None:
    for module in model.modules():
        if isinstance(module, MessagePassing):
            if not hasattr(module, "decomposed_layers"):
                module.decomposed_layers = 1
            if not hasattr(module, "__explain__"):
                module.__explain__ = False


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

    from data_preprocessing import (
        MOL_EDGE_LIST_FEAT_MTX,
        BipartiteData,
        cn_features,
        drug_to_mol_graph,
        exp_features,
        get_bipartite_graph,
    )

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    base_df = pd.read_csv(samples_csv).copy()

    class InferenceDataset(Dataset):
        def __init__(self, samples: pd.DataFrame):
            self.samples = []
            for row in samples.itertuples(index=False):
                if row.drug_a_name in MOL_EDGE_LIST_FEAT_MTX and row.drug_b_name in MOL_EDGE_LIST_FEAT_MTX:
                    self.samples.append((row.sample_id, row.drug_a_name, row.drug_b_name, row.cell_line))

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, index):
            return self.samples[index]

        @staticmethod
        def _create_graph_data(drug_name: str):
            edge_index, n_features = MOL_EDGE_LIST_FEAT_MTX[drug_name]
            return Data(x=n_features, edge_index=edge_index)

        @staticmethod
        def _create_b_graph(edge_index, x_s, x_t):
            return BipartiteData(edge_index, x_s, x_t)

        def collate_fn(self, batch):
            sample_ids = []
            h_samples = []
            t_samples = []
            b_samples = []
            cn_rows = []
            exp_rows = []

            for sample_id, da, db, cell in batch:
                sample_ids.append(sample_id)
                cn_data = cn_features.loc[
                    cn_features["cell_line_name"] == cell, cn_features.columns != "cell_line_name"
                ].values
                exp_data = exp_features.loc[
                    exp_features["cell_line_name"] == cell, exp_features.columns != "cell_line_name"
                ].values
                if len(cn_data) == 0 or len(exp_data) == 0:
                    raise ValueError(f"MVCASyn 缺少细胞特征: {cell}")

                h_data = self._create_graph_data(da)
                t_data = self._create_graph_data(db)
                h_graph = drug_to_mol_graph[da]
                t_graph = drug_to_mol_graph[db]
                b_graph = self._create_b_graph(get_bipartite_graph(h_graph, t_graph), h_data.x, t_data.x)

                h_samples.append(h_data)
                t_samples.append(t_data)
                b_samples.append(b_graph)
                cn_rows.append(cn_data)
                exp_rows.append(exp_data)

            triples = (
                Batch.from_data_list(h_samples),
                Batch.from_data_list(t_samples),
                torch.tensor(cn_rows, dtype=torch.float32),
                torch.tensor(exp_rows, dtype=torch.float32),
                Batch.from_data_list(b_samples),
            )
            return sample_ids, triples

    dataset = InferenceDataset(base_df)
    loader = DataLoader(dataset, batch_size=128, shuffle=False, collate_fn=dataset.collate_fn)

    def predict_once(model_path: Path):
        ensure_wrapped_hook_compat()
        ensure_numpy_pickle_compat()
        model = torch.load(model_path, map_location=device)
        hydrate_message_passing_modules(model)
        model.to(device)
        model.eval()
        sample_ids_all = []
        scores_all = []
        with torch.no_grad():
            for sample_ids, triples in loader:
                h_data, t_data, cn_data, exp_data, b_graph = triples
                h_data = h_data.to(device)
                t_data = t_data.to(device)
                cn_data = cn_data.to(device)
                exp_data = exp_data.to(device)
                b_graph = b_graph.to(device)
                logits = model((h_data, t_data, cn_data, exp_data, b_graph))
                probs = torch.sigmoid(logits).detach().cpu().numpy().flatten()
                sample_ids_all.extend(sample_ids)
                scores_all.extend(probs.tolist())
        return pd.DataFrame({"sample_id": sample_ids_all, "score": scores_all})

    fold_frames = []
    model_dir = artifact_root / "results" / "model"
    for fold in range(5):
        model_path = model_dir / f"fold{fold}_model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"未找到 MVCASyn 模型文件: {model_path}")
        fold_df = predict_once(model_path).rename(columns={"score": f"fold_{fold}_score"})
        fold_frames.append(fold_df)

    merged = fold_frames[0]
    for fold_df in fold_frames[1:]:
        merged = merged.merge(fold_df, on="sample_id", how="inner")

    score_cols = [column for column in merged.columns if column.endswith("_score")]
    merged["MVCASyn_score"] = merged[score_cols].mean(axis=1).round(6)
    merged["MVCASyn_label"] = (merged["MVCASyn_score"] >= 0.5).astype(int)
    result_df = merged[["sample_id", "MVCASyn_score", "MVCASyn_label"]]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_csv, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
