# Benchmark Factory

This folder is isolated from the old intersection workflow. Its job is:

- define one fixed canonical input format
- export four model-specific datasets aligned to the original code layouts in `md_for_ai`
- generate one shared 5-fold transductive protocol for fair comparison

## What It Exports

Given one canonical input bundle, the script writes:

- `exports/<dataset_name>/dualsyn/data/...`
- `exports/<dataset_name>/mfsyndcp/data/...`
- `exports/<dataset_name>/mvcasyn/data/...`
- `exports/<dataset_name>/mtlsynergy/data/...`
- `exports/<dataset_name>/protocol/fold_assignments.csv`
- `exports/<dataset_name>/protocol/manifest.json`

The exported file names match the original projects:

- DualSyn: `smiles.csv`, `cell_features_954.csv`, `fold0..fold4/train.csv,test.csv`
- MFSynDCP: `smiles.csv`, `cell_features.csv`, `labels.csv`, `fold/fold0..fold4/train.csv,test.csv`
- MVCASyn: `oneil_drug_two_smiles.csv`, `exp.csv`, `cn.csv`, `folds/folds0..fold4/train.csv,test.csv`
- MTLSynergy: `drugs.csv`, `drug_features.csv`, `cell_lines.csv`, `cell_line_features.csv`, `oneil_summary_idx.csv`

## Unified Comparison Rule

Use the shared `transductive_fold` as the default benchmark protocol for all four models.

Fair-comparison constraints:

- the same sample universe is exported to all four models
- the same binary label rule is used for all four models
- the same `transductive_fold` split is used for all four models
- unordered drug pairs are grouped before fold assignment to avoid `(A,B,cell)` and `(B,A,cell)` leaking across train and test

Extra protocol fields are still exported:

- `cell_fold` for leave-cell experiments
- `drug_a_fold` and `drug_b_fold` for leave-drug experiments
- MTLSynergy receives `syn_fold`, `sen_fold_1`, `sen_fold_2`, and a separate leave-cell file with `fold`

## Command

```powershell
python .\benchmark_factory\build_benchmark_dataset.py `
  --input-root D:\codex\bishe_base\my_dataset_bundle `
  --output-root D:\codex\bishe_base\benchmark_factory\exports `
  --dataset-name my_dataset `
  --label-source threshold `
  --label-threshold 10 `
  --default-ri 0 `
  --fold-strategy pair_group `
  --fold-count 5 `
  --seed 20260413
```

If your input bundle already has a fixed binary label:

```powershell
python .\benchmark_factory\build_benchmark_dataset.py `
  --input-root D:\codex\bishe_base\my_dataset_bundle `
  --output-root D:\codex\bishe_base\benchmark_factory\exports `
  --dataset-name my_dataset `
  --label-source existing
```

## Important Caveat

MTLSynergy originally uses both synergy and drug-response supervision. If `samples.csv` does not provide `ri_row` and `ri_col`, the script fills them with `--default-ri` so the original reader can still load the files, but that is not equivalent to a faithful original multitask benchmark.

## Fold Strategy

The shared 5-fold split supports three modes:

- `pair_group`: keep the same unordered drug pair in one fold. This is the recommended thesis protocol.
- `pair_cell_group`: keep the same unordered drug pair plus cell line in one fold.
- `sample_group`: random sample-level split.

Use `pair_group` for the main benchmark if you want a stricter and fairer comparison.

## Smoke Datasets

The checked-in `example_bundle`, `exports/smoke_test`, and
`exports/smoke_test_pair_group` now come from a real-dimension subset of the
O'Neil intersection bundle instead of a toy three-drug demo. This keeps:

- DualSyn and MFSynDCP cell features at 954 dimensions
- MVCASyn `exp.csv` at 4004 dimensions and `cn.csv` at 3895 dimensions
- MTLSynergy drug and cell features at 1213 and 5000 dimensions

Rebuild them at any time with:

```powershell
python .\benchmark_factory\build_smoke_test_bundle.py
python .\benchmark_factory\validate_smoke_exports.py
```

## Unified Metrics Summary

Prepare one per-fold metrics CSV with columns like:

```csv
fold,roc_auc,pr_auc,acc,bacc,precision,recall,kappa
fold0,0.81,0.77,0.74,0.72,0.70,0.76,0.48
fold1,0.79,0.75,0.73,0.71,0.69,0.74,0.46
```

Then summarize it:

```powershell
python .\benchmark_factory\summarize_fold_metrics.py D:\path\to\metrics.csv
```
