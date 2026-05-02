This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.repomixignore
DualSyn/creat_data_DC.py
DualSyn/data/cell_features_954_sample.csv
DualSyn/data/independent/independent_input_sample.csv
DualSyn/data/leave_cell/breast_sample.csv
DualSyn/data/leave_cell/colon_sample.csv
DualSyn/data/leave_cell/leave_breast_sample.csv
DualSyn/data/leave_cell/leave_colon_sample.csv
DualSyn/data/leave_cell/leave_lung_sample.csv
DualSyn/data/leave_cell/leave_melanoma_sample.csv
DualSyn/data/leave_cell/leave_ovarian_sample.csv
DualSyn/data/leave_cell/leave_prostate_sample.csv
DualSyn/data/leave_cell/lung_sample.csv
DualSyn/data/leave_cell/melanoma_sample.csv
DualSyn/data/leave_cell/ovarian_sample.csv
DualSyn/data/leave_cell/prostate_sample.csv
DualSyn/data/leave_comb/c00_sample.csv
DualSyn/data/leave_comb/c11_sample.csv
DualSyn/data/leave_comb/c22_sample.csv
DualSyn/data/leave_comb/c33_sample.csv
DualSyn/data/leave_comb/c44_sample.csv
DualSyn/data/leave_comb/leave_c00_sample.csv
DualSyn/data/leave_comb/leave_c11_sample.csv
DualSyn/data/leave_comb/leave_c22_sample.csv
DualSyn/data/leave_comb/leave_c33_sample.csv
DualSyn/data/leave_comb/leave_c44_sample.csv
DualSyn/data/leave_drug/d00_sample.csv
DualSyn/data/leave_drug/d11_sample.csv
DualSyn/data/leave_drug/d22_sample.csv
DualSyn/data/leave_drug/d33_sample.csv
DualSyn/data/leave_drug/d44_sample.csv
DualSyn/data/leave_drug/dd0and5_sample.csv
DualSyn/data/leave_drug/leave_d00_sample.csv
DualSyn/data/leave_drug/leave_d11_sample.csv
DualSyn/data/leave_drug/leave_d22_sample.csv
DualSyn/data/leave_drug/leave_d33_sample.csv
DualSyn/data/leave_drug/leave_d44_sample.csv
DualSyn/data/leave_drug/leave_dd0and5_sample.csv
DualSyn/data/new_labels_0_10_sample.csv
DualSyn/data/smiles_sample.csv
DualSyn/Inductive.sh
DualSyn/models/dualsyn_indepentent.py
DualSyn/models/dualsyn_leave_out.py
DualSyn/models/dualsyn.py
DualSyn/models/layer.py
DualSyn/train_independent.py
DualSyn/train_leave_out.py
DualSyn/train_transductive.py
DualSyn/utils_test.py
image/DualSyn.jpg
LICENSE
README.md
```

# Files

## File: .repomixignore
````
# 忽略所有原始的大 CSV 文件
*.csv

# 明确保留所有样本文件
!*_sample.csv

# 忽略不必要的文件
prepare_csv_samples.py
data/prepare_csv_samples.py
__pycache__/
.venv/
venv/
*.pyc
````

## File: DualSyn/data/cell_features_954_sample.csv
````
gene_id,ENSG00000116237,ENSG00000162413,ENSG00000171603
transcript_id,ENST00000343813.5,ENST00000377658.4,ENST00000361311.4
X22RV1_PROSTATE,57.81,6.73,26.89
X2313287_STOMACH,39.68,5.81,22.47
````

## File: DualSyn/data/independent/independent_input_sample.csv
````
drug1,drug2,cell,label
CNC(=O)CN1CCC(CC1)Oc2cc3c(cc2OC)ncnc3Nc4cccc(c4F)Cl,c1cc(ccc1[C@H](CCO)NC(=O)C2(CCN(CC2)c3c4cc[nH]c4ncn3)N)Cl,J82,1
CNC(=O)CN1CCC(CC1)Oc2cc3c(cc2OC)ncnc3Nc4cccc(c4F)Cl,c1cc(ccc1[C@H](CCO)NC(=O)C2(CCN(CC2)c3c4cc[nH]c4ncn3)N)Cl,SW780,0
````

## File: DualSyn/data/leave_cell/breast_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,T47D,1
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,ZR751,0
O=c1[nH]cc(F)c(=O)[nH]1,C=CCn1c(=O)c2cnc(Nc3ccc(N4CCN(C)CC4)cc3)nc2n1-c1cccc(C(C)(C)O)n1,KPL1,0
````

## File: DualSyn/data/leave_cell/colon_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT29,1
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,LOVO,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,RKO,0
````

## File: DualSyn/data/leave_cell/leave_breast_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_cell/leave_colon_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_cell/leave_lung_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_cell/leave_melanoma_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT29,1
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,LOVO,0
````

## File: DualSyn/data/leave_cell/leave_ovarian_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT29,1
````

## File: DualSyn/data/leave_cell/leave_prostate_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_cell/lung_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,MSTO,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,NCIH1650,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,NCIH23,0
````

## File: DualSyn/data/leave_cell/melanoma_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,RPMI7951,0
````

## File: DualSyn/data/leave_cell/ovarian_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,OV90,0
O=c1[nH]cc(F)c(=O)[nH]1,C=CCn1c(=O)c2cnc(Nc3ccc(N4CCN(C)CC4)cc3)nc2n1-c1cccc(C(C)(C)O)n1,A2780,1
````

## File: DualSyn/data/leave_cell/prostate_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,C=CCn1c(=O)c2cnc(Nc3ccc(N4CCN(C)CC4)cc3)nc2n1-c1cccc(C(C)(C)O)n1,VCAP,0
O=c1[nH]cc(F)c(=O)[nH]1,Cn1c(=O)n(-c2ccc(C(C)(C)C#N)cc2)c2c3cc(-c4cnc5ccccc5c4)ccc3ncc21,LNCAP,1
O=c1[nH]cc(F)c(=O)[nH]1,Cn1c(=O)n(-c2ccc(C(C)(C)C#N)cc2)c2c3cc(-c4cnc5ccccc5c4)ccc3ncc21,VCAP,1
````

## File: DualSyn/data/leave_comb/c00_sample.csv
````
drug1,drug2,cell,label
O=S1(=O)NC2(CN1CC(F)(F)F)C1CCC2Cc2cc(C=CCN3CCC(C(F)(F)F)CC3)ccc2C1,CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(C(=O)NC(CCC(=O)O)C(=O)O)cc1,NCIH460,0
N#Cc1ccc(Cn2cncc2CN2CCN(c3cccc(Cl)c3)C(=O)C2)cc1,O=C(NOCC(O)CO)c1ccc(F)c(F)c1Nc1ccc(I)cc1F,CAOV3,1
N#Cc1ccc(Cn2cncc2CN2CCN(c3cccc(Cl)c3)C(=O)C2)cc1,O=C(NOCC(O)CO)c1ccc(F)c(F)c1Nc1ccc(I)cc1F,NCIH460,1
````

## File: DualSyn/data/leave_comb/c11_sample.csv
````
drug1,drug2,cell,label
O=S1(=O)NC2(CN1CC(F)(F)F)C1CCC2Cc2cc(C=CCN3CCC(C(F)(F)F)CC3)ccc2C1,COC12C(COC(N)=O)C3=C(C(=O)C(C)=C(N)C3=O)N1CC1NC12,NCIH23,0
N#Cc1ccc(Cn2cncc2CN2CCN(c3cccc(Cl)c3)C(=O)C2)cc1,CCc1c2c(nc3ccc(O)cc13)-c1cc3c(c(=O)n1C2)COC(=O)C3(O)CC,A427,1
COc1cc(C2c3cc4c(cc3C(OC3OC5COC(C)OC5C(O)C3O)C3COC(=O)C23)OCO4)cc(OC)c1O,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A2780,1
````

## File: DualSyn/data/leave_comb/c22_sample.csv
````
drug1,drug2,cell,label
CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,COC1=C2CC(C)CC(OC)C(O)C(C)C=C(C)C(OC(N)=O)C(OC)C=CC=C(C)C(=O)NC(=CC1=O)C2=O,RKO,1
O=c1[nH]cc(F)c(=O)[nH]1,Cn1c(=O)n(-c2ccc(C(C)(C)C#N)cc2)c2c3cc(-c4cnc5ccccc5c4)ccc3ncc21,MDAMB436,1
O=C(NOCC(O)CO)c1ccc(F)c(F)c1Nc1ccc(I)cc1F,CCC1(O)C(=O)OCc2c1cc1n(c2=O)Cc2cc3c(CN(C)C)c(O)ccc3nc2-1,A2058,1
````

## File: DualSyn/data/leave_comb/c33_sample.csv
````
drug1,drug2,cell,label
CS(=O)(=O)CCNCc1ccc(-c2ccc3ncnc(Nc4ccc(OCc5cccc(F)c5)c(Cl)c4)c3c2)o1,COC1CC2CCC(C)C(O)(O2)C(=O)C(=O)N2CCCCC2C(=O)OC(C(C)CC2CCC(OP(C)(C)=O)C(OC)C2)CC(=O)C(C)C=C(C)C(O)C(OC)C(=O)C(C)CC(C)C=CC=CC=C1C,ES2,1
COc1cc(C2c3cc4c(cc3C(OC3OC5COC(C)OC5C(O)C3O)C3COC(=O)C23)OCO4)cc(OC)c1O,Cn1nnc2c(C(N)=O)ncn2c1=O,HT144,0
O=c1[nH]cc(F)c(=O)[nH]1,COC1CC2CCC(C)C(O)(O2)C(=O)C(=O)N2CCCCC2C(=O)OC(C(C)CC2CCC(OP(C)(C)=O)C(OC)C2)CC(=O)C(C)C=C(C)C(O)C(OC)C(=O)C(C)CC(C)C=CC=CC=C1C,SKMEL30,1
````

## File: DualSyn/data/leave_comb/c44_sample.csv
````
drug1,drug2,cell,label
CN(C)C(=N)N=C(N)N,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,UACC62,0
CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(C(=O)NC(CCC(=O)O)C(=O)O)cc1,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A2780,0
COc1cc(C2c3cc4c(cc3C(OC3OC5COC(C)OC5C(O)C3O)C3COC(=O)C23)OCO4)cc(OC)c1O,CC(C)CC(NC(=O)C(Cc1ccccc1)NC(=O)c1cnccn1)B(O)O,NCIH460,0
````

## File: DualSyn/data/leave_comb/leave_c00_sample.csv
````
drug1,drug2,cell,label
CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,COC1=C2CC(C)CC(OC)C(O)C(C)C=C(C)C(OC(N)=O)C(OC)C=CC=C(C)C(=O)NC(=CC1=O)C2=O,RKO,1
O=S1(=O)NC2(CN1CC(F)(F)F)C1CCC2Cc2cc(C=CCN3CCC(C(F)(F)F)CC3)ccc2C1,COC12C(COC(N)=O)C3=C(C(=O)C(C)=C(N)C3=O)N1CC1NC12,NCIH23,0
CN(C)C(=N)N=C(N)N,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,UACC62,0
````

## File: DualSyn/data/leave_comb/leave_c11_sample.csv
````
drug1,drug2,cell,label
CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,COC1=C2CC(C)CC(OC)C(O)C(C)C=C(C)C(OC(N)=O)C(OC)C=CC=C(C)C(=O)NC(=CC1=O)C2=O,RKO,1
CN(C)C(=N)N=C(N)N,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,UACC62,0
CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(C(=O)NC(CCC(=O)O)C(=O)O)cc1,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A2780,0
````

## File: DualSyn/data/leave_comb/leave_c22_sample.csv
````
drug1,drug2,cell,label
O=S1(=O)NC2(CN1CC(F)(F)F)C1CCC2Cc2cc(C=CCN3CCC(C(F)(F)F)CC3)ccc2C1,COC12C(COC(N)=O)C3=C(C(=O)C(C)=C(N)C3=O)N1CC1NC12,NCIH23,0
CN(C)C(=N)N=C(N)N,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,UACC62,0
CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(C(=O)NC(CCC(=O)O)C(=O)O)cc1,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A2780,0
````

## File: DualSyn/data/leave_comb/leave_c33_sample.csv
````
drug1,drug2,cell,label
CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,COC1=C2CC(C)CC(OC)C(O)C(C)C=C(C)C(OC(N)=O)C(OC)C=CC=C(C)C(=O)NC(=CC1=O)C2=O,RKO,1
O=S1(=O)NC2(CN1CC(F)(F)F)C1CCC2Cc2cc(C=CCN3CCC(C(F)(F)F)CC3)ccc2C1,COC12C(COC(N)=O)C3=C(C(=O)C(C)=C(N)C3=O)N1CC1NC12,NCIH23,0
CN(C)C(=N)N=C(N)N,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,UACC62,0
````

## File: DualSyn/data/leave_comb/leave_c44_sample.csv
````
drug1,drug2,cell,label
CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,COC1=C2CC(C)CC(OC)C(O)C(C)C=C(C)C(OC(N)=O)C(OC)C=CC=C(C)C(=O)NC(=CC1=O)C2=O,RKO,1
O=S1(=O)NC2(CN1CC(F)(F)F)C1CCC2Cc2cc(C=CCN3CCC(C(F)(F)F)CC3)ccc2C1,COC12C(COC(N)=O)C3=C(C(=O)C(C)=C(N)C3=O)N1CC1NC12,NCIH23,0
O=c1[nH]cc(F)c(=O)[nH]1,Cn1c(=O)n(-c2ccc(C(C)(C)C#N)cc2)c2c3cc(-c4cnc5ccccc5c4)ccc3ncc21,MDAMB436,1
````

## File: DualSyn/data/leave_drug/d00_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_drug/d11_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A2780,0
O=c1[nH]cc(F)c(=O)[nH]1,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A427,0
````

## File: DualSyn/data/leave_drug/d22_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,N#Cc1ccc(Cn2cncc2CN2CCN(c3cccc(Cl)c3)C(=O)C2)cc1,A427,1
O=c1[nH]cc(F)c(=O)[nH]1,N#Cc1ccc(Cn2cncc2CN2CCN(c3cccc(Cl)c3)C(=O)C2)cc1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,N#Cc1ccc(Cn2cncc2CN2CCN(c3cccc(Cl)c3)C(=O)C2)cc1,ES2,1
````

## File: DualSyn/data/leave_drug/d33_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,O=C(O)C1(Cc2cccc(Nc3nccs3)n2)CCC(Oc2cccc(Cl)c2F)CC1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,O=C(O)C1(Cc2cccc(Nc3nccs3)n2)CCC(Oc2cccc(Cl)c2F)CC1,HCT116,1
O=c1[nH]cc(F)c(=O)[nH]1,O=C(O)C1(Cc2cccc(Nc3nccs3)n2)CCC(Oc2cccc(Cl)c2F)CC1,HT29,1
````

## File: DualSyn/data/leave_drug/d44_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,Cn1cc(-c2cnn3c(N)c(Br)c(C4CCCNC4)nc23)cn1,A2058,1
O=c1[nH]cc(F)c(=O)[nH]1,Cn1cc(-c2cnn3c(N)c(Br)c(C4CCCNC4)nc23)cn1,A2058,1
O=c1[nH]cc(F)c(=O)[nH]1,Cn1cc(-c2cnn3c(N)c(Br)c(C4CCCNC4)nc23)cn1,A375,1
````

## File: DualSyn/data/leave_drug/dd0and5_sample.csv
````
drug1,drug2,cell,label
COC1CC2CCC(C)C(O)(O2)C(=O)C(=O)N2CCCCC2C(=O)OC(C(C)CC2CCC(OP(C)(C)=O)C(OC)C2)CC(=O)C(C)C=C(C)C(O)C(OC)C(=O)C(C)CC(C)C=CC=CC=C1C,CCc1c2c(nc3ccc(O)cc13)-c1cc3c(c(=O)n1C2)COC(=O)C3(O)CC,A2058,1
COC1CC2CCC(C)C(O)(O2)C(=O)C(=O)N2CCCCC2C(=O)OC(C(C)CC2CCC(OP(C)(C)=O)C(OC)C2)CC(=O)C(C)C=C(C)C(O)C(OC)C(=O)C(C)CC(C)C=CC=CC=C1C,CCc1c2c(nc3ccc(O)cc13)-c1cc3c(c(=O)n1C2)COC(=O)C3(O)CC,A2780,1
COC1CC2CCC(C)C(O)(O2)C(=O)C(=O)N2CCCCC2C(=O)OC(C(C)CC2CCC(OP(C)(C)=O)C(OC)C2)CC(=O)C(C)C=C(C)C(O)C(OC)C(=O)C(C)CC(C)C=CC=CC=C1C,CCc1c2c(nc3ccc(O)cc13)-c1cc3c(c(=O)n1C2)COC(=O)C3(O)CC,A375,1
````

## File: DualSyn/data/leave_drug/leave_d00_sample.csv
````
drug1,drug2,cell,label
CC1CC2C3CCC4=CC(=O)C=CC4(C)C3(F)C(O)CC2(C)C1(O)C(=O)CO,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A2058,0
CC1CC2C3CCC4=CC(=O)C=CC4(C)C3(F)C(O)CC2(C)C1(O)C(=O)CO,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,A2780,0
CC1CC2C3CCC4=CC(=O)C=CC4(C)C3(F)C(O)CC2(C)C1(O)C(=O)CO,CCc1cnn2c(NCc3ccc[n+]([O-])c3)cc(N3CCCCC3CCO)nc12,HCT116,0
````

## File: DualSyn/data/leave_drug/leave_d11_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_drug/leave_d22_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_drug/leave_d33_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_drug/leave_d44_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/leave_drug/leave_dd0and5_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/new_labels_0_10_sample.csv
````
drug1,drug2,cell,label
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,A375,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,CAOV3,0
O=c1[nH]cc(F)c(=O)[nH]1,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1,HT144,0
````

## File: DualSyn/data/smiles_sample.csv
````
name,smile
5-FU,O=c1[nH]cc(F)c(=O)[nH]1
ABT-888,CC1(c2nc3c(C(N)=O)cccc3[nH]2)CCCN1
AZD1775,C=CCn1c(=O)c2cnc(Nc3ccc(N4CCN(C)CC4)cc3)nc2n1-c1cccc(C(C)(C)O)n1
````

## File: DualSyn/creat_data_DC.py
````python
import csv
from itertools import islice

import pandas as pd
import numpy as np
import os
import json, pickle
from collections import OrderedDict
from rdkit import Chem
# from rdkit.Chem import MolFromSmiles
import networkx as nx
from utils_test import *
from torch_geometric.utils import degree, to_undirected



def get_cell_feature(cellId, cell_features):
    for row in islice(cell_features, 0, None):
        if row[0] == cellId:
            return row[1: ]

def atom_features(atom):
    return np.array(one_of_k_encoding_unk(atom.GetSymbol(),
                                          ['C', 'N', 'O', 'S', 'F', 'Si', 'P', 'Cl', 'Br', 'Mg', 'Na', 'Ca', 'Fe', 'As',
                                           'Al', 'I', 'B', 'V', 'K', 'Tl', 'Yb', 'Sb', 'Sn', 'Ag', 'Pd', 'Co', 'Se',
                                           'Ti', 'Zn', 'H', 'Li', 'Ge', 'Cu', 'Au', 'Ni', 'Cd', 'In', 'Mn', 'Zr', 'Cr',
                                           'Pt', 'Hg', 'Pb', 'Unknown']) +
                    one_of_k_encoding(atom.GetDegree(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding_unk(atom.GetTotalNumHs(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding_unk(atom.GetImplicitValence(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    [atom.GetIsAromatic()])

def one_of_k_encoding(x, allowable_set):
    if x not in allowable_set:
        raise Exception("input {0} not in allowable set{1}:".format(x, allowable_set))
    return list(map(lambda s: x == s, allowable_set))

def one_of_k_encoding_unk(x, allowable_set):
    """Maps inputs not in the allowable set to the last element."""
    if x not in allowable_set:
        x = allowable_set[-1]
    return list(map(lambda s: x == s, allowable_set)) 

def smile_to_graph(smile):
    mol = Chem.MolFromSmiles(smile)

   
    c_size = mol.GetNumAtoms() 
    features = []  
    for atom in mol.GetAtoms():
        feature = atom_features(atom)  
        features.append(feature / sum(feature))  

    
    edges = []  
    for bond in mol.GetBonds():  
        edges.append([bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()])  


    g = nx.Graph(edges).to_directed()  
    edge_index = []
    for e1, e2 in g.edges:
        edge_index.append([e1, e2])

    return c_size, features, edge_index  



def creat_data(datafile,drug_smiles_file, cellfile):

    
    file2 = cellfile
    cell_features = []
    with open(file2) as csvfile:
        csv_reader = csv.reader(csvfile)  
        for row in csv_reader:
            cell_features.append(row)
    cell_features = np.array(cell_features)  
    #print('cell_features', cell_features)


    compound_iso_smiles = []
    df = pd.read_csv(drug_smiles_file)  
    compound_iso_smiles += list(df['smile'])
    compound_iso_smiles = set(compound_iso_smiles)  
    smile_graph = {}
    #print('compound_iso_smiles', compound_iso_smiles)
    for smile in compound_iso_smiles:
        #print('smiles', smile)
        if smile not in smile_graph: 
            smile_graph[smile] = {}
        g = smile_to_graph(smile)  
        smile_graph[smile] = g 


    
    df = pd.read_csv(datafile)
    #df = pd.read_csv('data/independent_set/independent_input.csv')
    drug1, drug2, cell, label = list(df['drug1']), list(df['drug2']), list(df['cell']), list(df['label'])
    drug1, drug2, cell, label = np.asarray(drug1), np.asarray(drug2), np.asarray(cell), np.asarray(label)
    # make data PyTorch Geometric ready

    return drug1, drug2, cell, label, smile_graph, cell_features



if __name__ == "__main__":

    cellfile = 'data/independent_set/independent_cell_features_954.csv'  
    drug_smiles_file = 'data/smiles.csv'                  
    datafile = 'data/random_train_new_labels_0_10.csv'    

    creat_data(datafile, drug_smiles_file, cellfile)
````

## File: DualSyn/Inductive.sh
````bash
/home/.conda/envs/DualSyn/bin/python /home/DualSyn/train_leave_out.py --leave_type leave_drug --dropping_method DropNode --dropout_rate 0.1 --device_num 1
/home/.conda/envs/DualSyn/bin/python /home/DualSyn/train_leave_out.py --leave_type leave_comb --dropping_method DropNode --dropout_rate 0.1 --device_num 1
/home/.conda/envs/DualSyn/bin/python /home/DualSyn/train_leave_out.py --leave_type leave_cell --dropping_method DropNode --dropout_rate 0.1 --device_num 1

/home/.conda/envs/DualSyn/bin/python /home/DualSyn/train_independent.py --dropping_method DropNode --dropout_rate 0.2 --device_num 1 --lr 0.000005
````

## File: DualSyn/models/dualsyn_indepentent.py
````python
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import global_max_pool as gmp
import pandas as pd
import numpy as np
import argparse
from torch.nn import Parameter
from torch import Tensor
from torch_geometric.typing import Adj
from torch_sparse import SparseTensor
from models.layer import GNNLayer


parser = argparse.ArgumentParser(description='Process some floats.')

parser.add_argument('--dropping_method', type=str, help='The type of drop')
parser.add_argument('--dropout_rate', type=float, help='The dropout rate')
parser.add_argument('--device_num', type=int, help='The number of device')
parser.add_argument('--lr', type=float, help='The learning rate')

args = parser.parse_args()
            
dropping_method = args.dropping_method
dropout_rate = args.dropout_rate
device_num = args.device_num


class DNN(nn.Module):
    
    def __init__(self, layers, dropout=0.2):

        super(DNN, self).__init__()

        self.dnn_network = nn.ModuleList([
            nn.Linear(layer[0], layer[1]) for layer in list(zip(layers[:-1], layers[1:]))
            ]+ [
            nn.BatchNorm1d(layer[1]) for layer in list(zip(layers[:-1], layers[1:]))
        ])
        self.dropout = nn.Dropout(p=dropout)

        self.activate = nn.LeakyReLU()
    
    def forward(self, x):

        step = int(len(self.dnn_network)/2)
        for i in range(step):
            linear = self.dnn_network[i]
            batchnorm = self.dnn_network[i + step]
            
            x = self.dropout(x)
            x = linear(x)
            x = batchnorm(x)
            x = self.activate(x)
       
        x = self.dropout(x)
        
        return x

class ProductLayer(nn.Module):
    
    def __init__(self, mode, embed_dim, field_num, hidden_units):
        
        super(ProductLayer, self).__init__()
        self.mode = mode
        self.w_z = nn.Parameter(torch.rand([field_num, embed_dim, hidden_units[0]]))   
        
        if mode == 'in':
            self.w_p = nn.Parameter(torch.rand([field_num, field_num, hidden_units[0]]))  
        else:
            self.w_p = nn.Parameter(torch.rand([embed_dim, embed_dim, hidden_units[0]]))

        self.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(384, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU()  
        )

    
    def forward(self, z, sparse_embeds):  
        device = torch.device('cuda:'+str(device_num))
        l_z = z.view(z.size()[0], -1)
        l_z = F.normalize(l_z, 2, 1)
        l_z = self.fc(l_z)
        
        if self.mode == 'in':  
            p = torch.matmul(sparse_embeds, sparse_embeds.permute((0, 2, 1))) 
        else:  
            f_sum = torch.unsqueeze(torch.sum(sparse_embeds, dim=1), dim=1)  
            p = torch.matmul(f_sum.permute((0, 2,1)), f_sum)     
        
        l_p = torch.mm(p.reshape(p.shape[0], -1), self.w_p.permute((2, 0, 1)).reshape(self.w_p.shape[2], -1).T) 

        output = l_p.to(device) + l_z.to(device)

        return output


class DualSyn(torch.nn.Module):
    def __init__(self, n_output = 1, n_filters=32, embed_dim=128, num_features_xd=64, num_features_xt=954, output_dim=128, dropout=0.1):

        super(DualSyn, self).__init__()

        self.activate = nn.LeakyReLU()
        self.dropout = nn.Dropout(dropout)

        # SMILES1 graph branch
        self.n_output = n_output 
        #self.drug_conv1 = TransformerConv(78, num_features_xd * 2,  heads = 2)
        self.drug_conv1 = GNNLayer(78, num_features_xd * 2,  heads = 2, dropping_method = dropping_method)
        self.drug_ln1 = nn.LayerNorm(num_features_xd * 4)
        #self.drug_conv2 = TransformerConv(num_features_xd * 4, num_features_xd * 8, heads = 2)
        self.drug_conv2 = GNNLayer(num_features_xd * 4, num_features_xd * 8, heads = 2, dropping_method = dropping_method)
        self.drug_ln2 = nn.LayerNorm(num_features_xd * 16)
        
        self.drug_fc_g1 = torch.nn.Linear(num_features_xd * 16, num_features_xd * 8)
        self.drug_ln3 = nn.LayerNorm(num_features_xd * 8)
        self.drug_fc_g2 = torch.nn.Linear(num_features_xd * 8, output_dim )
        self.drug_ln4 = nn.LayerNorm(output_dim)


        # DL cell featrues
        self.reduction = nn.Sequential(
            nn.Linear(num_features_xt, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Linear(256, output_dim)
        )
    
        mode = 'in'
        field_num = 3   
        hidden_units = [256, 64]
        dnn_dropout = 0.2

        self.product = ProductLayer(mode, embed_dim, field_num, hidden_units)
        
        self.dnn_network = DNN(hidden_units, dnn_dropout)
        self.dense_final = nn.Linear(hidden_units[-1], 1)


    def forward(self, data1, data2):
        x1, edge_index1, batch1, cell = data1.x, data1.edge_index, data1.batch, data1.cell
        x2, edge_index2, batch2 = data2.x, data2.edge_index, data2.batch

        # deal drug1
        x1 = self.drug_conv1(x1, edge_index1, dropout_rate)
        x1 = self.activate(x1)

        x1 = self.drug_conv2(x1, edge_index1, dropout_rate)
        x1 = self.activate(x1)
                
        x1 = gmp(x1, batch1)       # global max pooling

        # flatten
        x1 = self.drug_fc_g1(x1)
        x1 = self.activate(x1)
        x1 = self.dropout(x1)

        x1 = self.drug_fc_g2(x1)
        x1 = self.dropout(x1)


        # deal drug2
        x2 = self.drug_conv1(x2, edge_index2, dropout_rate)
        x2 = self.activate(x2)

        x2 = self.drug_conv2(x2, edge_index2, dropout_rate)
        x2 = self.activate(x2)

        x2= gmp(x2, batch2)  # global max pooling


        # flatten
        x2 = self.drug_fc_g1(x2)
        x2 = self.activate(x2)
        x2 = self.dropout(x2)
        
        x2 = self.drug_fc_g2(x2)
        x2 = self.dropout(x2)

        # deal cell
        cell_vector = F.normalize(cell, 2, 1)
        cell_vector = self.reduction(cell_vector)

        sparse_embeds = torch.stack([x1, x2, cell_vector], dim=1) 
        z = sparse_embeds

        # product layer
        sparse_inputs = self.product(z, sparse_embeds)
        
        # dnn_network
        dnn_x = self.dnn_network(sparse_inputs)
        final = self.dense_final(dnn_x)

        outputs = torch.sigmoid(final.squeeze(1))
        
        return outputs
````

## File: DualSyn/models/dualsyn_leave_out.py
````python
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import global_max_pool as gmp
import pandas as pd
import numpy as np
import argparse
from torch.nn import Parameter
from torch import Tensor
from torch_geometric.typing import Adj
from torch_sparse import SparseTensor
from models.layer import GNNLayer


parser = argparse.ArgumentParser(description='Process some floats.')
parser.add_argument('--leave_type', type=str, help='The type of leaveout')
parser.add_argument('--dropping_method', type=str, help='The type of drop')
parser.add_argument('--dropout_rate', type=float, help='The dropout rate')
parser.add_argument('--device_num', type=int, help='The number of device')

args = parser.parse_args()
            
dropping_method = args.dropping_method
dropout_rate = args.dropout_rate
device_num = args.device_num


class DNN(nn.Module):
    
    def __init__(self, layers, dropout=0.2):
        super(DNN, self).__init__()

        self.dnn_network = nn.ModuleList([
            nn.Linear(layer[0], layer[1]) for layer in list(zip(layers[:-1], layers[1:]))
            ]+ [
            nn.BatchNorm1d(layer[1]) for layer in list(zip(layers[:-1], layers[1:]))
        ])
        self.dropout = nn.Dropout(p=dropout)

        self.activate = nn.LeakyReLU()

    def forward(self, x):

        step = int(len(self.dnn_network)/2)
        for i in range(step):
            linear = self.dnn_network[i]
            batchnorm = self.dnn_network[i + step]
            
            x = self.dropout(x)
            x = linear(x)
            x = batchnorm(x)
            x = self.activate(x)
       
        x = self.dropout(x)
        
        return x

class ProductLayer(nn.Module):
    
    def __init__(self, mode, embed_dim, field_num, hidden_units):
        
        super(ProductLayer, self).__init__()
        self.mode = mode
        self.w_z = nn.Parameter(torch.rand([field_num, embed_dim, hidden_units[0]])) 

        if mode == 'in':
            self.w_p = nn.Parameter(torch.rand([field_num, field_num, hidden_units[0]]))
        else:
            self.w_p = nn.Parameter(torch.rand([embed_dim, embed_dim, hidden_units[0]]))

        self.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(384, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU()  
        )

    
    def forward(self, z, sparse_embeds):  
        device = torch.device('cuda:'+str(device_num))
        l_z = z.view(z.size()[0], -1)
        l_z = F.normalize(l_z, 2, 1)
        l_z = self.fc(l_z)
        
        if self.mode == 'in':  
            p = torch.matmul(sparse_embeds, sparse_embeds.permute((0, 2, 1)))
        else:  
            f_sum = torch.unsqueeze(torch.sum(sparse_embeds, dim=1), dim=1)  
            p = torch.matmul(f_sum.permute((0, 2,1)), f_sum)     
        
        l_p = torch.mm(p.reshape(p.shape[0], -1), self.w_p.permute((2, 0, 1)).reshape(self.w_p.shape[2], -1).T) 

        output = l_p.to(device) + l_z.to(device)

        return output


class DualSyn(torch.nn.Module):
    def __init__(self, n_output = 1, n_filters=32, embed_dim=128, num_features_xd=64, num_features_xt=954, output_dim=128, dropout=0.1):

        super(DualSyn, self).__init__()

        self.activate = nn.LeakyReLU()
        self.dropout = nn.Dropout(dropout)

        # SMILES1 graph branch
        self.n_output = n_output 
        #self.drug_conv1 = TransformerConv(78, num_features_xd * 2,  heads = 2)
        self.drug_conv1 = GNNLayer(78, num_features_xd * 2,  heads = 2, dropping_method = dropping_method)
        self.drug_ln1 = nn.LayerNorm(num_features_xd * 4)
        #self.drug_conv2 = TransformerConv(num_features_xd * 4, num_features_xd * 8, heads = 2)
        self.drug_conv2 = GNNLayer(num_features_xd * 4, num_features_xd * 8, heads = 2, dropping_method = dropping_method)
        self.drug_ln2 = nn.LayerNorm(num_features_xd * 16)
        
        self.drug_fc_g1 = torch.nn.Linear(num_features_xd * 16, num_features_xd * 8)
        self.drug_ln3 = nn.LayerNorm(num_features_xd * 8)
        self.drug_fc_g2 = torch.nn.Linear(num_features_xd * 8, output_dim )
        self.drug_ln4 = nn.LayerNorm(output_dim)


        # DL cell featrues
        self.reduction = nn.Sequential(
            nn.Linear(num_features_xt, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Linear(256, output_dim)
        )
       
        mode = 'in'
        field_num = 3  
        hidden_units = [256, 64]
        dnn_dropout = 0.2

        self.product = ProductLayer(mode, embed_dim, field_num, hidden_units)
        
        self.dnn_network = DNN(hidden_units, dnn_dropout)
        self.dense_final = nn.Linear(hidden_units[-1], 1)


    def forward(self, data1, data2):
        x1, edge_index1, batch1, cell = data1.x, data1.edge_index, data1.batch, data1.cell
        x2, edge_index2, batch2 = data2.x, data2.edge_index, data2.batch

        # deal drug1
        x1 = self.drug_conv1(x1, edge_index1, dropout_rate)
        x1 = self.activate(x1)

        x1 = self.drug_conv2(x1, edge_index1, dropout_rate)
        x1 = self.activate(x1)
                
        x1 = gmp(x1, batch1)       # global max pooling

        # flatten
        x1 = self.drug_fc_g1(x1)
        x1 = self.activate(x1)
        x1 = self.dropout(x1)

        x1 = self.drug_fc_g2(x1)
        x1 = self.dropout(x1)


        # deal drug2
        x2 = self.drug_conv1(x2, edge_index2, dropout_rate)
        x2 = self.activate(x2)

        x2 = self.drug_conv2(x2, edge_index2, dropout_rate)
        x2 = self.activate(x2)

        x2= gmp(x2, batch2)  # global max pooling


        # flatten
        x2 = self.drug_fc_g1(x2)
        x2 = self.activate(x2)
        x2 = self.dropout(x2)
        
        x2 = self.drug_fc_g2(x2)
        x2 = self.dropout(x2)

        # deal cell
        cell_vector = F.normalize(cell, 2, 1)
        cell_vector = self.reduction(cell_vector)
        sparse_embeds = torch.stack([x1, x2, cell_vector], dim=1)   
        z = sparse_embeds

        # product layer
        sparse_inputs = self.product(z, sparse_embeds)
        
        
        # dnn_network
        dnn_x = self.dnn_network(sparse_inputs)
        final = self.dense_final(dnn_x)

        outputs = torch.sigmoid(final.squeeze(1))
        
        return outputs
````

## File: DualSyn/models/dualsyn.py
````python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import TransformerConv
from torch_geometric.nn import global_max_pool as gmp
from torch_geometric.nn import SAGPooling
import pandas as pd
import numpy as np

# 定义一个全连接层的神经网络
class DNN(nn.Module):
    
    def __init__(self, layers, dropout=0.2):
       
        super(DNN, self).__init__()
        
        
        self.dnn_network = nn.ModuleList([
            nn.Linear(layer[0], layer[1]) for layer in list(zip(layers[:-1], layers[1:]))
            ]+ [
            nn.BatchNorm1d(layer[1]) for layer in list(zip(layers[:-1], layers[1:]))
        ])
        self.dropout = nn.Dropout(p=dropout)

        self.activate = nn.LeakyReLU()
    

    def forward(self, x):

        step = int(len(self.dnn_network)/2)
        for i in range(step):
            linear = self.dnn_network[i]
            batchnorm = self.dnn_network[i + step]
            
            x = self.dropout(x)
            x = linear(x)
            x = batchnorm(x)
            x = self.activate(x)
       
        x = self.dropout(x)
        
        return x

class ProductLayer(nn.Module):
    
    def __init__(self, mode, embed_dim, field_num, hidden_units):
        
        super(ProductLayer, self).__init__()
        self.mode = mode
        self.w_z = nn.Parameter(torch.rand([field_num, embed_dim, hidden_units[0]]))   
        

        if mode == 'in':
            self.w_p = nn.Parameter(torch.rand([field_num, field_num, hidden_units[0]])) 
        else:
            self.w_p = nn.Parameter(torch.rand([embed_dim, embed_dim, hidden_units[0]]))
        
        #self.l_b = torch.rand([hidden_units[0], ], requires_grad=True)

        self.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(384, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU()  
        )

    
    def forward(self, z, sparse_embeds):  
        device = torch.device('cuda:0')
        l_z = z.view(z.size()[0], -1)
        l_z = F.normalize(l_z, 2, 1)
        l_z = self.fc(l_z)
        
        # lp 部分
        if self.mode == 'in':  
            p = torch.matmul(sparse_embeds, sparse_embeds.permute((0, 2, 1)))  
            
        else:  
            f_sum = torch.unsqueeze(torch.sum(sparse_embeds, dim=1), dim=1)  
            p = torch.matmul(f_sum.permute((0, 2,1)), f_sum)     
        
        l_p = torch.mm(p.reshape(p.shape[0], -1), self.w_p.permute((2, 0, 1)).reshape(self.w_p.shape[2], -1).T)  

        output = l_p.to(device) + l_z.to(device)

        return output


class DualSyn(torch.nn.Module):
    def __init__(self, n_output = 1, n_filters=32, embed_dim=128, num_features_xd=64, num_features_xt=954, output_dim=128, dropout=0.1):

        super(DualSyn, self).__init__()

        self.activate = nn.LeakyReLU()
        self.dropout = nn.Dropout(dropout)

        # SMILES1 graph branch
        self.n_output = n_output 
        self.drug_conv1 = TransformerConv(78, num_features_xd * 2,  heads = 2)
        self.drug_conv2 = TransformerConv(num_features_xd * 4, num_features_xd * 8, heads = 2)
        
        self.drug_fc_g1 = torch.nn.Linear(num_features_xd * 16, num_features_xd * 8)
        self.drug_fc_g2 = torch.nn.Linear(num_features_xd * 8, output_dim )


        # DL cell featrues
        self.reduction = nn.Sequential(
            nn.Linear(num_features_xt, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Linear(256, output_dim)
        )

       
        mode = 'in'
        field_num = 3   
        hidden_units = [256, 64]
        dnn_dropout = 0.2


        self.product = ProductLayer(mode, embed_dim, field_num, hidden_units)
        

        self.dnn_network = DNN(hidden_units, dnn_dropout)
        self.dense_final = nn.Linear(hidden_units[-1], 1)


    def forward(self, data1, data2):
        x1, edge_index1, batch1, cell = data1.x, data1.edge_index, data1.batch, data1.cell
        x2, edge_index2, batch2 = data2.x, data2.edge_index, data2.batch

        # deal drug1
        x1 = self.drug_conv1(x1, edge_index1)
        x1 = self.activate(x1)

        x1 = self.drug_conv2(x1, edge_index1)
        x1 = self.activate(x1)

        x1 = gmp(x1, batch1)       # global max pooling    


        # flatten
        x1 = self.drug_fc_g1(x1)
        x1 = self.activate(x1)
        x1 = self.dropout(x1)

        x1 = self.drug_fc_g2(x1)
        x1 = self.dropout(x1)


        # deal drug2
        x2 = self.drug_conv1(x2, edge_index2)
        x2 = self.activate(x2)

        x2 = self.drug_conv2(x2, edge_index2)
        x2 = self.activate(x2)
      
        x2 = gmp(x2, batch2)       # global max pooling    


        # flatten
        x2 = self.drug_fc_g1(x2)
        x2 = self.activate(x2)
        x2 = self.dropout(x2)
        
        x2 = self.drug_fc_g2(x2)
        x2 = self.dropout(x2)

        # deal cell
        cell_vector = F.normalize(cell, 2, 1)
        cell_vector = self.reduction(cell_vector)


        sparse_embeds = torch.stack([x1, x2, cell_vector], dim=1)
        z = sparse_embeds


        sparse_inputs = self.product(z, sparse_embeds)
        
        
        dnn_x = self.dnn_network(sparse_inputs)
        final = self.dense_final(dnn_x)

        outputs = torch.sigmoid(final.squeeze(1))
        
        return outputs
````

## File: DualSyn/models/layer.py
````python
import os
import sys
import torch
from torch.nn import Parameter
from torch import Tensor
from torch_geometric.typing import Adj
import torch.nn.functional as F
from torch_sparse import SparseTensor
from typing import Union, Tuple, Optional
from torch_geometric.nn import TransformerConv, GCNConv

class DropBlock:
    def __init__(self, dropping_method: str):
        super(DropBlock, self).__init__()
        self.dropping_method = dropping_method

    def drop(self, x: Tensor, edge_index: Adj, drop_rate: float = 0):
        if self.dropping_method == 'DropNode':  
            x = x * torch.bernoulli(torch.ones(x.size(0), 1) - drop_rate).to(x.device)
            x = x / (1 - drop_rate)  
        elif self.dropping_method == 'DropEdge':
            edge_reserved_size = int(edge_index.size(1) * (1 - drop_rate))
            if isinstance(edge_index, SparseTensor):
                row, col, _ = edge_index.coo()
                edge_index = torch.stack((row, col))
            perm = torch.randperm(edge_index.size(1))
            edge_index = edge_index.t()[perm][:edge_reserved_size].t()
        elif self.dropping_method == 'Dropout': 
            x = F.dropout(x, drop_rate)

        return x, edge_index


class GNNLayer(torch.nn.Module):
    def __init__(self,
        #in_channels: Union[int, Tuple[int, int]],
        in_channels: int, 
        out_channels: int,
        dropping_method: str,
        heads: int ,
        #transform_first: bool = False,
        ):

        super(GNNLayer, self).__init__()
        
        self.dropping_method = dropping_method
        self.drop_block = DropBlock(dropping_method)
        #self.transform_first = transform_first

        self.backbone = TransformerConv(in_channels, out_channels, heads )
        # self.backbone = GCNConv(in_channels, out_channels)
       

    def forward(self, x: Tensor, edge_index: Adj, drop_rate: float = 0):
        message_drop = 0
        if self.dropping_method == 'DropMessage':
            message_drop = drop_rate

        x, edge_index = self.drop_block.drop(x, edge_index, drop_rate)

        # if self.transform_first:
        #     x = x.matmul(self.weight)

        out = self.backbone(x, edge_index)

        # if not self.transform_first:
        #     out = out.matmul(self.weight)
        # if self.bias is not None:
        #     out += self.bias

        return out
````

## File: DualSyn/train_independent.py
````python
import random
import torch.nn.functional as F
import torch.nn as nn
from models.dualsyn_indepentent import DualSyn
from utils_test import *
from sklearn.metrics import roc_curve, confusion_matrix
from sklearn.metrics import cohen_kappa_score, accuracy_score, roc_auc_score, precision_score, recall_score, balanced_accuracy_score
from sklearn import metrics
from creat_data_DC import creat_data
import pandas as pd
import datetime
import argparse

parser = argparse.ArgumentParser(description='Process some floats.')

parser.add_argument('--dropping_method', type=str, help='The type of drop')
parser.add_argument('--dropout_rate', type=float, help='The dropout rate')
parser.add_argument('--device_num', type=int, help='The number of device')
parser.add_argument('--lr', type=float, help='The learning rate')

args = parser.parse_args()
            

dropping_method = args.dropping_method
dropout_rate = args.dropout_rate
device_num = args.device_num
lr = args.lr

# print(f'dropout_method:{dropping_method}, dropout_rate: {dropout_rate}, device_num: {device_num}')

result_name = 'DualSyn_independent_'+str(dropping_method)+"_drop_rate="+str(dropout_rate)+"_lr="+str(lr)

modeling = DualSyn

log_dir = "runs/"+result_name


# training function at each epoch
def train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch):
    print("===============")
    print('Training on {} samples...'.format(len(drug1_loader_train.dataset)))
    model.train()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()
    # train_loader = np.array(train_loader)

    for batch_idx, data in enumerate(zip(drug1_loader_train, drug2_loader_train)): 
        data1 = data[0]
        data2 = data[1]
        data1 = data1.to(device)
        data2 = data2.to(device)
        #y = data[0].y.view(-1, 1).long().to(device)
        y = data[0].y.view(-1, 1).float().to(device)
        y = y.squeeze(1)
        optimizer.zero_grad()
        output = model(data1, data2)

        #loss = loss_fn(output, y)
        loss = loss_fn(output, y) 
        # print('loss', loss)
        loss.backward()
        optimizer.step()
        if batch_idx % LOG_INTERVAL == 0:
            print('Train epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch,
                                                                           batch_idx * len(data1.x),
                                                                           len(drug1_loader_train.dataset),
                                                                           100. * batch_idx / len(drug1_loader_train),
                                                                           loss.item()))
        ys = output.to('cpu').data.numpy()
        #predicted_labels = list(map(lambda x: np.argmax(x), ys))
        predicted_labels = list(map(lambda x: int(x>0.5), ys))
        #predicted_scores = list(map(lambda x: x[1], ys))
        predicted_scores = list(map(lambda x: x, ys))
        total_preds = torch.cat((total_preds, torch.Tensor(predicted_scores)), 0)
        total_prelabels = torch.cat((total_prelabels, torch.Tensor(predicted_labels)), 0)
        total_labels = torch.cat((total_labels, data1.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(), total_preds.numpy().flatten(), total_prelabels.numpy().flatten()

def predicting(model, device, drug1_loader_test, drug2_loader_test):
    model.eval()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()
    print('Make prediction for {} samples...'.format(len(drug1_loader_test.dataset)))
    with torch.no_grad():
        for data in zip(drug1_loader_test, drug2_loader_test):
            data1 = data[0]
            data2 = data[1]
            data1 = data1.to(device)
            data2 = data2.to(device)
            output = model(data1, data2)
            #ys = F.softmax(output, 1).to('cpu').data.numpy()
            ys = output.to('cpu').data.numpy()
            #predicted_labels = list(map(lambda x: np.argmax(x), ys))
            predicted_labels = list(map(lambda x: int(x>0.5), ys))
            #predicted_scores = list(map(lambda x: x[1], ys))
            predicted_scores = list(map(lambda x: x, ys))
            total_preds = torch.cat((total_preds, torch.Tensor(predicted_scores)), 0)
            total_prelabels = torch.cat((total_prelabels, torch.Tensor(predicted_labels)), 0)
            total_labels = torch.cat((total_labels, data1.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(), total_preds.numpy().flatten(), total_prelabels.numpy().flatten()


def shuffle_dataset(dataset, seed):
    np.random.seed(seed)
    np.random.shuffle(dataset)
    return dataset


def split_dataset(dataset, ratio):
    n = int(len(dataset) * ratio)
    dataset_1, dataset_2 = dataset[:n], dataset[n:]
    return dataset_1, dataset_2


# CPU or GPU

if torch.cuda.is_available():
    device = torch.device('cuda:'+str(device_num))
    print('The code uses GPU...')
else:
    device = torch.device('cpu')
    print('The code uses CPU!!!')


TRAIN_BATCH_SIZE = 1024
TEST_BATCH_SIZE = 1024
LR = lr
LOG_INTERVAL = 20
NUM_EPOCHS = 300

print('Learning rate: ', LR)
print('Epochs: ', NUM_EPOCHS)


cellfile = 'data/cell_features_954.csv'  
drug_smiles_file = 'data/smiles.csv'                 
train_datafile = 'data/new_labels_0_10.csv'   
train_dataset = 'new_labels_0_10'
independent_datafile = 'data/independent/independent_input.csv'
datafile = 'independent_input'    


for i in range(5):
    train_drug1, train_drug2, train_cell, train_label, smile_graph, cell_features = creat_data(train_datafile, drug_smiles_file, cellfile)
    train_drug1_data = TestbedDataset(dataset=train_dataset + '_drug1', xd=train_drug1, xt=train_cell, y=train_label, smile_graph=smile_graph, xt_featrue=cell_features)
    train_drug2_data = TestbedDataset(dataset=train_dataset + '_drug2', xd=train_drug2, xt=train_cell, y=train_label, smile_graph=smile_graph, xt_featrue=cell_features)
    #print('src_new_labels_0_10[0]', train_drug1_data[0])
    lenth = len(train_drug1_data)
    random_num = random.sample(range(0, lenth), lenth)
    drug1_data = train_drug1_data[random_num]
    drug2_data = train_drug2_data[random_num]


    independent_drug1, independent_drug2, independent_cell, independent_label, smile_graph, cell_features = creat_data(
        independent_datafile, drug_smiles_file, cellfile)
    independent_drug1_data = TestbedDataset(dataset='independent_input_drug1', xd=independent_drug1, xt=independent_cell, y=independent_label, smile_graph=smile_graph, xt_featrue=cell_features)
    independent_drug2_data = TestbedDataset(dataset='independent_input_drug2', xd=independent_drug2, xt=independent_cell, y=independent_label, smile_graph=smile_graph, xt_featrue=cell_features)
    lenth = len(independent_drug1_data)

    drug1_loader_train = DataLoader(drug1_data, batch_size=TRAIN_BATCH_SIZE, shuffle=None)
    drug2_loader_train = DataLoader(drug2_data, batch_size=TRAIN_BATCH_SIZE, shuffle=None)

    independent_drug1_loader_test = DataLoader(independent_drug1_data, batch_size=TEST_BATCH_SIZE, shuffle=None)
    independent_drug2_loader_test = DataLoader(independent_drug2_data, batch_size=TEST_BATCH_SIZE, shuffle=None)

    model = modeling().to(device)
    #loss_fn = nn.CrossEntropyLoss()
    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    folder_path = './result/' + result_name
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_AUCs = folder_path + '/'+ result_name + '_' + str(i) + '--AUCs--' + datafile + '_' + time_str + '.txt'
    AUCs = ('Epoch\tAUC_dev\tPR_AUC\tACC\tBACC\tPREC\tTPR\tKAPPA\tRECALL')
    with open(file_AUCs, 'w') as f:
        f.write(AUCs + '\n')


    best_auc = 0
    for epoch in range(NUM_EPOCHS):
        train_T, train_S, train_Y = train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch + 1)
        T, S, Y = predicting(model, device, independent_drug1_loader_test, independent_drug2_loader_test)
        # T is correct label
        # S is predict score
        # Y is predict label

        # compute preformence
        AUC = roc_auc_score(T, S)
        precision, recall, threshold = metrics.precision_recall_curve(T, S)
        PR_AUC = metrics.auc(recall, precision)
        BACC = balanced_accuracy_score(T, Y)
        tn, fp, fn, tp = confusion_matrix(T, Y).ravel()
        TPR = tp / (tp + fn)
        PREC = precision_score(T, Y)
        ACC = accuracy_score(T, Y)
        KAPPA = cohen_kappa_score(T, Y)
        recall = recall_score(T, Y)

        train_AUC = roc_auc_score(train_T, train_S)
        train_precision, train_recall, train_threshold = metrics.precision_recall_curve(T, S)
        train_PR_AUC = metrics.auc(train_recall, train_precision)
        train_ACC = accuracy_score(train_T, train_Y)
        
        print("Train: AUC={}, PR_AUC={}, ACC={}".format(train_AUC, train_PR_AUC, train_ACC))
        print("Test: AUC={}, PR_AUC={}, ACC={}".format(AUC, PR_AUC, ACC))

        # save data

        if best_auc < AUC:
            best_auc = AUC
            # torch.save(model.state_dict(), model_file_name)
            # independent_num = []
            # independent_num.append(test_num)
            # independent_num.append(T)
            # independent_num.append(Y)
            # independent_num.append(S)
            # txtDF = pd.DataFrame(data=independent_num)
            # txtDF.to_csv(result_file_name, index=False, header=False)
            AUCs = [epoch, AUC, PR_AUC, ACC, BACC, PREC, TPR, KAPPA]
            save_AUCs(AUCs, file_AUCs)
        print('best_auc', best_auc)
        print("\n")
    save_AUCs("best_auc:"+str(best_auc), file_AUCs)
````

## File: DualSyn/train_leave_out.py
````python
import random
import torch.nn.functional as F
import torch.nn as nn
from models.dualsyn_leave_out import DualSyn
from utils_test import *
from sklearn.metrics import roc_curve, confusion_matrix
from sklearn.metrics import cohen_kappa_score, accuracy_score, roc_auc_score, precision_score, recall_score, balanced_accuracy_score
from sklearn import metrics
from creat_data_DC import creat_data
import pandas as pd
import datetime
import argparse

parser = argparse.ArgumentParser(description='Process some floats.')

parser.add_argument('--leave_type', type=str, help='The type of leaveout')
parser.add_argument('--dropping_method', type=str, help='The type of drop')
parser.add_argument('--dropout_rate', type=float, help='The dropout rate')
parser.add_argument('--device_num', type=int, help='The number of device')


args = parser.parse_args()
            

leave_type = args.leave_type
dropping_method = args.dropping_method
dropout_rate = args.dropout_rate
device_num = args.device_num


# print(f'leave_type:{leave_type}, dropout_method:{dropping_method}, dropout_rate: {dropout_rate}, device_num: {device_num}')


result_name = 'DualSyn_'+str(leave_type)+'_'+str(dropping_method)+"_drop_rate="+str(dropout_rate)

modeling = DualSyn


# training function at each epoch
def train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch):
    print('Training on {} samples...'.format(len(drug1_loader_train.dataset)))
    model.train()
    # train_loader = np.array(train_loader)

    for batch_idx, data in enumerate(zip(drug1_loader_train, drug2_loader_train)): 
        data1 = data[0]
        data2 = data[1]
        data1 = data1.to(device)
        data2 = data2.to(device)
        #y = data[0].y.view(-1, 1).long().to(device)
        y = data[0].y.view(-1, 1).float().to(device)
        y = y.squeeze(1)
        optimizer.zero_grad()
        output = model(data1, data2)
        loss = loss_fn(output, y)
        # print('loss', loss)
        loss.backward()
        optimizer.step()
        if batch_idx % LOG_INTERVAL == 0:
            print('Train epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch,
                                                                           batch_idx * len(data1.x),
                                                                           len(drug1_loader_train.dataset),
                                                                           100. * batch_idx / len(drug1_loader_train),
                                                                           loss.item()))


def predicting(model, device, drug1_loader_test, drug2_loader_test):
    model.eval()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()
    print('Make prediction for {} samples...'.format(len(drug1_loader_test.dataset)))
    with torch.no_grad():
        for data in zip(drug1_loader_test, drug2_loader_test):
            data1 = data[0]
            data2 = data[1]
            data1 = data1.to(device)
            data2 = data2.to(device)
            output = model(data1, data2)
            #ys = F.softmax(output, 1).to('cpu').data.numpy()
            ys = output.to('cpu').data.numpy()
            #predicted_labels = list(map(lambda x: np.argmax(x), ys))
            predicted_labels = list(map(lambda x: int(x>0.5), ys))
            #predicted_scores = list(map(lambda x: x[1], ys))
            predicted_scores = list(map(lambda x: x, ys))
            total_preds = torch.cat((total_preds, torch.Tensor(predicted_scores)), 0)
            total_prelabels = torch.cat((total_prelabels, torch.Tensor(predicted_labels)), 0)
            total_labels = torch.cat((total_labels, data1.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(), total_preds.numpy().flatten(), total_prelabels.numpy().flatten()


def shuffle_dataset(dataset, seed):
    np.random.seed(seed)
    np.random.shuffle(dataset)
    return dataset


def split_dataset(dataset, ratio):
    n = int(len(dataset) * ratio)
    dataset_1, dataset_2 = dataset[:n], dataset[n:]
    return dataset_1, dataset_2


# CPU or GPU

if torch.cuda.is_available():
    device = torch.device('cuda:'+str(device_num))
    print('The code uses GPU...')
else:
    device = torch.device('cpu')
    print('The code uses CPU!!!')


TRAIN_BATCH_SIZE = 1024
TEST_BATCH_SIZE = 1024
LR = 0.001
LOG_INTERVAL = 20
NUM_EPOCHS = 200

print('Learning rate: ', LR)
print('Epochs: ', NUM_EPOCHS)

cellfile = 'data/cell_features_954.csv'  
drug_smiles_file = 'data/smiles.csv'                  

if leave_type == 'leave_drug':
    train_datafile = ['data/leave_drug/leave_d00.csv',
                        'data/leave_drug/leave_d11.csv',
                        'data/leave_drug/leave_d22.csv',
                        'data/leave_drug/leave_d33.csv',
                        'data/leave_drug/leave_d44.csv']   
    train_pt_dataset = ['leave_drug_d00', 'leave_drug_d11', 'leave_drug_d22', 'leave_drug_d33', 'leave_drug_d44']   
    test_datafile = ['data/leave_drug/d00.csv',
                        'data/leave_drug/d11.csv',
                        'data/leave_drug/d22.csv',
                        'data/leave_drug/d33.csv',
                        'data/leave_drug/d44.csv']
    test_pt_result_dataset = ['drug_d00', 'drug_d11', 'drug_d22', 'drug_d33', 'drug_d44']
    fold_num = 5
elif leave_type == 'leave_comb':
    train_datafile = ['data/leave_comb/leave_c00.csv',
                        'data/leave_comb/leave_c11.csv',
                        'data/leave_comb/leave_c22.csv',
                        'data/leave_comb/leave_c33.csv',
                        'data/leave_comb/leave_c44.csv']    
    train_pt_dataset = ['leave_comb_c00', 'leave_comb_c11', 'leave_comb_c22', 'leave_comb_c33', 'leave_comb_c44']     
    test_datafile = ['data/leave_comb/c00.csv',
                        'data/leave_comb/c11.csv',
                        'data/leave_comb/c22.csv',
                        'data/leave_comb/c33.csv',
                        'data/leave_comb/c44.csv']
    test_pt_result_dataset = ['comb_c00', 'comb_c11', 'comb_c22', 'comb_c33', 'comb_c44']
    fold_num = 5
elif leave_type == 'leave_cell':
    train_datafile = ['data/leave_cell/leave_breast.csv',
                        'data/leave_cell/leave_colon.csv',
                        'data/leave_cell/leave_lung.csv',
                        'data/leave_cell/leave_melanoma.csv',
                        'data/leave_cell/leave_ovarian.csv',
                        'data/leave_cell/leave_prostate.csv']    
    train_pt_dataset = ['leave_cell_breast', 'leave_cell_colon', 'leave_cell_lung', 'leave_cell_melanoma', 'leave_cell_ovarian', 'leave_cell_prostate']   
    test_datafile = ['data/leave_cell/breast.csv',
                        'data/leave_cell/colon.csv',
                        'data/leave_cell/lung.csv',
                        'data/leave_cell/melanoma.csv',
                        'data/leave_cell/ovarian.csv',
                        'data/leave_cell/prostate.csv']
    test_pt_result_dataset = ['cell_breast', 'cell_colon', 'cell_lung', 'cell_melanoma', 'cell_ovarian', 'cell_prostate']
    fold_num = 6

for i in range(fold_num):

    train_drug1, train_drug2, train_cell, train_label, smile_graph, cell_features = creat_data(train_datafile[i], drug_smiles_file, cellfile)
    train_drug1_data = TestbedDataset(dataset=train_pt_dataset[i] + '_drug1', xd=train_drug1, xt=train_cell, y=train_label, smile_graph=smile_graph, xt_featrue=cell_features)
    train_drug2_data = TestbedDataset(dataset=train_pt_dataset[i] + '_drug2', xd=train_drug2, xt=train_cell, y=train_label, smile_graph=smile_graph, xt_featrue=cell_features)
    print('src_new_labels_0_10[0]', train_drug1_data[0])
    lenth = len(train_drug1_data)
    random_num = random.sample(range(0, lenth), lenth)
    drug1_data = train_drug1_data[random_num]
    drug2_data = train_drug2_data[random_num]


    test_drug1, test_drug2, test_cell, test_label, smile_graph, cell_features = creat_data(test_datafile[i], drug_smiles_file, cellfile)
    test_drug1_data = TestbedDataset(dataset=test_pt_result_dataset[i] + '_drug1', xd=test_drug1, xt=test_cell, y=test_label, smile_graph=smile_graph, xt_featrue=cell_features)
    test_drug2_data = TestbedDataset(dataset=test_pt_result_dataset[i] + '_drug2', xd=test_drug2, xt=test_cell, y=test_label, smile_graph=smile_graph, xt_featrue=cell_features)
    lenth = len(test_drug1_data)

    # build training set
    drug1_loader_train = DataLoader(drug1_data, batch_size=TRAIN_BATCH_SIZE, shuffle=None)
    drug2_loader_train = DataLoader(drug2_data, batch_size=TRAIN_BATCH_SIZE, shuffle=None)

    # build test set
    drug1_loader_test = DataLoader(test_drug1_data, batch_size=TEST_BATCH_SIZE, shuffle=None)
    drug2_loader_test = DataLoader(test_drug2_data, batch_size=TEST_BATCH_SIZE, shuffle=None)

    model = modeling().to(device)
    #loss_fn = nn.CrossEntropyLoss()
    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    folder_path = './result/' + result_name
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_AUCs = folder_path + '/'+ result_name + '_' + str(i) + '--AUCs--' + test_pt_result_dataset[i] + '_' + time_str + '.txt'
    AUCs = ('Epoch\tAUC_dev\tPR_AUC\tACC\tBACC\tPREC\tTPR\tKAPPA\tRECALL')
    with open(file_AUCs, 'w') as f:
        f.write(AUCs + '\n')

    best_auc = 0
    for epoch in range(NUM_EPOCHS):
        train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch + 1)
        T, S, Y = predicting(model, device, drug1_loader_test, drug2_loader_test)
        # T is correct label
        # S is predict score
        # Y is predict label

        # compute preformence
        AUC = roc_auc_score(T, S)
        precision, recall, threshold = metrics.precision_recall_curve(T, S)
        PR_AUC = metrics.auc(recall, precision)
        BACC = balanced_accuracy_score(T, Y)
        tn, fp, fn, tp = confusion_matrix(T, Y).ravel()
        TPR = tp / (tp + fn)
        PREC = precision_score(T, Y)
        ACC = accuracy_score(T, Y)
        KAPPA = cohen_kappa_score(T, Y)
        recall = recall_score(T, Y)


        # save data

        if best_auc < AUC:
            best_auc = AUC
            # torch.save(model.state_dict(), model_file_name)
            # independent_num = []
            # independent_num.append(test_num)
            # independent_num.append(T)
            # independent_num.append(Y)
            # independent_num.append(S)
            # txtDF = pd.DataFrame(data=independent_num)
            # txtDF.to_csv(result_file_name, index=False, header=False)
            AUCs = [epoch, AUC, PR_AUC, ACC, BACC, PREC, TPR, KAPPA]
            save_AUCs(AUCs, file_AUCs)
        print('best_auc', best_auc)
    save_AUCs("best_auc:"+str(best_auc), file_AUCs)
````

## File: DualSyn/train_transductive.py
````python
import random
import torch.nn.functional as F
import torch.nn as nn
from models.dualsyn import DualSyn
from utils_test import *
from sklearn.metrics import roc_curve, confusion_matrix
from sklearn.metrics import cohen_kappa_score, accuracy_score, roc_auc_score, precision_score, recall_score, \
    balanced_accuracy_score
from sklearn import metrics
from creat_data_DC import creat_data
import pandas as pd
import datetime
import argparse


result_name = 'DualSyn_transductive'

modeling = DualSyn

# training function at each epoch
def train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch):
    print("===============")
    print('Training on {} samples...'.format(len(drug1_loader_train.dataset)))
    model.train()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()

    zipped = zip(drug1_loader_train, drug2_loader_train)
    enumerate_data = enumerate(zipped)
    for batch_idx, data in enumerate_data:  
        data1 = data[0]
        data2 = data[1]
        data1 = data1.to(device)
        data2 = data2.to(device)
        y = data[0].y.view(-1, 1).float().to(device)
        y = y.squeeze(1)
        optimizer.zero_grad()
        output = model(data1, data2)
        loss = loss_fn(output, y)
        # print('loss', loss)
        loss.backward()
        optimizer.step()
        if batch_idx % LOG_INTERVAL == 0:
            print('Train epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch,
                                                                           batch_idx * len(data1.x),
                                                                           len(drug1_loader_train.dataset),
                                                                           100. * batch_idx / len(drug1_loader_train),
                                                                           loss.item()))
        ys = output.to('cpu').data.numpy()
        predicted_labels = list(map(lambda x: int(x>0.5), ys))
        predicted_scores = list(map(lambda x: x, ys))
        total_preds = torch.cat((total_preds, torch.Tensor(predicted_scores)), 0)
        total_prelabels = torch.cat((total_prelabels, torch.Tensor(predicted_labels)), 0)
        total_labels = torch.cat((total_labels, data1.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(), total_preds.numpy().flatten(), total_prelabels.numpy().flatten()


def predicting(model, device, drug1_loader_test, drug2_loader_test):
    model.eval()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    total_prelabels = torch.Tensor()
    print('Make prediction for {} samples...'.format(len(drug1_loader_test.dataset)))
    with torch.no_grad():
        for data in zip(drug1_loader_test, drug2_loader_test):
            data1 = data[0]
            data2 = data[1]
            data1 = data1.to(device)
            data2 = data2.to(device)
            output = model(data1, data2)
            ys = output.to('cpu').data.numpy()
            predicted_labels = list(map(lambda x: int(x>0.5), ys))
            predicted_scores = list(map(lambda x: x, ys))
            total_preds = torch.cat((total_preds, torch.Tensor(predicted_scores)), 0)
            total_prelabels = torch.cat((total_prelabels, torch.Tensor(predicted_labels)), 0)
            total_labels = torch.cat((total_labels, data1.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(), total_preds.numpy().flatten(), total_prelabels.numpy().flatten()


def shuffle_dataset(dataset, seed):
    np.random.seed(seed)
    np.random.shuffle(dataset)
    return dataset


def split_dataset(dataset, ratio):
    n = int(len(dataset) * ratio)
    dataset_1, dataset_2 = dataset[:n], dataset[n:]
    return dataset_1, dataset_2


# CPU or GPU

if torch.cuda.is_available():
    device = torch.device('cuda:0')
    print('The code uses GPU...')
else:
    device = torch.device('cpu')
    print('The code uses CPU!!!')


TRAIN_BATCH_SIZE = 1024
TEST_BATCH_SIZE = 1024
LR = 0.0005
LOG_INTERVAL = 20
NUM_EPOCHS = 400

print('Learning rate: ', LR)
print('Epochs: ', NUM_EPOCHS)

cellfile = 'data/cell_features_954.csv'  
drug_smiles_file = 'data/smiles.csv'  
datafile = 'data/new_labels_0_10.csv' 
dataset = 'new_labels_0_10'


print('开始处理源文件....')
drug1, drug2, cell, label, smile_graph, cell_features = creat_data(datafile, drug_smiles_file, cellfile)
print('从源文件提取特征成功！')

print('载入数据...')
drug1_data = TestbedDataset(dataset=dataset + '_drug1', xd=drug1, xt=cell, y=label, smile_graph=smile_graph,
                            xt_featrue=cell_features)
drug2_data = TestbedDataset(dataset=dataset + '_drug2', xd=drug2, xt=cell, y=label, smile_graph=smile_graph,
                            xt_featrue=cell_features)
print('载入数据完成！')

lenth = len(drug1_data)
pot = int(lenth / 5)
print('lenth', lenth)
print('pot', pot)

random_num = random.sample(range(0, lenth), lenth)  

folder_path = './result/' + result_name
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


for i in range(5):

    test_num = random_num[pot * i:pot * (i + 1)]  
    train_num = random_num[:pot * i] + random_num[pot * (i + 1):] 

    drug1_data_train = drug1_data[train_num]  
    drug1_data_test = drug1_data[test_num]  
    drug1_loader_train = DataLoader(drug1_data_train, batch_size=TRAIN_BATCH_SIZE,
                                    shuffle=None) 
    drug1_loader_test = DataLoader(drug1_data_test, batch_size=TRAIN_BATCH_SIZE,
                                   shuffle=None)  


    drug2_data_test = drug2_data[test_num]
    drug2_data_train = drug2_data[train_num]
    drug2_loader_train = DataLoader(drug2_data_train, batch_size=TRAIN_BATCH_SIZE, shuffle=None)
    drug2_loader_test = DataLoader(drug2_data_test, batch_size=TRAIN_BATCH_SIZE, shuffle=None)

    model = modeling().to(device)
    # torch.save(model.state_dict(), 'save_model/'+ result_name + '_'+ str(i)+'_epoch=0.pt')
    #loss_fn = nn.CrossEntropyLoss()
    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    file_AUCs = folder_path + '/'+ result_name + '_' + str(i) + '--AUCs--' + dataset + '_' + time_str + '.txt'
    AUCs = ('Epoch\tAUC_dev\tPR_AUC\tACC\tBACC\tPREC\tTPR\tKAPPA\tRECALL')
    with open(file_AUCs, 'w') as f:
        f.write(AUCs + '\n')

    best_auc = 0
    for epoch in range(NUM_EPOCHS):
        train_T, train_S, train_Y = train(model, device, drug1_loader_train, drug2_loader_train, optimizer, epoch + 1)
        T, S, Y = predicting(model, device, drug1_loader_test, drug2_loader_test)
        # T is correct label
        # S is predict score
        # Y is predict label

        # compute preformence
        AUC = roc_auc_score(T, S)
        precision, recall, threshold = metrics.precision_recall_curve(T, S)
        PR_AUC = metrics.auc(recall, precision)
        BACC = balanced_accuracy_score(T, Y)
        tn, fp, fn, tp = confusion_matrix(T, Y).ravel()
        TPR = tp / (tp + fn)
        PREC = precision_score(T, Y)
        ACC = accuracy_score(T, Y)
        KAPPA = cohen_kappa_score(T, Y)
        recall = recall_score(T, Y)

        train_AUC = roc_auc_score(train_T, train_S)
        train_precision, train_recall, train_threshold = metrics.precision_recall_curve(T, S)
        train_PR_AUC = metrics.auc(train_recall, train_precision)
        train_ACC = accuracy_score(train_T, train_Y)
        
        print("Train: AUC={}, PR_AUC={}, ACC={}".format(train_AUC, train_PR_AUC, train_ACC))
        print("Test: AUC={}, PR_AUC={}, ACC={}".format(AUC, PR_AUC, ACC))


        # save data

        if best_auc < AUC:
            best_auc = AUC

            AUCs = [epoch, AUC, PR_AUC, ACC, BACC, PREC, TPR, KAPPA, recall]
            save_AUCs(AUCs, file_AUCs)
        
        print('best_auc', best_auc)  
    save_AUCs("best_auc:" + str(best_auc), file_AUCs)
    # torch.save(model.state_dict(), 'save_model/'+ result_name + '_'+ str(i)+'_epoch=400.pt')
````

## File: DualSyn/utils_test.py
````python
import os
from itertools import islice
import sys
import numpy as np
from math import sqrt
from scipy import stats
from torch_geometric.data import InMemoryDataset, DataLoader
from torch_geometric import data as DATA
import torch
import pandas as pd
import random
import copy

class TestbedDataset(InMemoryDataset):   
    def __init__(self, root='data', dataset=None,
                 xd=None, xt=None, y=None, xt_featrue=None, transform=None,
                 pre_transform=None, smile_graph=None):

        #root is required for save preprocessed data, default is '/tmp'
        super(TestbedDataset, self).__init__(root, transform, pre_transform)

        self.dataset = dataset

        print('Start processing data...')

        if os.path.isfile(self.processed_paths[0]):
            print('Pre-processed data found: {}, loading ...'.format(self.processed_paths[0]))
            self.data, self.slices = torch.load(self.processed_paths[0])
        else:
            print('Pre-processed data {} not found, doing pre-processing...'.format(self.processed_paths[0]))
            self.process(xd, xt, xt_featrue, y, smile_graph)
            self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def raw_file_names(self):
        pass
        #return ['some_file_1', 'some_file_2', ...]

    @property
    def processed_file_names(self):
        return [self.dataset + '.pt']
        #pass

    def download(self):
        # Download to `self.raw_dir`.
        pass

    def _download(self):
        pass

    def _process(self):
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

    def get_cell_feature(self, cellId, cell_features):
        for row in islice(cell_features, 0, None): 
            if cellId in row[0]:  
                return row[1:]  
        return False


    def process(self, xd, xt, xt_featrue, y, smile_graph):  
        assert (len(xd) == len(xt) and len(xt) == len(y)), "The three lists must be the same length!"
        data_list = []
        data_len = len(xd)
        print('number of data', data_len)

        for i in range(data_len):
            # print('Converting SMILES to graph: {}/{}'.format(i+1, data_len))
            smiles = xd[i]
            target = xt[i]
            labels = y[i]

            cell = self.get_cell_feature(target, xt_featrue)  
            if cell == False:  
                print('cell', cell)
                sys.exit()
            new_cell = []
            # print('cell_feature', cell_feature)
            for n in cell:
                new_cell.append(float(n))

            c_size, features, edge_index = smile_graph[smiles]


            GCNData = DATA.Data(x=torch.Tensor(features), 
                                edge_index=torch.LongTensor(edge_index).transpose(1, 0),
                                
                                y=torch.Tensor([labels]))  
            GCNData.cell = torch.FloatTensor([new_cell])
            GCNData.__setitem__('c_size', torch.LongTensor([c_size]))
            # append graph, label and target sequence to data list
            data_list.append(GCNData)


        if self.pre_filter is not None:
            data_list = [data for data in data_list if self.pre_filter(data)]

        if self.pre_transform is not None:
            data_list = [self.pre_transform(data) for data in data_list]
        print('Graph construction done. Saving to file.')
        data, slices = self.collate(data_list)  
        torch.save((data, slices), self.processed_paths[0])  

def save_AUCs(AUCs, filename):
    with open(filename, 'a') as f:
        f.write('\t'.join(map(str, AUCs)) + '\n')
````

## File: LICENSE
````
MIT License

Copyright (c) 2024 chakchen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

## File: README.md
````markdown
# DualSyn: A Dual-Level Feature Interaction Method to Predict Synergistic Drug Combinations

## Introduction

Drug combination therapy can reduce drug resistance and improve treatment efficacy, making it an increasingly promising cancer treatment method. Although existing computational methods have achieved significant success, predictions on unseen data remain a challenge. There are complex associations between drug pairs and cell lines, and existing models cannot capture more general feature interaction patterns among them, which hinders the ability of models to generalize from seen samples to unseen samples. To address this problem, we propose a dual-level feature interaction model called DualSyn to efficiently predict the synergy of drug combination therapy. This model first achieves interaction at the drug pair level through the drugs feature extraction module. We also designed two modules to further deepen the interaction at the drug pair and cell line level from two different perspectives. The high-order relation module is used to capture the high-order relationships among the three features, and the global information module focuses on preserving global information details. DualSyn not only improves the AUC by 2.15\% compared with the state-of-the-art methods in the transductive task of the benchmark dataset, but also surpasses them in all four tasks under the inductive setting. Overall, DualSyn shows great potential in predicting and explaining drug synergistic therapies, providing a powerful new tool for future clinical applications.

![DualSyn](https://github.com/chakchen/DualSyn/blob/main/image/DualSyn.jpg)

# Installation

You can create a virtual environment using conda

```
conda create -n ddi python=3.7
source activate ddi
conda install pytorch==1.9.0 cudatoolkit=10.2 -c pytorch
pip install https://data.pyg.org/whl/torch-1.9.0%2Bcu102/torch_scatter-2.0.9-cp37-cp37m-linux_x86_64.whl -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install https://data.pyg.org/whl/torch-1.9.0%2Bcu102/torch_sparse-0.6.12-cp37-cp37m-linux_x86_64.whl -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install torch-geometric==2.0.3
pip install https://data.pyg.org/whl/torch-1.9.0%2Bcu102/torch_cluster-1.5.9-cp37-cp37m-linux_x86_64.whl -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install https://data.pyg.org/whl/torch-1.9.0%2Bcu102/torch_spline_conv-1.2.1-cp37-cp37m-linux_x86_64.whl -i https://pypi.tuna.tsinghua.edu.cn/simple
conda install -c rdkit rdkit
```

## Usage

Train the model for transductive task

```
python train_transductive.py
```

Train the model for inductive task (Include leave-out setting and independent dataset setting)

```
bash inductive.sh
```
````
