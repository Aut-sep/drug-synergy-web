# Input Schema

`benchmark_factory` does not reuse the old intersection outputs. It expects one canonical bundle that you can swap out for any future dataset.

Required files under `--input-root`:

`samples.csv`

- Required columns: `drug_a_name`, `drug_b_name`, `cell_line`, `synergy_score`
- Optional columns: `sample_id`, `label`, `ri_row`, `ri_col`
- If `--label-source threshold` is used, labels are generated from `synergy_score >= --label-threshold`
- If `--label-source existing` is used, `label` must already exist

`drugs.csv`

- Required columns: `drug_name`, `smiles`
- Optional column: `synonyms`
- All remaining columns are treated as numeric MTLSynergy drug features

`cells_dualsyn.csv`

- Required column: `cell_line`
- All remaining columns are treated as numeric cell features for DualSyn and MFSynDCP

`cells_mtl.csv`

- Required column: `cell_line`
- All remaining columns are treated as numeric cell features for MTLSynergy

`cells_mvc_exp.csv`

- Required column: `cell_line`
- All remaining columns are treated as MVCASyn expression features

`cells_mvc_cn.csv`

- Required column: `cell_line`
- All remaining columns are treated as MVCASyn copy-number features

Validation rules:

- Every sample drug must exist in `drugs.csv`
- Every sample cell line must exist in all four cell feature files
- Drug and cell names must be unique in their own files
- All feature columns must be numeric

Minimal `samples.csv` example:

```csv
sample_id,drug_a_name,drug_b_name,cell_line,synergy_score,ri_row,ri_col
s1,5-FU,ABT-888,A375,18.7,42.1,37.9
s2,5-FU,AZD1775,HT29,7.4,40.5,31.2
```

Minimal `drugs.csv` example:

```csv
drug_name,smiles,synonyms,feat_1,feat_2
5-FU,O=c1[nH]cc(F)c(=O)[nH]1,5-Fluorouracil,0.12,0.88
ABT-888,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,Veliparib,0.45,0.67
```

Minimal cell feature example:

```csv
cell_line,f1,f2,f3
A375,1.2,0.3,4.1
HT29,0.8,2.7,1.5
```
