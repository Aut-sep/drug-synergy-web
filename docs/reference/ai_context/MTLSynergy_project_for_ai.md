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
AEtrain.py
data/cell_line_features_sample.csv
data/cell_lines_sample.csv
data/drug_features_sample.csv
data/drugs_sample.csv
data/oneil_summary_idx_sample.csv
Dataset.py
GBM_LeaveCellOut.py
GBM_LeaveDrugOut.py
GBMtrain.py
Models.py
MTLSynergy_LeaveCellOut.py
MTLSynergy_LeaveDrugOut.py
MTLSynergytrain.py
README.md
RF_LeaveCellOut.py
RF_LeaveDrugOut.py
RFtrain.py
static/constant.py
utils/tools.py
```

# Files

## File: .repomixignore
```
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
```

## File: data/cell_line_features_sample.csv
```
TSPAN6,CFH,FUCA2,GCLC
2.2474455407047564,2.5851841995363345,-0.2074982269019793,2.246446997618922
0.7013751189423649,-0.7616106030591328,1.171448873011025,1.0362998438436508
-0.5514563169619481,-0.8354886116719006,0.7110352476893406,-0.07543414262083452
```

## File: data/cell_lines_sample.csv
```
id,name,synonyms,from_oneil
0,RT-4,RT-4; RT4; RT4P,No
1,SW837,SW837; SW-837; SW 837,Yes
2,A101D,A101D; A-101D,No
```

## File: data/drug_features_sample.csv
```
0,1,2,3
-0.45949890964366696,-0.2769273012556875,-0.20474893901969765,-0.310408643169523
-0.45949890964366696,-0.2769273012556875,-0.20474893901969765,-0.310408643169523
-0.45949890964366696,-0.2769273012556875,-0.20474893901969765,-0.310408643169523
```

## File: data/drugs_sample.csv
```
id,name,synonyms,from_oneil
0,5-FU,"5-Fluorouracil; fluorouracil; 51-21-8; 5-FU; Fluoroplex; Efudex; Adrucil; Carac; Fluracil; 5-fluoropyrimidine-2,4(1H,3H)-dione; Fluoroblastin; Kecimeton; Carzonal; Timazin; Arumel; Efudix; Fluril; 5-Fluoracil; Fluracilum; Queroplex; Ulup; Phthoruracil; Fluro Uracil; 5-fluoro-1H-pyrimidine-2,4-dione; 5-Fluoro-2,4(1H,3H)-pyrimidinedione; Fluorouracilum; Ftoruracil; Efurix; Fluri; 5 Fluorouracil; 5-Fluoropyrimidine-2,4-dione; Effluderm (free base); Fluorouracilo; Fluroblastin; 2,4(1H,3H)-Pyrimidinedione, 5-fluoro-; 2,4-Dihydroxy-5-fluoropyrimidine; Fluoro-uracile; Fluoro-uracilo; Uracil, 5-fluoro-; 5-Fluoruracil; 5-Faracil; Cinco FU; Ro 2-9757; 5-Fluor-2,4-pyrimidindiol; Fluorouracile [DCIT]; 5-Fluoracil [German]; 5-fluoro uracil; 5-Ftouracyl; 5-Fluoruracil [German]; Fluorouracil, 5-; Fluorouracilum [INN-Latin]; Fluorouracilo [INN-Spanish]; 5-Fluoropyrimidin-2,4-diol; 5-fluoropyrimidine-2,4-diol; C4H3FN2O2; NSC 19893; NSC-19893; 2,4-Dioxo-5-fluoropyrimidine; 5-Fluoro-2,4-pyrimidinedione; Fluorouracil (Adrucil); 5-Fluor-2,4-dihydroxypyrimidin; U-8953; 5-fluoro-uracil; 5-Fluor-2,4-pyrimidindiol [Czech]; Ro-2-9757; UNII-U3P01618RT; CCRIS 2582; 5-Fluor-2,4-dihydroxypyrimidin [Czech]; FU; HSDB 3228; 5-Fluor-2,4(1H,3H)-pyrimidindion [Czech]; 5-Fluorouracil, 99%; EINECS 200-085-6; CHEMBL185; AI3-25297; MLS000069498; 191047-65-1; 5FU; Phtoruracil; CHEBI:46345; U3P01618RT; NSC19893; 5-fluoro-1,2,3,4-tetrahydropyrimidine-2,4-dione; MFCD00006018; URF; NCGC00015442-02; Fluorouracile; Effluderm; SMR000038082; DSSTox_CID_634; 5-Fluoracyl; DSSTox_RID_75705; DSSTox_GSID_20634; Fluorouracil Cream; CAS-51-21-8; Fluoroplex (TN); 1004-03-1; 5-fluoranyl-1H-pyrimidine-2,4-dione; Adrucil (TN); 5-fluoro-1,3-dihydropyrimidine-2,4-dione; Carac (TN); SR-01000075881; Fluorouracil [USAN:INN:BAN:JAN]; 5-Fluor-2,4(1H,3H)-pyrimidindion; Fluouracil; inhibits thymilidate synthetase; Tolak; 2,4-Dioxo-5-fluoropryimidine; 5-fluorourasil; Fluoro Uracil; 5-florouracil; 5-fluorouacil; 5-flurouricil; 5-FU (TN); 5-Fluracil; 1upf; 5F-uracil; U 8953; 1-fluoro-1h-pyrimidine-2,4-dione; Adrucil (ICN); Fluorouracil (5-Fluoracil, 5-FU); Adrucil (Fluorouracil); Fluorouracil - Adrucil; Fluorouracil [USAN:USP:INN:BAN:JAN]; Spectrum_000841; ACMC-1ATRK; Opera_ID_134; Spectrum2_000076; Spectrum3_000434; Spectrum4_000557; Spectrum5_000718; WLN: T6MVMVJ EF; Lopac-F-6627; F0151; UPCMLD-DP130; EC 200-085-6; F 6627; SCHEMBL3646; 5-fluorpyrimidin-2,4-diol; Lopac0_000536; BSPBio_002048; KBioGR_001253; KBioSS_001321; KSC270K6T; MLS002415705; 5-fluoro-2,4-Pyrimidinediol; DivK1c_000054; SPECTRUM1500305; SPBio_000291; 5 FU; 5-fluoro-2,4-dioxo-pyrimidin; 5-fluoro-pyrimidine-2,4-diol; GTPL4789; DTXSID2020634; UPCMLD-DP130:001; CTK1H0569; CTK8H4220; Fluorouracil (JP17/USP/INN); HMS500C16; KBio1_000054; KBio2_001321; KBio2_003889; KBio2_006457; KBio3_001268; 5-Fluoro-2,3H)-pyrimidinedione; 2,4-Pyrimidinedione, 5-fluoro-; NINDS_000054; BCPP000428; HMS1920O18; HMS2090I04; HMS2091F19; HMS3259O03; HMS3261L13; HMS3654K22; HMS3715H03; HMS3865L03; Pharmakon1600-01500305; 5-Fluorouracil, analytical standard; BCP02083; KS-00000DY3; 2,3H)-Pyrimidinedione, 5-fluoro-; Tox21_110150; Tox21_202335; Tox21_300112; Tox21_500536; ANW-31214; BBL009635; BDBM50340677; CCG-39879; CF0033; DL-399; LS-153; NSC757036; Ro-29757; RW2456; s1209; SBB085751; STK297802; STL367375; ZINC38212689; AKOS000119162; AKOS003237897; AKOS008044307; Tox21_110150_1; BCP9000239; CS-0993; DB00544; KS-5129; LP00536; LS40596; MCULE-6338086431; NC00454; NSC-757036; SDCCGSBI-0050519.P005; IDI1_000054; NCGC00015442-01; NCGC00015442-03; NCGC00015442-04; NCGC00015442-05; NCGC00015442-06; NCGC00015442-07; NCGC00015442-08; NCGC00015442-09; NCGC00015442-10; NCGC00015442-11; NCGC00015442-12; NCGC00015442-15; NCGC00015442-16; NCGC00015442-30; NCGC00091349-01; NCGC00091349-02; NCGC00091349-03; NCGC00091349-04; NCGC00091349-05; NCGC00091349-07; NCGC00091349-08; NCGC00254023-01; NCGC00259884-01; NCGC00261221-01; 5-Fluoro-2,4-(1H,3H)-pyrimidinedione; AC-11201; AK-46307; HY-90006; NCI60_001652; SC-09038; SRI-10792-04; SRI-10792-05; SRI-10792-06; SRI-10792_07; SRI-10792_08; 5-Fluoro-1H-pyrimidine-2,4-dione(5FU); 5-Fluorouracil, >=99% (HPLC), powder; SBI-0050519.P004; 5-Fluoro-1H-pyrimidine-2,4-dione(5-FU); DB-051923; DB-065735; 5-Fluoro-1H-pyrimidine-2,4-dione (5-FU); AM20100252; EU-0100536; FT-0601511; FT-0668745; FT-0695666; FT-0695667; FT-0707652; NS00000337; ST45025877; SW199617-3; 5-Fluoro-1H-pyrimidine-2,4-dione(5-FUra); Fluorouracil, meets USP testing specifications; 51F218; 7375-EP2269989A1; 7375-EP2269994A1; 7375-EP2270008A1; 7375-EP2270018A1; 7375-EP2272827A1; 7375-EP2272832A1; 7375-EP2275102A1; 7375-EP2275412A1; 7375-EP2275413A1; 7375-EP2277876A1; 7375-EP2280012A2; 7375-EP2281563A1; 7375-EP2281815A1; 7375-EP2287156A1; 7375-EP2289892A1; 7375-EP2292233A2; 7375-EP2292614A1; 7375-EP2292615A1; 7375-EP2292617A1; 7375-EP2295416A2; 7375-EP2295426A1; 7375-EP2295427A1; 7375-EP2298748A2; 7375-EP2298768A1; 7375-EP2298772A1; 7375-EP2298780A1; 7375-EP2301928A1; 7375-EP2301933A1; 7375-EP2305219A1; 7375-EP2305243A1; 7375-EP2305640A2; 7375-EP2305642A2; 7375-EP2305671A1; 7375-EP2305689A1; 7375-EP2308833A2; 7375-EP2308839A1; 7375-EP2308855A1; 7375-EP2308861A1; 7375-EP2311807A1; 7375-EP2311808A1; 7375-EP2311825A1; 7375-EP2311827A1; 7375-EP2311829A1; 7375-EP2311840A1; 7375-EP2314590A1; 7375-EP2316459A1; 7375-EP2316831A1; 7375-EP2316834A1; 7375-EP2316974A1; 7375-EP2374454A1; C07649; D00584; W-5036; 29507-EP2270008A1; 29507-EP2270505A1; 29507-EP2272827A1; 29507-EP2289892A1; 29507-EP2292234A1; 29507-EP2292617A1; 29507-EP2295426A1; 29507-EP2295427A1; 29507-EP2298305A1; 29507-EP2308861A1; 29507-EP2311842A2; 42164-EP2272827A1; 42164-EP2275420A1; 42164-EP2277565A2; 42164-EP2277566A2; 42164-EP2277567A1; 42164-EP2277568A2; 42164-EP2277569A2; 42164-EP2277570A2; 42164-EP2277876A1; 42164-EP2292280A1; 42164-EP2292614A1; 42164-EP2295412A1; 42164-EP2295413A1; 42164-EP2295416A2; 42164-EP2298748A2; 42164-EP2298764A1; 42164-EP2298765A1; 42164-EP2298778A1; 42164-EP2305642A2; 42164-EP2308833A2; 42164-EP2311808A1; 42164-EP2311829A1; 42164-EP2311840A1; 5-Fluorouracil, Vetec(TM) reagent grade, >=99%; Q238512; W-60379; (5-fluorouracil)5-Fluoro-1H-pyrimidine-2,4-dione; 5-Fluoro-1H-pyrimidine-2,4-dione(5-fluoro uracil); SR-01000075881-1; SR-01000075881-3; SR-01000075881-5; W-202929; 5-Fluoro-1H-pyrimidine-2,4-dione (5-Fluorouracil); BRD-K24844714-001-02-1; Z275128052; 5-Fluoro-1H-pyrimidine-2,4-dione(5-fluorouracil)(5-FU); 5-Fluorouracil, certified reference material, TraceCERT(R); Fluorouracil, British Pharmacopoeia (BP) Reference Standard; Fluorouracil, European Pharmacopoeia (EP) Reference Standard; Fluorouracil, United States Pharmacopeia (USP) Reference Standard; pyrimidine antimetabolite: inhibits nucleic acid replication; tetratogen; Fluorouracil, Pharmaceutical Secondary Standard; Certified Reference Material",Yes
1,ABT-888,"Veliparib; 912444-00-9; ABT-888; ABT 888; ABT-888 (Veliparib); (R)-2-(2-methylpyrrolidin-2-yl)-1H-benzo[d]imidazole-4-carboxamide; ABT888; UNII-01O4K0631N; 2-[(2R)-2-methyl-2-pyrrolidinyl]-1H-benzimidazole-7-carboxamide; 2-[(2R)-2-Methylpyrrolidin-2-yl]-1H-benzimidazole-4-carboxamide; CHEBI:62880; 2-[(R)-2-methylpyrrolidin-2-yl]-1H-benzimidazole-4-carboxamide; 01O4K0631N; 2-[(2R)-2-Methylpyrrolidin-2-yl]-1H-benimidazole-4-; (2r)-2-(7-Carbamoyl-1h-Benzimidazol-2-Yl)-2-Methylpyrrolidinium; Veliparib (ABT-888); 2-((2r)-2-methyl-2-pyrrolidinyl)-1h-benzimidazole-7-carboxamide; (R)-2-(2-methylpyrrolidin-2-yl)-1H-benzo[d]imidazole-7-carboxamide; ABT-888(Veliparib); NSC-737664; Veliparib [USAN:INN]; 2-((2R)-2-methylpyrrolidin-2-yl)-1H-benzimidazole-4-carboxamide; 78P; Veliparib free base; ABT-888 Veliparib; ABT888 (free base); A861695; benzimidazole carboxamide, 3a; cc-346; MLS006010184; Veliparib (JAN/USAN/INN); SCHEMBL422318; CHEMBL506871; GTPL7417; QCR-33; BDBM27135; ABT-695; DTXSID90238456; EX-A001; BDBM209932; AOB87114; EBD52357; PARP-1 INHIBITOR ABT-888; Veliparib (ABT-888 hydrochloride); 2-[(2R)-2-methylpyrrolidin-2-yl]-1H-1,3-benzodiazole-4-carboxamide; 912444-00-9 (free base); ABP000419; NSC737664; s1004; ZINC84610155; AKOS015951440; AKOS017343746; CCG-264771; CS-0076; DB07232; EX-7209; SB16480; ABT-888(Veliparib)/MX-1,ABT888; NCGC00250404-01; AC-23330; AK-36839; AS-19397; HY-10129; SMR004701290; ABT-888 (Veliparib, NSC 737664); X7540; A24888; D09692; W-5661; A 861695; A-861695; J-505211; Q7919041; BRD-K87142802-001-02-7; 1H-Benzimidazole-4-carboxamide, 2-((2R)-2-methyl-2-pyrrolidinyl)-; 2-[(2R)-2-methylpyrrolidin-2-yl]-1H-benzimidazole-7-carboxamide; (R)-2-(2-Methylpyrrolidin-2-yl)-1H-benimidazole-4-carboxamide (VELIPARIB); ABT-888;2-[(2R)-2-Methylpyrrolidin-2-yl]-1H-benimidazole-4- carboxamide;(R)-2-(2-methylpyrrolidin-2-yl)-3H-benzo[d]imidazole-4-carboxamide",Yes
2,AZD1775,"MK-1775; 955365-80-7; Adavosertib; MK1775; MK 1775; AZD1775; AZD 1775; AZD-1775; UNII-K2T6HJX3I3; 2-allyl-1-(6-(2-hydroxypropan-2-yl)pyridin-2-yl)-6-(4-(4-methylpiperazin-1-yl)phenylamino)-1H-pyrazolo[3,4-d]pyrimidin-3(2H)-one; 1-[6-(2-hydroxypropan-2-yl)pyridin-2-yl]-6-[4-(4-methylpiperazin-1-yl)anilino]-2-prop-2-enylpyrazolo[3,4-d]pyrimidin-3-one; K2T6HJX3I3; 1-[6-(2-Hydroxypropan-2-Yl)pyridin-2-Yl]-6-{[4-(4-Methylpiperazin-1-Yl)phenyl]amino}-2-(Prop-2-En-1-Yl)-1,2-Dihydro-3h-Pyrazolo[3,4-D]pyrimidin-3-One; 2-Allyl-1-[6-(1-hydroxy-1-methylethyl)pyridin-2-yl]-6-[[4-(4-methylpiperazin-1-yl)phenyl]amino]-1,2-dihydro-3H-pyrazolo[3,4-d]pyrimidin-3-one; 3H-Pyrazolo(3,4-d)pyrimidin-3-one, 1,2-dihydro-1-(6-(1-hydroxy-1-methylethyl)-2-pyridinyl)-6-((4-(4-methyl-1-piperazinyl)phenyl)amino)-2-(2-propen-1-yl)-; 2-Allyl-1-(6-(2-hydroxypropan-2-yl)pyridin-2-yl)-6-((4-(4-methylpiperazin-1-yl)phenyl)amino)-1H-pyrazolo[3,4-d]pyrimidin-3(2H)-one; 3H-Pyrazolo[3,4-d]pyrimidin-3-one, 1,2-dihydro-1-[6-(1-hydroxy-1-methylethyl)-2-pyridinyl]-6-[[4-(4-methyl-1-piperazinyl)phenyl]amino]-2-(2-propen-1-yl)-; 8X7; Adavosertib (USAN); Kinome_2656; cc-686; MLS006011025; GTPL7702; QCR-46; SCHEMBL1504444; CHEMBL1976040; CHEBI:91414; DTXSID30241868; EX-A331; C27H32N8O2; HMS3295K03; HMS3654H20; HMS3744I13; AOB87173; BCP01928; ABP000952; BDBM50240826; s1525; ZINC63539231; AKOS024259153; MK-1775(AZD-1775,Adavosertib); AM90274; BCP9000937; CCG-264905; CS-0105; DB11740; MK-1775/MK1775; SB16663; KS-0000063H; NCGC00263183-01; NCGC00263183-10; 1-[6-(2-hydroxypropan-2-yl)pyridin-2-yl]-6-{[4-(4-methylpiperazin-1-yl)phenyl]amino}-2-(prop-2-en-1-yl)pyrazolo[3,4-d]pyrimidin-3-one; AC-28416; AK-99219; AS-17001; HY-10993; SC-94519; SMR004702820; AB0008188; FT-0699265; NS00072864; SW218122-2; X7493; D11361; S-7817; BRD-K54256913-001-01-2; Q27074716; 1,2-Dihydro-1-[6-(1-hydroxy-1-methylethyl)-2-pyridinyl]-6-[[4-(4-methyl-1-piperazinyl)phenyl]amino]-2-(2-propen-1-yl)-3h-pyrazolo[3,4-d]pyrimidin-3-one; 1075739-30-8; 2-allyl-1-(6-(2-hydroxypropan-2-yl)pyridin-2-yl)-6-(4-(4-methylpiperazin-1-yl)phenylamino)-1,2-dihydropyrazolo[3,4-d]pyrimidin-3-one; 2-allyl-1-(6-(2-hydroxypropan-2-yl)pyridin-2-yl)-6-(4-(4-methylpiperazin-1-yl)phenylamino)-1H-pyrazo; 2-Allyl-1-[6-(1-hydroxy-1-methyl-ethyl)-pyridin-2-yl]-6-[4-(4-methyl-piperazin-1-yl)-phenylamino]-1,2-dihydro-pyrazolo[3,4-d]pyrimidin-3-one",Yes
```

## File: data/oneil_summary_idx_sample.csv
```
drug_row_idx,drug_col_idx,cell_line_idx,ri_row
0,1,4,19.098
0,2,4,19.098
0,3,4,19.098
```

## File: AEtrain.py
```python
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from torch.utils.data import DataLoader
from torch.optim import Adam
from Dataset import DrugDataset, CellLineDataset
from Models import DrugAE, CellLineAE
from torch.nn import MSELoss
import torch
import time
import pandas as pd
from utils.tools import EarlyStopping, set_seed
from static.constant import DrugAE_OutputDim_Optional, CellAE_OutputDim_Optional, DrugAE_SaveBase, CellAE_SaveBase, \
    DrugAE_Result, CellLineAE_Result

device = torch.device('cuda')


def fit(model, train_dataloader, train_num, optimizer, criterion):
    print('---Training---')
    model.train()
    train_running_loss = 0.0
    for i, (x, y) in enumerate(train_dataloader):
        data, target = x.float().to(device), y.float().to(device)
        optimizer.zero_grad()
        outputs = model(data)
        loss = criterion(outputs, target)
        train_running_loss += (loss.item() * x.shape[0])
        loss.backward()
        optimizer.step()
    train_loss = train_running_loss / train_num
    return train_loss


def validate(model, validation_dataloader, validation_num, criterion):
    model.eval()
    validation_running_loss = 0.0
    with torch.no_grad():
        for i, (x, y) in enumerate(validation_dataloader):
            data, target = x.float().to(device), y.float().to(device)
            outputs = model(data)
            loss = criterion(outputs, target)
            validation_running_loss += (loss.item() * x.shape[0])
        validation_loss = validation_running_loss / validation_num
        return validation_loss


# drug AE train
drug_features_data = pd.read_csv('data/drug_features.csv')
drug_num = drug_features_data.shape[0]
print("drugs num:", drug_num)
drug_bz = 32
drug_lr = 0.0001
drug_epochs = 3000
drug_patience = 100
for drug_outputdim in DrugAE_OutputDim_Optional:
    set_seed(1)
    drugAE = DrugAE(output_dim=drug_outputdim).to(device)
    drug_optimizer = Adam(drugAE.parameters(), lr=drug_lr)
    drug_loss_fn = MSELoss(reduction='mean').to(device)
    drug_dataset = DrugDataset(drug_features_data)
    drug_feature_loader = DataLoader(drug_dataset, batch_size=drug_bz, shuffle=True)
    validation_loader = DataLoader(drug_dataset, batch_size=drug_bz)
    drug_es = EarlyStopping(patience=drug_patience)
    path = DrugAE_SaveBase + str(drug_outputdim) + ".pth"
    with open(DrugAE_Result, 'a') as file:
        file.write("---- start drugAE_" + str(drug_outputdim) + " train ----\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    if os.path.exists(path):
        print('---- start to load drugAE_' + str(drug_outputdim) + ' ----')
        drugAE.load_state_dict(torch.load(path))
        drug_es.best_loss = validate(drugAE, validation_loader, drug_num, drug_loss_fn)
        with open(DrugAE_Result, 'a') as file:
            file.write("---- Before loss:" + str(drug_es.best_loss) + "\n")
    # drug_train_loss = []
    print("---- start drugAE_" + str(drug_outputdim) + " train ----")
    for epoch in range(drug_epochs):
        print(f"Epoch {epoch + 1} of {drug_epochs}")
        if drug_es.early_stop:
            break
        train_epoch_loss = fit(
            drugAE, drug_feature_loader, drug_num, drug_optimizer, drug_loss_fn
        )
        # drug_train_loss.append(train_epoch_loss)
        validation_loss = validate(drugAE, validation_loader, drug_num, drug_loss_fn)
        drug_es(validation_loss, drugAE, path)
        print(f"Train Loss: {train_epoch_loss:.4f}")
        print(f"Validation Loss: {validation_loss:.4f}")
    print(f"Best Loss:{drug_es.best_loss:.4f}")
    with open(DrugAE_Result, 'a') as file:
        file.write("Best Loss:" + str(drug_es.best_loss) + "\n")

# cell line AE train
cell_line_features_data = pd.read_csv('data/cell_line_features.csv')
cell_line_num = cell_line_features_data.shape[0]
print("cell lines num:", cell_line_num)
cell_line_bz = 32
cell_line_lr = 0.0001
cell_line_epochs = 1500
cell_line_patience = 100

for cell_outputdim in CellAE_OutputDim_Optional:
    set_seed(1)
    cellLineAE = CellLineAE(output_dim=cell_outputdim).to(device)
    cell_line_optimizer = Adam(cellLineAE.parameters(), lr=cell_line_lr)
    cell_line_loss_fn = MSELoss(reduction='mean').to(device)
    cell_line_dataset = CellLineDataset(cell_line_features_data)
    cell_line_feature_loader = DataLoader(cell_line_dataset, batch_size=cell_line_bz, shuffle=True)
    validation_loader = DataLoader(cell_line_dataset, batch_size=cell_line_bz)
    cell_line_es = EarlyStopping(patience=cell_line_patience)
    path = CellAE_SaveBase + str(cell_outputdim) + ".pth"
    with open(CellLineAE_Result, 'a') as file:
        file.write("---- start cellLineAE_" + str(cell_outputdim) + ' train ----\n')
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    if os.path.exists(path):
        print('---- start to load cellLineAE_' + str(cell_outputdim) + ' ----')
        cellLineAE.load_state_dict(torch.load(path))
        cell_line_es.best_loss = validate(cellLineAE, validation_loader, cell_line_num, cell_line_loss_fn)
        with open(CellLineAE_Result, 'a') as file:
            file.write("---- Before loss:" + str(cell_line_es.best_loss) + "\n")
    # cell_line_train_loss = []
    print("---- start cellLineAE_" + str(cell_outputdim) + ' train ----')
    for epoch in range(cell_line_epochs):
        print(f"Epoch {epoch + 1} of {cell_line_epochs}")
        if cell_line_es.early_stop:
            break
        train_epoch_loss = fit(
            cellLineAE, cell_line_feature_loader, cell_line_num, cell_line_optimizer, cell_line_loss_fn
        )
        # cell_line_train_loss.append(train_epoch_loss)
        validation_loss = validate(cellLineAE, validation_loader, cell_line_num, cell_line_loss_fn)
        cell_line_es(validation_loss, cellLineAE, path)
        print(f"Train Loss: {train_epoch_loss:.4f}")
        print(f"Validation Loss: {validation_loss:.4f}")
    print(f"Best Loss:{cell_line_es.best_loss:.4f}")
    with open(CellLineAE_Result, 'a') as file:
        file.write("Best Loss:" + str(cell_line_es.best_loss) + "\n")
```

## File: GBM_LeaveCellOut.py
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
from sklearn.model_selection import GridSearchCV
import time
import random
from utils.tools import double_data, calculate

drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)
FILE_URL = "result/GBM_LeaveCellOut_result.txt"


class DataLoader:
    def __init__(self, drugs, cell_lines, summary, test_fold, syn_threshold=30):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.summary_test = self.summary.loc[self.summary['fold'] == test_fold]
        self.summary_train = self.summary.loc[self.summary['fold'] != test_fold]
        self.length_train = self.summary_train.shape[0]
        print("train:", self.length_train)
        self.length_test = self.summary_test.shape[0]
        print("test:", self.length_test)

    def syn_map(self, x):
        return 1 if x > self.syn_threshold else 0

    def get_samples(self, flag, method):
        if flag == 0:  # train data
            summary = self.summary_train
        else:  # test data
            summary = self.summary_test
        d1_idx = summary.iloc[:, 0]
        d2_idx = summary.iloc[:, 1]
        c_idx = summary.iloc[:, 2]
        d1 = np.array(self.drugs.iloc[d1_idx])
        d2 = np.array(self.drugs.iloc[d2_idx])
        c_exp = np.array(self.cell_lines.iloc[c_idx])
        X = np.concatenate((d1, d2, c_exp), axis=1)
        if method == 0:  # regression
            y = np.array(summary.iloc[:, 5])
        else:  # classification
            y = np.array(summary.iloc[:, 5].apply(lambda s: self.syn_map(s)))
        return X, y


Fold = 5

print("----------- Regression ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Regression ---------------------\n")
result_r = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 0)
    x_test, syn_true_value = sampelData.get_samples(1, 0)
    hyper_params = {'n_estimators': [128, 512, 1024], 'learning_rate': [0.1, 0.05, 0.01]}
    gbr = GradientBoostingRegressor(subsample=0.8, max_depth=25, min_samples_split=100, min_samples_leaf=20,
                                    max_features='sqrt', random_state=1)
    grid_cv = GridSearchCV(gbr, param_grid=hyper_params, scoring='neg_mean_squared_error', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_value = grid_cv.predict(x_test)
    n = sampelData.length_test // 2
    syn_true_value = syn_true_value[0:n]
    syn_pred_value = (syn_pred_value[0:n] + syn_pred_value[n:]) / 2
    syn_metrics = {}
    syn_metrics['MSE'] = mean_squared_error(syn_true_value, syn_pred_value)
    syn_metrics['RMSE'] = np.sqrt(syn_metrics['MSE'])
    syn_metrics["Pearsonr"] = pearsonr(syn_true_value, syn_pred_value)[0]
    result_r.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_r), "regression", Fold, FILE_URL)
```

## File: GBM_LeaveDrugOut.py
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
from sklearn.model_selection import GridSearchCV
import time
import random
from utils.tools import double_data, calculate

drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)
FILE_URL = "result/GBM_LeaveDrugOut_result.txt"


class DataLoader:
    def __init__(self, drugs, cell_lines, summary, test_fold, syn_threshold=30):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.summary_test = self.summary.loc[(self.summary['sen_fold_1'] == test_fold)|(self.summary['sen_fold_2']==test_fold)]
        self.summary_train = self.summary.loc[~self.summary.index.isin(self.summary_test.index)]
        self.length_train = self.summary_train.shape[0]
        print("train:", self.length_train)
        self.length_test = self.summary_test.shape[0]
        print("test:", self.length_test)

    def syn_map(self, x):
        return 1 if x > self.syn_threshold else 0

    def get_samples(self, flag, method):
        if flag == 0:  # train data
            summary = self.summary_train
        else:  # test data
            summary = self.summary_test
        d1_idx = summary.iloc[:, 0]
        d2_idx = summary.iloc[:, 1]
        c_idx = summary.iloc[:, 2]
        d1 = np.array(self.drugs.iloc[d1_idx])
        d2 = np.array(self.drugs.iloc[d2_idx])
        c_exp = np.array(self.cell_lines.iloc[c_idx])
        X = np.concatenate((d1, d2, c_exp), axis=1)
        if method == 0:  # regression
            y = np.array(summary.iloc[:, 5])
        else:  # classification
            y = np.array(summary.iloc[:, 5].apply(lambda s: self.syn_map(s)))
        return X, y


Fold = 5

print("----------- Regression ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Regression ---------------------\n")
result_r = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 0)
    x_test, syn_true_value = sampelData.get_samples(1, 0)
    hyper_params = {'n_estimators': [512, 1024], 'learning_rate': [0.1, 0.01]}
    gbr = GradientBoostingRegressor(subsample=0.8, max_depth=25, min_samples_split=100, min_samples_leaf=20,
                                    max_features='sqrt', random_state=1)
    grid_cv = GridSearchCV(gbr, param_grid=hyper_params, scoring='neg_mean_squared_error', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_value = grid_cv.predict(x_test)
    n = sampelData.length_test // 2
    syn_true_value = syn_true_value[0:n]
    syn_pred_value = (syn_pred_value[0:n] + syn_pred_value[n:]) / 2
    syn_metrics = {}
    syn_metrics['MSE'] = mean_squared_error(syn_true_value, syn_pred_value)
    syn_metrics['RMSE'] = np.sqrt(syn_metrics['MSE'])
    syn_metrics["Pearsonr"] = pearsonr(syn_true_value, syn_pred_value)[0]
    result_r.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_r), "regression", Fold, FILE_URL)
```

## File: GBMtrain.py
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, cohen_kappa_score, mean_squared_error
from scipy.stats import pearsonr
from sklearn.model_selection import GridSearchCV
import time
import random
from utils.tools import double_data, calculate

drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)
FILE_URL = "result/GBM_result.txt"


class DataLoader:
    def __init__(self, drugs, cell_lines, summary, test_fold, syn_threshold=30):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.summary_test = self.summary.loc[self.summary['syn_fold'] == test_fold]
        self.summary_train = self.summary.loc[self.summary['syn_fold'] != test_fold]
        self.length_train = self.summary_train.shape[0]
        print("train:", self.length_train)
        self.length_test = self.summary_test.shape[0]
        print("test:", self.length_test)

    def syn_map(self, x):
        return 1 if x > self.syn_threshold else 0

    def get_samples(self, flag, method):
        if flag == 0:  # train data
            summary = self.summary_train
        else:  # test data
            summary = self.summary_test
        d1_idx = summary.iloc[:, 0]
        d2_idx = summary.iloc[:, 1]
        c_idx = summary.iloc[:, 2]
        d1 = np.array(self.drugs.iloc[d1_idx])
        d2 = np.array(self.drugs.iloc[d2_idx])
        c_exp = np.array(self.cell_lines.iloc[c_idx])
        X = np.concatenate((d1, d2, c_exp), axis=1)
        if method == 0:  # regression
            y = np.array(summary.iloc[:, 5])
        else:  # classification
            y = np.array(summary.iloc[:, 5].apply(lambda s: self.syn_map(s)))
        return X, y


Fold = 5
print("----------- Classification ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Classification ---------------------\n")
result_c = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 1)
    x_test, syn_true_label = sampelData.get_samples(1, 1)
    hyper_params = {'n_estimators': [128, 512, 1024], 'learning_rate': [0.1, 0.05, 0.01]}
    gbc = GradientBoostingClassifier(subsample=0.8, max_depth=25, min_samples_split=100, min_samples_leaf=20,
                                     max_features='sqrt', random_state=1)
    grid_cv = GridSearchCV(gbc, param_grid=hyper_params, scoring='roc_auc', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_label = grid_cv.predict(x_test)
    syn_pred_prob = grid_cv.predict_proba(x_test)
    n = sampelData.length_test // 2
    syn_true_label = syn_true_label[0:n]
    syn_pred_label = syn_pred_label[0:n]
    syn_pred_prob = (syn_pred_prob[0:n, ] + syn_pred_prob[n:, ]) / 2
    syn_pred_prob = syn_pred_prob[:, 1]
    syn_prec, syn_recall, syn_threshold = precision_recall_curve(syn_true_label, syn_pred_prob)
    syn_TP = np.sum(np.logical_and(syn_pred_label, syn_true_label))
    syn_FP = np.sum(np.logical_and(syn_pred_label, np.logical_not(syn_true_label)))
    syn_TN = np.sum(np.logical_and(np.logical_not(syn_pred_label), np.logical_not(syn_true_label)))
    syn_FN = np.sum(np.logical_and(np.logical_not(syn_pred_label), syn_true_label))
    syn_metrics = {}
    syn_metrics["ROC AUC"] = roc_auc_score(syn_true_label, syn_pred_prob)
    syn_metrics["PR AUC"] = auc(syn_recall, syn_prec)
    syn_metrics["ACC"] = (syn_TP + syn_TN) / (syn_TP + syn_FP + syn_TN + syn_FN)
    syn_metrics["TPR"] = syn_TP / (syn_TP + syn_FN)
    syn_metrics["TNR"] = syn_TN / (syn_TN + syn_FP)
    syn_metrics["BACC"] = (syn_metrics["TPR"] + syn_metrics["TNR"]) / 2
    syn_metrics["PREC"] = syn_TP / (syn_TP + syn_FP)
    syn_metrics["Kappa"] = cohen_kappa_score(syn_true_label, syn_pred_label)
    result_c.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_c), "classification", Fold, FILE_URL)

print("----------- Regression ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Regression ---------------------\n")
result_r = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 0)
    x_test, syn_true_value = sampelData.get_samples(1, 0)
    hyper_params = {'n_estimators': [128, 512, 1024], 'learning_rate': [0.1, 0.05, 0.01]}
    gbr = GradientBoostingRegressor(subsample=0.8, max_depth=25, min_samples_split=100, min_samples_leaf=20,
                                    max_features='sqrt', random_state=1)
    grid_cv = GridSearchCV(gbr, param_grid=hyper_params, scoring='neg_mean_squared_error', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_value = grid_cv.predict(x_test)
    n = sampelData.length_test // 2
    syn_true_value = syn_true_value[0:n]
    syn_pred_value = (syn_pred_value[0:n] + syn_pred_value[n:]) / 2
    syn_metrics = {}
    syn_metrics['MSE'] = mean_squared_error(syn_true_value, syn_pred_value)
    syn_metrics['RMSE'] = np.sqrt(syn_metrics['MSE'])
    syn_metrics["Pearsonr"] = pearsonr(syn_true_value, syn_pred_value)[0]
    result_r.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_r), "regression", Fold, FILE_URL)
```

## File: MTLSynergy_LeaveCellOut.py
```python
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from torch.utils.data import DataLoader
from torch.optim import Adam
from Dataset import MTLSynergy_LeaveCellOutDataset
from torch.nn import MSELoss
import torch
import time
import pandas as pd
from utils.tools import EarlyStopping, set_seed, CategoricalCrossEntropyLoss
from static.constant import Fold, DrugAE_SaveBase, CellAE_SaveBase
from Models import MTLSynergy, DrugAE, CellLineAE
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, cohen_kappa_score, precision_score, \
    accuracy_score

MTLSyn_LeaveCellOut_SaveBase = "save/MTLSyn_LeaveCellOut/"
MTLSyn_LeaveCellOut_Result = "result/MTLSyn_LeaveCellOut_result.txt"
device = torch.device('cuda')

HYPERPARAMETERS = { # example
    'learning_rate': 0.0001,
    'batch_size': 256,
    'hidden_neurons': [4096, 2048, 2048, 1024],
}


def fit(model, drugEncoder, cellLineEncoder, train_dataloader, train_num, optimizer, mse, cce):
    model.train()
    train_running_loss1 = 0.0
    train_running_loss2 = 0.0
    train_running_loss3 = 0.0
    train_running_loss4 = 0.0
    for i, (x, y) in enumerate(train_dataloader):
        d1_features, d2_features, c_features = x
        d1_features = d1_features.float().to(device)
        d2_features = d2_features.float().to(device)
        c_features = c_features.float().to(device)
        y1, y2, y3, y4 = y
        y1 = y1.float().to(device)
        y3 = y3.long().to(device)
        y2 = y2.float().to(device)
        y4 = y4.long().to(device)
        d1_encoder = drugEncoder(d1_features)
        d2_encoder = drugEncoder(d2_features)
        c_encoder = cellLineEncoder(c_features)
        optimizer.zero_grad()
        out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
        loss1 = mse(out1, y1)
        loss3 = cce(out3, y3)
        loss2 = mse(out2, y2)
        loss4 = cce(out4, y4)
        num = d1_features.shape[0]
        train_running_loss1 += (loss1.item() * num)
        train_running_loss3 += (loss3.item() * num)
        train_running_loss2 += (loss2.item() * num)
        train_running_loss4 += (loss4.item() * num)
        loss = loss1 + loss2 + loss3 + loss4
        loss.backward()
        optimizer.step()
    train_loss1 = train_running_loss1 / train_num
    train_loss2 = train_running_loss2 / train_num
    train_loss3 = train_running_loss3 / train_num
    train_loss4 = train_running_loss4 / train_num
    train_loss_tol = train_loss1 + train_loss2 + train_loss3 + train_loss4
    print("train loss:" + str([train_loss_tol, train_loss1, train_loss2, train_loss3, train_loss4]))
    return [train_loss_tol, train_loss1, train_loss2, train_loss3, train_loss4]


def validate(model, drugEncoder, cellLineEncoder, validation_dataloader, validation_num, mse, cce):
    model.eval()
    validation_running_loss2 = 0.0
    validation_running_loss4 = 0.0
    y_true1 = torch.Tensor().to(device)
    y_pred1 = torch.Tensor().to(device)
    y_true3 = torch.Tensor().long().to(device)
    y_pred3 = torch.Tensor().to(device)
    with torch.no_grad():
        for i, (x, y) in enumerate(validation_dataloader):
            d1_features, d2_features, c_features = x
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y
            y1 = y1.float().to(device)
            y3 = y3.long().to(device)
            y_true1 = torch.cat((y_true1, y1), 0)
            y_true3 = torch.cat((y_true3, y3), 0)
            y2 = y2.float().to(device)
            y4 = y4.long().to(device)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred1 = torch.cat((y_pred1, out1), 0)
            y_pred3 = torch.cat((y_pred3, out3), 0)
            loss2 = mse(out2, y2)
            loss4 = cce(out4, y4)
            num = d1_features.shape[0]
            validation_running_loss2 += (loss2.item() * num)
            validation_running_loss4 += (loss4.item() * num)

        n = validation_num // 2
        y_pred1_mean = (y_pred1[0:n] + y_pred1[n:]) / 2
        y_pred3_mean = (y_pred3[0:n, ] + y_pred3[n:, ]) / 2
        validation_loss1 = mse(y_pred1_mean, y_true1[0:n]).item()
        validation_loss2 = validation_running_loss2 / validation_num
        validation_loss3 = cce(y_pred3_mean, y_true3[0:n]).item()
        validation_loss4 = validation_running_loss4 / validation_num
        validation_loss_tol = validation_loss1 + validation_loss2 + validation_loss3 + validation_loss4
        print("validation loss:" + str(
            [validation_loss_tol, validation_loss1, validation_loss2, validation_loss3, validation_loss4]))
        return [validation_loss_tol, validation_loss1, validation_loss2, validation_loss3, validation_loss4]


def test(model, drugEncoder, cellLineEncoder, test_dataloader, test_num, mse, cce):
    model.eval()
    y_true1 = torch.Tensor().to(device)
    y_pred1 = torch.Tensor().to(device)
    y_true2 = torch.Tensor().to(device)
    y_pred2 = torch.Tensor().to(device)
    y_true3 = torch.Tensor().long().to(device)
    y_pred3 = torch.Tensor().to(device)
    y_true4 = torch.Tensor().long().to(device)
    y_pred4 = torch.Tensor().to(device)
    with torch.no_grad():
        for i, (x, y) in enumerate(test_dataloader):
            d1_features, d2_features, c_features = x
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y
            y1 = y1.float().to(device)
            y3 = y3.long().to(device)
            y_true1 = torch.cat((y_true1, y1), 0)
            y_true3 = torch.cat((y_true3, y3), 0)
            y2 = y2.float().to(device)
            y4 = y4.long().to(device)
            y_true2 = torch.cat((y_true2, y2), 0)
            y_true4 = torch.cat((y_true4, y4), 0)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred1 = torch.cat((y_pred1, out1), 0)
            y_pred3 = torch.cat((y_pred3, out3), 0)
            y_pred2 = torch.cat((y_pred2, out2), 0)
            y_pred4 = torch.cat((y_pred4, out4), 0)
        n = test_num // 2
        y_true1 = y_true1[0:n]
        y_true3 = y_true3[0:n]
        y_pred1 = (y_pred1[0:n] + y_pred1[n:]) / 2
        y_pred3 = (y_pred3[0:n, ] + y_pred3[n:, ]) / 2
        test_loss1 = mse(y_pred1, y_true1).item()
        test_loss2 = mse(y_pred2, y_true2).item()
        synergy_result = {}
        sensitivity_result = {}
        synergy_result["MSE"] = test_loss1
        sensitivity_result["MSE"] = test_loss2
        synergy_result["RMSE"] = np.sqrt(test_loss1)
        sensitivity_result["RMSE"] = np.sqrt(test_loss2)
        y_true1 = y_true1.cpu()
        y_pred1 = y_pred1.cpu()
        y_true2 = y_true2.cpu()
        y_pred2 = y_pred2.cpu()
        synergy_result["Pearsonr"] = pearsonr(y_true1, y_pred1)[0]
        sensitivity_result["Pearsonr"] = pearsonr(y_true2, y_pred2)[0]
        synergy_result["CCE"] = cce(y_pred3, y_true3).item()
        sensitivity_result["CCE"] = cce(y_pred4, y_true4).item()
        y_true3 = y_true3.cpu()
        y_pred3 = y_pred3.cpu()
        y_true4 = y_true4.cpu()
        y_pred4 = y_pred4.cpu()
        y_pred3_prob = y_pred3[:, 1]
        y_pred4_prob = y_pred4[:, 1]
        synergy_result["ROC AUC"] = roc_auc_score(y_true3, y_pred3_prob)
        sensitivity_result["ROC AUC"] = roc_auc_score(y_true4, y_pred4_prob)
        y_pred3_label = y_pred3.argmax(axis=1)
        y_pred4_label = y_pred4.argmax(axis=1)
        y_pred3_prec, y_pred3_recall, y_pred3_threshold = precision_recall_curve(y_true3, y_pred3_prob)
        y_pred4_prec, y_pred4_recall, y_pred4_threshold = precision_recall_curve(y_true4, y_pred4_prob)
        synergy_result["PR AUC"] = auc(y_pred3_recall, y_pred3_prec)
        sensitivity_result["PR AUC"] = auc(y_pred4_recall, y_pred4_prec)
        synergy_result["ACC"] = accuracy_score(y_true3, y_pred3_label)
        sensitivity_result["ACC"] = accuracy_score(y_true4, y_pred4_label)
        synergy_result["PREC"] = precision_score(y_true3, y_pred3_label)
        sensitivity_result["PREC"] = precision_score(y_true4, y_pred4_label)
        synergy_result["Kappa"] = cohen_kappa_score(y_true3, y_pred3_label)
        sensitivity_result["Kappa"] = cohen_kappa_score(y_true4, y_pred4_label)
        print("test result:\n" + "Synergy:\n" + str(synergy_result) + "\nSensitivity:\n" + str(
            sensitivity_result) + "\n")
        with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
            file.write("---------- Test ----------\n")
            file.write("test result:\n" + "Synergy:\n" + str(synergy_result) + "\nSensitivity:\n" + str(
                sensitivity_result) + "\n")
        return [synergy_result, sensitivity_result]


def calculate(result, name):
    tol_result = {}
    keys = result[0].keys()
    for key in keys:
        tol_result[key] = []
    for i in range(Fold):
        for key in keys:
            tol_result[key].append(result[i][key])
    print(str(name) + " result :")
    with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
        file.write(str(name) + " result :\n")
    for key in keys:
        print(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]))
        with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
            file.write(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]) + "\n")


epochs = 500
patience = 100  # 50
mse = MSELoss(reduction='mean').to(device)
cce = CategoricalCrossEntropyLoss().to(device)
drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)

drug_output = 128
cell_output = 256
drugAE = DrugAE(output_dim=drug_output).to(device)
print('---- start to load drugAE ----')
drug_path = DrugAE_SaveBase + str(drug_output) + '.pth'
drugAE.load_state_dict(torch.load(drug_path))
drugAE.eval()
cell_path = CellAE_SaveBase + str(cell_output) + '.pth'
cellLineAE = CellLineAE(output_dim=cell_output).to(device)
print('---- start to load cellLineAE ----')
cellLineAE.load_state_dict(torch.load(cell_path))
cellLineAE.eval()
print("--------- MTL-Model with drugAE(" + str(drug_output) + ") cellLineAE(" + str(cell_output) + ") ---------")
with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
    file.write("--------- MTL-Model with drugAE(" + str(drug_output) + ") cellLineAE(" + str(
        cell_output) + ") ---------\n")
result_per_fold = []
model_input = drug_output + cell_output

for fold_test in range(0, Fold):
    print("----- Test Fold " + str(fold_test) + " -----")
    with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
        file.write("----- Test Fold " + str(fold_test) + " -----\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    set_seed(seed=1)
    test_summary = summary.loc[summary['fold'] == fold_test]
    train_val_summary = summary.loc[summary['fold']!=fold_test]
    validation_summary = train_val_summary.sample(frac=0.1, replace=False, random_state=1, axis=0)
    train_summary = train_val_summary.loc[~train_val_summary.index.isin(validation_summary.index)]
    train_dataset = MTLSynergy_LeaveCellOutDataset(drugs, cell_lines, train_summary)
    train_num = len(train_dataset)
    train_loader = DataLoader(train_dataset, batch_size=HYPERPARAMETERS['batch_size'], shuffle=True,
                              num_workers=2, pin_memory=True)
    validation_dataset = MTLSynergy_LeaveCellOutDataset(drugs, cell_lines, validation_summary)
    validation_num = len(validation_dataset)
    validation_loader = DataLoader(validation_dataset, batch_size=HYPERPARAMETERS['batch_size'],
                                   shuffle=False)  # no shuffle
    test_dataset = MTLSynergy_LeaveCellOutDataset(drugs, cell_lines, test_summary)
    test_num = len(test_dataset)
    test_loader = DataLoader(test_dataset, batch_size=HYPERPARAMETERS['batch_size'],
                             shuffle=False)  # no shuffle

    model = MTLSynergy(HYPERPARAMETERS['hidden_neurons'], model_input).to(device)
    model_es = EarlyStopping(patience=patience)
    optimizer = Adam(model.parameters(), lr=HYPERPARAMETERS['learning_rate'])
    train_loss = []
    validation_loss = []
    start_time = time.time()
    save_path = MTLSyn_LeaveCellOut_SaveBase + "fold_" + str(fold_test) + ".pth"
    for epoch in range(epochs):
        train_result = fit(model, drugAE.encoder, cellLineAE.encoder, train_loader, train_num, optimizer, mse, cce)
        train_loss.append(train_result)
        validation_result = validate(model, drugAE.encoder, cellLineAE.encoder, validation_loader, validation_num,
                                     mse, cce)
        validation_loss.append(validation_result)

        model_es(validation_result[0], model, save_path)
        if model_es.early_stop:
            with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
                file.write("When in epoch " + str(epoch - patience + 1) + ":\n")
                file.write("Validation loss:" + str(validation_loss[epoch - patience]) + "\n")
                file.write("Best loss:" + str(model_es.best_loss) + "\n")
            break

    model = MTLSynergy(HYPERPARAMETERS['hidden_neurons'], model_input).to(device)
    model.load_state_dict(torch.load(save_path))
    test_result = test(model, drugAE.encoder, cellLineAE.encoder, test_loader, test_num, mse, cce)
    result_per_fold.append(test_result)
result = np.array(result_per_fold)
with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
    file.write("------------------ Calculate ---------------\n")
calculate(result[:, 0], "Synergy")
calculate(result[:, 1], "Sensitivity")
with open(MTLSyn_LeaveCellOut_Result, 'a') as file:
    file.write("\n")
```

## File: MTLSynergy_LeaveDrugOut.py
```python
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from torch.utils.data import DataLoader
from torch.optim import Adam
from Dataset import MTLSynergyDataset
from torch.nn import MSELoss
import torch
import time
import pandas as pd
from utils.tools import EarlyStopping, set_seed, CategoricalCrossEntropyLoss, filter1
from static.constant import Fold, DrugAE_SaveBase, CellAE_SaveBase
from Models import MTLSynergy, DrugAE, CellLineAE
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, cohen_kappa_score, precision_score, \
    accuracy_score

MTLSyn_LeaveDrugOut_SaveBase = "save/MTLSyn_LeaveDrugOut/"
MTLSyn_LeaveDrugOut_Result = "result/MTLSyn_LeaveDrugOut_result.txt"
device = torch.device('cuda')

HYPERPARAMETERS = {  # example
    'learning_rate': 0.0001,
    'batch_size': 256,
    'hidden_neurons': [4096, 2048, 2048, 1024],
}


def fit(model, drugEncoder, cellLineEncoder, train_dataloader, train_num, optimizer, mse, cce, test_fold):
    model.train()
    train_running_loss1 = 0.0
    train_running_loss2 = 0.0
    train_running_loss3 = 0.0
    train_running_loss4 = 0.0
    count = 0
    for i, (x, y) in enumerate(train_dataloader):
        d1_features, d2_features, c_features, sen_fold = x
        d1_features = d1_features.float().to(device)
        d2_features = d2_features.float().to(device)
        c_features = c_features.float().to(device)
        y1, y2, y3, y4 = y
        y1 = y1.float().to(device)
        y3 = y3.long().to(device)
        d1_encoder = drugEncoder(d1_features)
        d2_encoder = drugEncoder(d2_features)
        c_encoder = cellLineEncoder(c_features)
        optimizer.zero_grad()
        out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
        loss1 = mse(out1, y1)
        loss3 = cce(out3, y3)
        num = d1_features.shape[0]
        train_running_loss1 += (loss1.item() * num)
        train_running_loss3 += (loss3.item() * num)

        x_filter, y_filter = filter1((x, y), test_fold)
        d1_features, d2_features, c_features = x_filter
        d1_features = d1_features.float().to(device)
        d2_features = d2_features.float().to(device)
        c_features = c_features.float().to(device)
        y1, y2, y3, y4 = y_filter
        y2 = y2.float().to(device)
        y4 = y4.long().to(device)
        d1_encoder = drugEncoder(d1_features)
        d2_encoder = drugEncoder(d2_features)
        c_encoder = cellLineEncoder(c_features)
        out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
        loss2 = mse(out2, y2)
        loss4 = cce(out4, y4)
        num = d1_features.shape[0]
        train_running_loss2 += (loss2.item() * num)
        train_running_loss4 += (loss4.item() * num)
        count += num
        loss = loss1 + loss2 + loss3 + loss4
        loss.backward()
        optimizer.step()
    train_loss1 = train_running_loss1 / train_num
    train_loss2 = train_running_loss2 / count
    train_loss3 = train_running_loss3 / train_num
    train_loss4 = train_running_loss4 / count
    train_loss_tol = train_loss1 + train_loss2 + train_loss3 + train_loss4
    print("train loss:" + str([train_loss_tol, train_loss1, train_loss2, train_loss3, train_loss4]))
    return [train_loss_tol, train_loss1, train_loss2, train_loss3, train_loss4]


def validate(model, drugEncoder, cellLineEncoder, validation_dataloader, validation_num, mse, cce):
    model.eval()
    validation_running_loss2 = 0.0
    validation_running_loss4 = 0.0
    y_true1 = torch.Tensor().to(device)
    y_pred1 = torch.Tensor().to(device)
    y_true3 = torch.Tensor().long().to(device)
    y_pred3 = torch.Tensor().to(device)
    with torch.no_grad():
        for i, (x, y) in enumerate(validation_dataloader):
            d1_features, d2_features, c_features, sen_fold = x
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y
            y1 = y1.float().to(device)
            y3 = y3.long().to(device)
            y_true1 = torch.cat((y_true1, y1), 0)
            y_true3 = torch.cat((y_true3, y3), 0)
            y2 = y2.float().to(device)
            y4 = y4.long().to(device)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred1 = torch.cat((y_pred1, out1), 0)
            y_pred3 = torch.cat((y_pred3, out3), 0)
            loss2 = mse(out2, y2)
            loss4 = cce(out4, y4)
            num = d1_features.shape[0]
            validation_running_loss2 += (loss2.item() * num)
            validation_running_loss4 += (loss4.item() * num)

        n = validation_num // 2
        y_pred1_mean = (y_pred1[0:n] + y_pred1[n:]) / 2
        y_pred3_mean = (y_pred3[0:n, ] + y_pred3[n:, ]) / 2
        validation_loss1 = mse(y_pred1_mean, y_true1[0:n]).item()
        validation_loss2 = validation_running_loss2 / validation_num
        validation_loss3 = cce(y_pred3_mean, y_true3[0:n]).item()
        validation_loss4 = validation_running_loss4 / validation_num
        validation_loss_tol = validation_loss1 + validation_loss2 + validation_loss3 + validation_loss4
        print("validation loss:" + str(
            [validation_loss_tol, validation_loss1, validation_loss2, validation_loss3, validation_loss4]))
        return [validation_loss_tol, validation_loss1, validation_loss2, validation_loss3, validation_loss4]


def test(model, drugEncoder, cellLineEncoder, test_dataloader, test_num, mse, cce, test_fold):
    model.eval()
    y_true1 = torch.Tensor().to(device)
    y_pred1 = torch.Tensor().to(device)
    y_true2 = torch.Tensor().to(device)
    y_pred2 = torch.Tensor().to(device)
    y_true3 = torch.Tensor().long().to(device)
    y_pred3 = torch.Tensor().to(device)
    y_true4 = torch.Tensor().long().to(device)
    y_pred4 = torch.Tensor().to(device)
    with torch.no_grad():
        for i, (x, y) in enumerate(test_dataloader):
            d1_features, d2_features, c_features, sen_fold = x
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y
            y1 = y1.float().to(device)
            y3 = y3.long().to(device)
            y_true1 = torch.cat((y_true1, y1), 0)
            y_true3 = torch.cat((y_true3, y3), 0)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred1 = torch.cat((y_pred1, out1), 0)
            y_pred3 = torch.cat((y_pred3, out3), 0)

            x_filter, y_filter = filter1((x, y), test_fold, flag=1)
            d1_features, d2_features, c_features = x_filter
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y_filter
            y2 = y2.float().to(device)
            y4 = y4.long().to(device)
            y_true2 = torch.cat((y_true2, y2), 0)
            y_true4 = torch.cat((y_true4, y4), 0)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred2 = torch.cat((y_pred2, out2), 0)
            y_pred4 = torch.cat((y_pred4, out4), 0)
        n = test_num // 2
        y_true1 = y_true1[0:n]
        y_true3 = y_true3[0:n]
        y_pred1 = (y_pred1[0:n] + y_pred1[n:]) / 2
        y_pred3 = (y_pred3[0:n, ] + y_pred3[n:, ]) / 2
        test_loss1 = mse(y_pred1, y_true1).item()
        test_loss2 = mse(y_pred2, y_true2).item()
        synergy_result = {}
        sensitivity_result = {}
        synergy_result["MSE"] = test_loss1
        sensitivity_result["MSE"] = test_loss2
        synergy_result["RMSE"] = np.sqrt(test_loss1)
        sensitivity_result["RMSE"] = np.sqrt(test_loss2)
        y_true1 = y_true1.cpu()
        y_pred1 = y_pred1.cpu()
        y_true2 = y_true2.cpu()
        y_pred2 = y_pred2.cpu()
        synergy_result["Pearsonr"] = pearsonr(y_true1, y_pred1)[0]
        sensitivity_result["Pearsonr"] = pearsonr(y_true2, y_pred2)[0]
        synergy_result["CCE"] = cce(y_pred3, y_true3).item()
        sensitivity_result["CCE"] = cce(y_pred4, y_true4).item()
        y_true3 = y_true3.cpu()
        y_pred3 = y_pred3.cpu()
        y_true4 = y_true4.cpu()
        y_pred4 = y_pred4.cpu()
        y_pred3_prob = y_pred3[:, 1]
        y_pred4_prob = y_pred4[:, 1]
        synergy_result["ROC AUC"] = roc_auc_score(y_true3, y_pred3_prob)
        sensitivity_result["ROC AUC"] = roc_auc_score(y_true4, y_pred4_prob)
        y_pred3_label = y_pred3.argmax(axis=1)
        y_pred4_label = y_pred4.argmax(axis=1)
        y_pred3_prec, y_pred3_recall, y_pred3_threshold = precision_recall_curve(y_true3, y_pred3_prob)
        y_pred4_prec, y_pred4_recall, y_pred4_threshold = precision_recall_curve(y_true4, y_pred4_prob)
        synergy_result["PR AUC"] = auc(y_pred3_recall, y_pred3_prec)
        sensitivity_result["PR AUC"] = auc(y_pred4_recall, y_pred4_prec)
        synergy_result["ACC"] = accuracy_score(y_true3, y_pred3_label)
        sensitivity_result["ACC"] = accuracy_score(y_true4, y_pred4_label)
        synergy_result["PREC"] = precision_score(y_true3, y_pred3_label)
        sensitivity_result["PREC"] = precision_score(y_true4, y_pred4_label)
        synergy_result["Kappa"] = cohen_kappa_score(y_true3, y_pred3_label)
        sensitivity_result["Kappa"] = cohen_kappa_score(y_true4, y_pred4_label)
        print("test result:\n" + "Synergy:\n" + str(synergy_result) + "\nSensitivity:\n" + str(
            sensitivity_result) + "\n")
        with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
            file.write("---------- Test ----------\n")
            file.write("test result:\n" + "Synergy:\n" + str(synergy_result) + "\nSensitivity:\n" + str(
                sensitivity_result) + "\n")
        return [synergy_result, sensitivity_result]


def calculate(result, name):
    tol_result = {}
    keys = result[0].keys()
    for key in keys:
        tol_result[key] = []
    for i in range(Fold):
        for key in keys:
            tol_result[key].append(result[i][key])
    print(str(name) + " result :")
    with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
        file.write(str(name) + " result :\n")
    for key in keys:
        print(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]))
        with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
            file.write(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]) + "\n")


epochs = 500
patience = 100  # 50
mse = MSELoss(reduction='mean').to(device)
cce = CategoricalCrossEntropyLoss().to(device)
drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)

drug_output = 128
cell_output = 256
drugAE = DrugAE(output_dim=drug_output).to(device)
print('---- start to load drugAE ----')
drug_path = DrugAE_SaveBase + str(drug_output) + '.pth'
drugAE.load_state_dict(torch.load(drug_path))
drugAE.eval()
cell_path = CellAE_SaveBase + str(cell_output) + '.pth'
cellLineAE = CellLineAE(output_dim=cell_output).to(device)
print('---- start to load cellLineAE ----')
cellLineAE.load_state_dict(torch.load(cell_path))
cellLineAE.eval()
print("--------- MTL-Model with drugAE(" + str(drug_output) + ") cellLineAE(" + str(cell_output) + ") ---------")
with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
    file.write("--------- MTL-Model with drugAE(" + str(drug_output) + ") cellLineAE(" + str(
        cell_output) + ") ---------\n")
result_per_fold = []
model_input = drug_output + cell_output

for fold_test in range(0, Fold):
    print("----- Test Fold " + str(fold_test) + " -----")
    with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
        file.write("----- Test Fold " + str(fold_test) + " -----\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    set_seed(seed=1)
    test_summary = summary.loc[(summary['sen_fold_1'] == fold_test) | (summary['sen_fold_2'] == fold_test)]
    train_val_summary = summary.loc[~summary.index.isin(test_summary.index)]
    validation_summary = train_val_summary.sample(frac=0.1, replace=False, random_state=1, axis=0)
    train_summary = train_val_summary.loc[~train_val_summary.index.isin(validation_summary.index)]
    train_dataset = MTLSynergyDataset(drugs, cell_lines, train_summary)
    train_num = len(train_dataset)
    train_loader = DataLoader(train_dataset, batch_size=HYPERPARAMETERS['batch_size'], shuffle=True,
                              num_workers=2, pin_memory=True)
    validation_dataset = MTLSynergyDataset(drugs, cell_lines, validation_summary)
    validation_num = len(validation_dataset)
    validation_loader = DataLoader(validation_dataset, batch_size=HYPERPARAMETERS['batch_size'],
                                   shuffle=False)  # no shuffle
    test_dataset = MTLSynergyDataset(drugs, cell_lines, test_summary)
    test_num = len(test_dataset)
    test_loader = DataLoader(test_dataset, batch_size=HYPERPARAMETERS['batch_size'],
                             shuffle=False)  # no shuffle

    model = MTLSynergy(HYPERPARAMETERS['hidden_neurons'], model_input).to(device)
    model_es = EarlyStopping(patience=patience)
    optimizer = Adam(model.parameters(), lr=HYPERPARAMETERS['learning_rate'])
    train_loss = []
    validation_loss = []
    start_time = time.time()
    save_path = MTLSyn_LeaveDrugOut_SaveBase + "fold_" + str(fold_test) + ".pth"
    for epoch in range(epochs):
        train_result = fit(model, drugAE.encoder, cellLineAE.encoder, train_loader, train_num, optimizer, mse, cce,
                           fold_test)
        train_loss.append(train_result)
        validation_result = validate(model, drugAE.encoder, cellLineAE.encoder, validation_loader, validation_num,
                                     mse, cce)
        validation_loss.append(validation_result)

        model_es(validation_result[0], model, save_path)
        if model_es.early_stop:
            with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
                file.write("When in epoch " + str(epoch - patience + 1) + ":\n")
                file.write("Validation loss:" + str(validation_loss[epoch - patience]) + "\n")
                file.write("Best loss:" + str(model_es.best_loss) + "\n")
            break

    model = MTLSynergy(HYPERPARAMETERS['hidden_neurons'], model_input).to(device)
    model.load_state_dict(torch.load(save_path))
    test_result = test(model, drugAE.encoder, cellLineAE.encoder, test_loader, test_num, mse, cce, fold_test)
    result_per_fold.append(test_result)
result = np.array(result_per_fold)
with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
    file.write("------------------ Calculate ---------------\n")
calculate(result[:, 0], "Synergy")
calculate(result[:, 1], "Sensitivity")
with open(MTLSyn_LeaveDrugOut_Result, 'a') as file:
    file.write("\n")
```

## File: RF_LeaveCellOut.py
```python
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import time
import random
from utils.tools import double_data, calculate

drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)
FILE_URL = "result/RF_LeaveCellOut_result.txt"


class DataLoader:
    def __init__(self, drugs, cell_lines, summary, test_fold, syn_threshold=30):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.summary_test = self.summary.loc[self.summary['fold'] == test_fold]
        self.summary_train = self.summary.loc[self.summary['fold'] != test_fold]
        self.length_train = self.summary_train.shape[0]
        print("train:", self.length_train)
        self.length_test = self.summary_test.shape[0]
        print("test:", self.length_test)

    def syn_map(self, x):
        return 1 if x > self.syn_threshold else 0

    def get_samples(self, flag, method):
        if flag == 0:  # train data
            summary = self.summary_train
        else:  # test data
            summary = self.summary_test
        d1_idx = summary.iloc[:, 0]
        d2_idx = summary.iloc[:, 1]
        c_idx = summary.iloc[:, 2]
        d1 = np.array(self.drugs.iloc[d1_idx])
        d2 = np.array(self.drugs.iloc[d2_idx])
        c_exp = np.array(self.cell_lines.iloc[c_idx])
        X = np.concatenate((d1, d2, c_exp), axis=1)
        if method == 0:  # regression
            y = np.array(summary.iloc[:, 5])
        else:  # classification
            y = np.array(summary.iloc[:, 5].apply(lambda s: self.syn_map(s)))
        return X, y


Fold = 5
print("----------- Regression ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Regression ---------------------\n")
result_r = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 0)
    x_test, syn_true_value = sampelData.get_samples(1, 0)
    hyper_params = {'n_estimators': [128, 512, 1024], 'max_features': ['sqrt', 256, 512]}
    gbr = RandomForestRegressor(max_depth=20, min_samples_split=100, min_samples_leaf=20, random_state=1)
    grid_cv = GridSearchCV(gbr, param_grid=hyper_params, scoring='neg_mean_squared_error', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_value = grid_cv.predict(x_test)
    n = sampelData.length_test // 2
    syn_true_value = syn_true_value[0:n]
    syn_pred_value = (syn_pred_value[0:n] + syn_pred_value[n:]) / 2
    syn_metrics = {}
    syn_metrics['MSE'] = mean_squared_error(syn_true_value, syn_pred_value)
    syn_metrics['RMSE'] = np.sqrt(syn_metrics['MSE'])
    syn_metrics["Pearsonr"] = pearsonr(syn_true_value, syn_pred_value)[0]
    result_r.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_r), "regression", Fold, FILE_URL)
```

## File: RF_LeaveDrugOut.py
```python
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import time
import random
from utils.tools import double_data, calculate

drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)
FILE_URL = "result/RF_LeaveDrugOut_result.txt"


class DataLoader:
    def __init__(self, drugs, cell_lines, summary, test_fold, syn_threshold=30):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.summary_test = self.summary.loc[(self.summary['sen_fold_1'] == test_fold) | (self.summary['sen_fold_2'] == test_fold)]
        self.summary_train = self.summary.loc[~self.summary.index.isin(self.summary_test.index)]
        self.length_train = self.summary_train.shape[0]
        print("train:", self.length_train)
        self.length_test = self.summary_test.shape[0]
        print("test:", self.length_test)

    def syn_map(self, x):
        return 1 if x > self.syn_threshold else 0

    def get_samples(self, flag, method):
        if flag == 0:  # train data
            summary = self.summary_train
        else:  # test data
            summary = self.summary_test
        d1_idx = summary.iloc[:, 0]
        d2_idx = summary.iloc[:, 1]
        c_idx = summary.iloc[:, 2]
        d1 = np.array(self.drugs.iloc[d1_idx])
        d2 = np.array(self.drugs.iloc[d2_idx])
        c_exp = np.array(self.cell_lines.iloc[c_idx])
        X = np.concatenate((d1, d2, c_exp), axis=1)
        if method == 0:  # regression
            y = np.array(summary.iloc[:, 5])
        else:  # classification
            y = np.array(summary.iloc[:, 5].apply(lambda s: self.syn_map(s)))
        return X, y


Fold = 5
print("----------- Regression ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Regression ---------------------\n")
result_r = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 0)
    x_test, syn_true_value = sampelData.get_samples(1, 0)
    hyper_params = {'n_estimators': [512, 1024], 'max_features': ['sqrt', 256]}
    gbr = RandomForestRegressor(max_depth=20, min_samples_split=100, min_samples_leaf=20, random_state=1)
    grid_cv = GridSearchCV(gbr, param_grid=hyper_params, scoring='neg_mean_squared_error', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_value = grid_cv.predict(x_test)
    n = sampelData.length_test // 2
    syn_true_value = syn_true_value[0:n]
    syn_pred_value = (syn_pred_value[0:n] + syn_pred_value[n:]) / 2
    syn_metrics = {}
    syn_metrics['MSE'] = mean_squared_error(syn_true_value, syn_pred_value)
    syn_metrics['RMSE'] = np.sqrt(syn_metrics['MSE'])
    syn_metrics["Pearsonr"] = pearsonr(syn_true_value, syn_pred_value)[0]
    result_r.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_r), "regression", Fold, FILE_URL)
```

## File: RFtrain.py
```python
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, cohen_kappa_score, mean_squared_error
import time
import random
from utils.tools import double_data, calculate

drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)
FILE_URL = "result/RF_result.txt"


class DataLoader:
    def __init__(self, drugs, cell_lines, summary, test_fold, syn_threshold=30):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.summary_test = self.summary.loc[self.summary['syn_fold'] == test_fold]
        self.summary_train = self.summary.loc[self.summary['syn_fold'] != test_fold]
        self.length_train = self.summary_train.shape[0]
        print("train:", self.length_train)
        self.length_test = self.summary_test.shape[0]
        print("test:", self.length_test)

    def syn_map(self, x):
        return 1 if x > self.syn_threshold else 0

    def get_samples(self, flag, method):
        if flag == 0:  # train data
            summary = self.summary_train
        else:  # test data
            summary = self.summary_test
        d1_idx = summary.iloc[:, 0]
        d2_idx = summary.iloc[:, 1]
        c_idx = summary.iloc[:, 2]
        d1 = np.array(self.drugs.iloc[d1_idx])
        d2 = np.array(self.drugs.iloc[d2_idx])
        c_exp = np.array(self.cell_lines.iloc[c_idx])
        X = np.concatenate((d1, d2, c_exp), axis=1)
        if method == 0:  # regression
            y = np.array(summary.iloc[:, 5])
        else:  # classification
            y = np.array(summary.iloc[:, 5].apply(lambda s: self.syn_map(s)))
        return X, y


Fold = 5
print("----------- Classification ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Classification ---------------------\n")
result_c = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 1)
    x_test, syn_true_label = sampelData.get_samples(1, 1)
    hyper_params = {'n_estimators': [128, 512, 1024], 'max_features': ['sqrt', 256, 512]}
    gbc = RandomForestClassifier(max_depth=20, min_samples_split=100, min_samples_leaf=20, random_state=1,
                                 class_weight={0: 1, 1: 5})
    grid_cv = GridSearchCV(gbc, param_grid=hyper_params, scoring='roc_auc', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_label = grid_cv.predict(x_test)
    syn_pred_prob = grid_cv.predict_proba(x_test)
    n = sampelData.length_test // 2
    syn_true_label = syn_true_label[0:n]
    syn_pred_label = syn_pred_label[0:n]
    syn_pred_prob = (syn_pred_prob[0:n, ] + syn_pred_prob[n:, ]) / 2
    syn_pred_prob = syn_pred_prob[:, 1]
    syn_prec, syn_recall, syn_threshold = precision_recall_curve(syn_true_label, syn_pred_prob)
    syn_TP = np.sum(np.logical_and(syn_pred_label, syn_true_label))
    syn_FP = np.sum(np.logical_and(syn_pred_label, np.logical_not(syn_true_label)))
    syn_TN = np.sum(np.logical_and(np.logical_not(syn_pred_label), np.logical_not(syn_true_label)))
    syn_FN = np.sum(np.logical_and(np.logical_not(syn_pred_label), syn_true_label))
    syn_metrics = {}
    syn_metrics["ROC AUC"] = roc_auc_score(syn_true_label, syn_pred_prob)
    syn_metrics["PR AUC"] = auc(syn_recall, syn_prec)
    syn_metrics["ACC"] = (syn_TP + syn_TN) / (syn_TP + syn_FP + syn_TN + syn_FN)
    syn_metrics["TPR"] = syn_TP / (syn_TP + syn_FN)
    syn_metrics["TNR"] = syn_TN / (syn_TN + syn_FP)
    syn_metrics["BACC"] = (syn_metrics["TPR"] + syn_metrics["TNR"]) / 2
    syn_metrics["PREC"] = syn_TP / (syn_TP + syn_FP)
    syn_metrics["Kappa"] = cohen_kappa_score(syn_true_label, syn_pred_label)
    result_c.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_c), "classification", Fold, FILE_URL)

print("----------- Regression ----------")
with open(FILE_URL, 'a') as file:
    file.write("---------------------- Regression ---------------------\n")
result_r = []
for fold_test in range(0, Fold):
    print("---------- Test Fold " + str(fold_test) + " ----------")
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    random.seed(1)
    np.random.seed(1)
    with open(FILE_URL, 'a') as file:
        file.write("---------- Test Fold " + str(fold_test) + " ----------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    sampelData = DataLoader(drugs, cell_lines, summary, test_fold=fold_test)
    x_train, y_train = sampelData.get_samples(0, 0)
    x_test, syn_true_value = sampelData.get_samples(1, 0)
    hyper_params = {'n_estimators': [128, 512, 1024], 'max_features': ['sqrt', 256, 512]}
    gbr = RandomForestRegressor(max_depth=20, min_samples_split=100, min_samples_leaf=20, random_state=1)
    grid_cv = GridSearchCV(gbr, param_grid=hyper_params, scoring='neg_mean_squared_error', verbose=10, cv=4)

    grid_cv.fit(x_train, y_train)
    syn_pred_value = grid_cv.predict(x_test)
    n = sampelData.length_test // 2
    syn_true_value = syn_true_value[0:n]
    syn_pred_value = (syn_pred_value[0:n] + syn_pred_value[n:]) / 2
    syn_metrics = {}
    syn_metrics['MSE'] = mean_squared_error(syn_true_value, syn_pred_value)
    syn_metrics['RMSE'] = np.sqrt(syn_metrics['MSE'])
    syn_metrics["Pearsonr"] = pearsonr(syn_true_value, syn_pred_value)[0]
    result_r.append(syn_metrics)
    print("syn_metrics:", syn_metrics)
    with open(FILE_URL, 'a') as file:
        file.write("syn_metrics:" + str(syn_metrics) + "\n")
calculate(np.array(result_r), "regression", Fold, FILE_URL)
```

## File: static/constant.py
```python
Fold = 5
DrugAE_InputDim = 1213
CELLAE_InputDim = 5000
DrugAE_OutputDim = 128
CellAE_OutputDim = 256
DrugAE_OutputDim_Optional = [32, 64, 128, 256, 512]
CellAE_OutputDim_Optional = [128, 256, 512, 1024, 2048]
DrugAE_SaveBase = "save/AutoEncoder/DrugAE_"
CellAE_SaveBase = "save/AutoEncoder/CellLineAE_"
DrugAE_Result = "result/DrugAE_result.txt"
CellLineAE_Result = "result/CellLineAE_result.txt"
MTLSA_SaveBase = "save/MTLSA/"
MTLSA_Result = "result/MTLSA_result.txt"
MTLSynergy_SaveBase = "save/MTLSynergy/"
MTLSynergy_Result = "result/MTLSynergy_result.txt"
MTLSynergy_InputDim = 384
```

## File: utils/tools.py
```python
import torch
import torch.nn.functional as F
import random
import numpy as np
import os
import pandas as pd


class EarlyStopping():
    def __init__(self, patience, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss, model, save_path):
        if self.best_loss == None:
            self.best_loss = val_loss
            torch.save(model.state_dict(), save_path)
        elif self.best_loss - val_loss > self.min_delta:
            self.best_loss = val_loss
            # reset counter if validation loss improves
            self.counter = 0
            # save weights
            torch.save(model.state_dict(), save_path)
        elif self.best_loss - val_loss < self.min_delta:
            self.counter += 1
            print(f"INFO: Early stopping counter {self.counter} of {self.patience}")
            if self.counter >= self.patience:
                print('INFO: Early stopping')
                self.early_stop = True


def set_seed(seed=1):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)  # set random seed for CPU
    torch.cuda.manual_seed(seed)  # set random seed for GPU


def double_data(data):
    double_summary = pd.DataFrame()
    double_summary['drug_row_idx'] = data['drug_col_idx']
    double_summary['drug_col_idx'] = data['drug_row_idx']
    double_summary['cell_line_idx'] = data['cell_line_idx']
    double_summary['ri_row'] = data['ri_col']
    double_summary['ri_col'] = data['ri_row']
    double_summary['synergy_loewe'] = data['synergy_loewe']
    double_summary['syn_fold'] = data['syn_fold']
    double_summary['sen_fold_1'] = data['sen_fold_2']
    double_summary['sen_fold_2'] = data['sen_fold_1']
    result = pd.concat([data, double_summary], axis=0)
    return result


def init_weights(modules):
    for n, m in modules.items():
        if isinstance(m, torch.nn.Sequential):
            for layer in m:
                if isinstance(layer, torch.nn.Linear):
                    torch.nn.init.xavier_uniform_(layer.weight, 1.0)
                    torch.nn.init.constant_(layer.bias, 0.0)
        elif isinstance(m, torch.nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight, 1.0)
            torch.nn.init.constant_(m.bias, 0.0)


def filter1(data, fold_test, flag=0):
    x, y = data
    d1_features, d2_features, c_features, sen_fold = x
    y1, y2, y3, y4 = y
    if flag == 0:
        remain = np.where(sen_fold != fold_test)
    else:
        remain = np.where(sen_fold == fold_test)
    return (d1_features[remain], d2_features[remain], c_features[remain]), (
        y1[remain], y2[remain], y3[remain], y4[remain])


def filter2(data, fold_test, flag=0):
    x, y = data
    d1_features, d2_features, c_features, sen_fold = x
    y1, y2 = y
    if flag == 0:
        remain = np.where(sen_fold != fold_test)
    else:
        remain = np.where(sen_fold == fold_test)
    return (d1_features[remain], d2_features[remain], c_features[remain]), (y1[remain], y2[remain])


def score_classification(x, threshold):
    return 1 if x > threshold else 0


def calculate(result, name, fold_num, save_path):
    tol_result = {}
    keys = result[0].keys()
    for key in keys:
        tol_result[key] = []
    for i in range(fold_num):
        for key in keys:
            tol_result[key].append(result[i][key])
    print(str(name) + " result :")
    with open(save_path, 'a') as file:
        file.write(str(name) + " result :\n")
    for key in keys:
        print(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]))
        with open(save_path, 'a') as file:
            file.write(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]) + "\n")



class CategoricalCrossEntropyLoss(torch.nn.Module):
    def __init__(self):
        super(CategoricalCrossEntropyLoss, self).__init__()

    def forward(self, y_pred, y_true):
        y_true = F.one_hot(y_true, y_pred.shape[1])
        y_pred = torch.clamp(y_pred, 1e-9, 1.0)
        tol_loss = -torch.sum(y_true * torch.log(y_pred), dim=1)
        loss = torch.mean(tol_loss, dim=0)
        return loss
```

## File: Dataset.py
```python
from torch.utils.data import Dataset
import numpy as np
from utils.tools import double_data, score_classification


class DrugDataset(Dataset):
    def __init__(self, drug_features):
        self.drug_features = drug_features

    def __len__(self):
        return self.drug_features.shape[0]

    def __getitem__(self, idx):
        drug_item = np.array(self.drug_features.iloc[idx])
        return drug_item, drug_item


class CellLineDataset(Dataset):
    def __init__(self, cell_line_features):
        self.cell_line_features = cell_line_features

    def __len__(self):
        return self.cell_line_features.shape[0]

    def __getitem__(self, idx):
        cell_line_item = np.array(self.cell_line_features.iloc[idx])
        return cell_line_item, cell_line_item


class MTLSynergyDataset(Dataset):
    def __init__(self, drugs, cell_lines, summary, syn_threshold=30, ri_threshold=50):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.ri_threshold = ri_threshold

    def __len__(self):
        return self.summary.shape[0]

    def __getitem__(self, idx):
        data = self.summary.iloc[idx]
        d1_idx, d2_idx, c_idx, d1_ri, d2_ri, syn, syn_fold, sen_fold_1, sen_fold_2 = data
        d1 = np.array(self.drugs.iloc[int(d1_idx)])
        d2 = np.array(self.drugs.iloc[int(d2_idx)])
        c_exp = np.array(self.cell_lines.iloc[int(c_idx)])
        syn_label = np.array(score_classification(syn, self.syn_threshold))
        d1_label = np.array(score_classification(d1_ri, self.ri_threshold))
        return (d1, d2, c_exp, np.array(sen_fold_1)), (np.array(syn), np.array(d1_ri), syn_label, d1_label)


class MTLSynergy_LeaveCellOutDataset(Dataset):
    def __init__(self, drugs, cell_lines, summary, syn_threshold=30, ri_threshold=50):
        self.drugs = drugs
        self.cell_lines = cell_lines
        self.summary = double_data(summary)
        self.syn_threshold = syn_threshold
        self.ri_threshold = ri_threshold

    def __len__(self):
        return self.summary.shape[0]

    def __getitem__(self, idx):
        data = self.summary.iloc[idx]
        d1_idx, d2_idx, c_idx, d1_ri, d2_ri, syn, syn_fold, sen_fold_1, sen_fold_2,fold = data
        d1 = np.array(self.drugs.iloc[int(d1_idx)])
        d2 = np.array(self.drugs.iloc[int(d2_idx)])
        c_exp = np.array(self.cell_lines.iloc[int(c_idx)])
        syn_label = np.array(score_classification(syn, self.syn_threshold))
        d1_label = np.array(score_classification(d1_ri, self.ri_threshold))
        return (d1, d2, c_exp), (np.array(syn), np.array(d1_ri), syn_label, d1_label)
```

## File: Models.py
```python
import torch
from torch.nn import Module, Sequential, Linear, ReLU, BatchNorm1d, Dropout, Softmax
from static.constant import DrugAE_InputDim, DrugAE_OutputDim, CELLAE_InputDim, CellAE_OutputDim, MTLSynergy_InputDim
from utils.tools import init_weights


class DrugAE(Module):
    def __init__(self, input_dim=DrugAE_InputDim, output_dim=DrugAE_OutputDim):
        super(DrugAE, self).__init__()
        if output_dim == 32 or output_dim == 64:
            hidden_dim = 256
        elif output_dim == 128 or output_dim == 256:
            hidden_dim = 512
        else:
            hidden_dim = 1024
        self.encoder = Sequential(
            Linear(input_dim, hidden_dim),
            ReLU(True),
            Dropout(0.5),
            Linear(hidden_dim, output_dim),
        )
        self.decoder = Sequential(
            Linear(output_dim, hidden_dim),
            ReLU(True),
            Linear(hidden_dim, input_dim),
        )
        init_weights(self._modules)

    def forward(self, input):
        x = self.encoder(input)
        y = self.decoder(x)
        return y


class CellLineAE(Module):
    def __init__(self, input_dim=CELLAE_InputDim, output_dim=CellAE_OutputDim):
        super(CellLineAE, self).__init__()
        if output_dim == 128 or output_dim == 256:
            hidden_dim = 512
        elif output_dim == 512:
            hidden_dim = 1024
        else:
            hidden_dim = 4096
        self.encoder = Sequential(
            Linear(input_dim, hidden_dim),
            ReLU(True),
            Dropout(0.5),
            Linear(hidden_dim, output_dim),
        )
        self.decoder = Sequential(
            Linear(output_dim, hidden_dim),
            ReLU(True),
            Linear(hidden_dim, input_dim)
        )
        init_weights(self._modules)

    def forward(self, input):
        x = self.encoder(input)
        y = self.decoder(x)
        return y


class MTLSynergy(Module):
    def __init__(self, hidden_neurons, input_dim=MTLSynergy_InputDim):
        super(MTLSynergy, self).__init__() 
        self.drug_cell_line_layer = Sequential(
            Linear(input_dim, hidden_neurons[0]),
            BatchNorm1d(hidden_neurons[0]),
            ReLU(True),
            Linear(hidden_neurons[0], hidden_neurons[1]),
            ReLU(True)
        )
        self.synergy_layer = Sequential(
            Linear(2 * hidden_neurons[1], hidden_neurons[2]),
            ReLU(True),
            Dropout(0.5),
            Linear(hidden_neurons[2], 128),
            ReLU(True)
        )
        self.sensitivity_layer = Sequential(
            Linear(hidden_neurons[1], hidden_neurons[3]),
            ReLU(True),
            Dropout(0.5),
            Linear(hidden_neurons[3], 64),
            ReLU(True)
        )
        self.synergy_out_1 = Linear(128, 1)
        self.synergy_out_2 = Sequential(Linear(128, 2), Softmax(dim=1))
        self.sensitivity_out_1 = Linear(64, 1)
        self.sensitivity_out_2 = Sequential(Linear(64, 2), Softmax(dim=1))
        init_weights(self._modules)

    def forward(self, d1, d2, c_exp):
        d1_c = self.drug_cell_line_layer(torch.cat((d1, c_exp), 1))
        d2_c = self.drug_cell_line_layer(torch.cat((d2, c_exp), 1))
        d1_sen = self.sensitivity_layer(d1_c)
        syn = self.synergy_layer(torch.cat((d1_c, d2_c), 1))
        syn_out_1 = self.synergy_out_1(syn)
        syn_out_2 = self.synergy_out_2(syn)
        d1_sen_out_1 = self.sensitivity_out_1(d1_sen)
        d1_sen_out_2 = self.sensitivity_out_2(d1_sen)
        return syn_out_1.squeeze(-1), d1_sen_out_1.squeeze(-1), syn_out_2, d1_sen_out_2
```

## File: MTLSynergytrain.py
```python
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from torch.utils.data import DataLoader
from torch.optim import Adam
from Dataset import MTLSynergyDataset
from torch.nn import MSELoss
import torch
import time
import pandas as pd
from utils.tools import EarlyStopping, set_seed, filter1, CategoricalCrossEntropyLoss
from static.constant import Fold, DrugAE_SaveBase, CellAE_SaveBase, MTLSynergy_SaveBase, MTLSynergy_Result,DrugAE_OutputDim,CellAE_OutputDim
from Models import MTLSynergy, DrugAE, CellLineAE
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, cohen_kappa_score, precision_score, \
    accuracy_score

device = torch.device('cuda')



hyper_parameters_candidate = [ # example
    {
        'learning_rate': 0.0001,
        'hidden_neurons': [8192, 4096, 4096, 2048]
    },
    {
        'learning_rate': 0.0001,
        'hidden_neurons': [4096, 2048, 2048, 1024]
    },
]


def fit(model, drugEncoder, cellLineEncoder, train_dataloader, optimizer, mse, cce, test_fold):
    # print('--- MTL-Synergy Training ---')
    model.train()
    train_running_loss1 = 0.0
    train_running_loss2 = 0.0
    train_running_loss3 = 0.0
    train_running_loss4 = 0.0
    cnt = 0
    count = 0
    for i, (x, y) in enumerate(train_dataloader):
        d1_features, d2_features, c_features, sen_fold = x
        d1_features = d1_features.float().to(device)
        d2_features = d2_features.float().to(device)
        c_features = c_features.float().to(device)
        y1, y2, y3, y4 = y
        y1 = y1.float().to(device)
        y3 = y3.long().to(device)
        d1_encoder = drugEncoder(d1_features)
        d2_encoder = drugEncoder(d2_features)
        c_encoder = cellLineEncoder(c_features)
        optimizer.zero_grad()
        out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
        loss1 = mse(out1, y1)
        loss3 = cce(out3, y3)
        num = d1_features.shape[0]
        cnt += num
        train_running_loss1 += (loss1.item() * num)
        train_running_loss3 += (loss3.item() * num)

        x_filter, y_filter = filter1((x, y), test_fold)
        d1_features, d2_features, c_features = x_filter
        d1_features = d1_features.float().to(device)
        d2_features = d2_features.float().to(device)
        c_features = c_features.float().to(device)
        y1, y2, y3, y4 = y_filter
        y2 = y2.float().to(device)
        y4 = y4.long().to(device)
        d1_encoder = drugEncoder(d1_features)
        d2_encoder = drugEncoder(d2_features)
        c_encoder = cellLineEncoder(c_features)
        out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
        loss2 = mse(out2, y2)
        loss4 = cce(out4, y4)
        num = d1_features.shape[0]
        train_running_loss2 += (loss2.item() * num)
        train_running_loss4 += (loss4.item() * num)
        count += num
        loss = loss1 + loss2 + loss3 + loss4
        loss.backward()
        optimizer.step()
    train_loss1 = train_running_loss1 / cnt
    train_loss2 = train_running_loss2 / count
    train_loss3 = train_running_loss3 / cnt
    train_loss4 = train_running_loss4 / count
    train_loss_tol = train_loss1 + train_loss2 + train_loss3 + train_loss4
    print("train loss:" + str([train_loss_tol, train_loss1, train_loss2, train_loss3, train_loss4]))
    return [train_loss_tol, train_loss1, train_loss2, train_loss3, train_loss4]


def validate(model, drugEncoder, cellLineEncoder, validation_dataloader, validation_num, mse, cce):
    # print('--- MTL-Synergy Validating ---')
    model.eval()
    validation_running_loss2 = 0.0
    validation_running_loss4 = 0.0
    y_true1 = torch.Tensor().to(device)
    y_pred1 = torch.Tensor().to(device)
    y_true3 = torch.Tensor().long().to(device)
    y_pred3 = torch.Tensor().to(device)
    with torch.no_grad():
        for i, (x, y) in enumerate(validation_dataloader):
            d1_features, d2_features, c_features, sen_fold = x
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y
            y1 = y1.float().to(device)
            y3 = y3.long().to(device)
            y_true1 = torch.cat((y_true1, y1), 0)
            y_true3 = torch.cat((y_true3, y3), 0)
            y2 = y2.float().to(device)
            y4 = y4.long().to(device)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred1 = torch.cat((y_pred1, out1), 0)
            y_pred3 = torch.cat((y_pred3, out3), 0)
            loss2 = mse(out2, y2)
            loss4 = cce(out4, y4)
            num = d1_features.shape[0]
            validation_running_loss2 += (loss2.item() * num)
            validation_running_loss4 += (loss4.item() * num)

        n = validation_num // 2
        y_pred1_mean = (y_pred1[0:n] + y_pred1[n:]) / 2
        y_pred3_mean = (y_pred3[0:n, ] + y_pred3[n:, ]) / 2
        validation_loss1 = mse(y_pred1_mean, y_true1[0:n]).item()
        validation_loss2 = validation_running_loss2 / validation_num
        validation_loss3 = cce(y_pred3_mean, y_true3[0:n]).item()
        validation_loss4 = validation_running_loss4 / validation_num
        validation_loss_tol = validation_loss1 + validation_loss2 + validation_loss3 + validation_loss4
        print("validation loss:" + str(
            [validation_loss_tol, validation_loss1, validation_loss2, validation_loss3, validation_loss4]))
        return [validation_loss_tol, validation_loss1, validation_loss2, validation_loss3, validation_loss4]


def test(model, drugEncoder, cellLineEncoder, test_dataloader, test_num, mse, cce, test_fold):
    # print('--- MTL-Synergy Testing ---')
    model.eval()
    y_true1 = torch.Tensor().to(device)
    y_pred1 = torch.Tensor().to(device)
    y_true2 = torch.Tensor().to(device)
    y_pred2 = torch.Tensor().to(device)
    y_true3 = torch.Tensor().long().to(device)
    y_pred3 = torch.Tensor().to(device)
    y_true4 = torch.Tensor().long().to(device)
    y_pred4 = torch.Tensor().to(device)
    with torch.no_grad():
        for i, (x, y) in enumerate(test_dataloader):
            d1_features, d2_features, c_features, sen_fold = x
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y
            y1 = y1.float().to(device)
            y3 = y3.long().to(device)
            y_true1 = torch.cat((y_true1, y1), 0)
            y_true3 = torch.cat((y_true3, y3), 0)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred1 = torch.cat((y_pred1, out1), 0)
            y_pred3 = torch.cat((y_pred3, out3), 0)

            x_filter, y_filter = filter1((x, y), test_fold, flag=1)
            d1_features, d2_features, c_features = x_filter
            d1_features = d1_features.float().to(device)
            d2_features = d2_features.float().to(device)
            c_features = c_features.float().to(device)
            y1, y2, y3, y4 = y_filter
            y2 = y2.float().to(device)
            y4 = y4.long().to(device)
            y_true2 = torch.cat((y_true2, y2), 0)
            y_true4 = torch.cat((y_true4, y4), 0)
            d1_encoder = drugEncoder(d1_features)
            d2_encoder = drugEncoder(d2_features)
            c_encoder = cellLineEncoder(c_features)
            out1, out2, out3, out4 = model(d1_encoder, d2_encoder, c_encoder)
            y_pred2 = torch.cat((y_pred2, out2), 0)
            y_pred4 = torch.cat((y_pred4, out4), 0)
        n = test_num // 2
        y_true1 = y_true1[0:n]
        y_true3 = y_true3[0:n]
        y_pred1 = (y_pred1[0:n] + y_pred1[n:]) / 2  # average of drug_row-drug_col and drug_col-drug-row
        y_pred3 = (y_pred3[0:n, ] + y_pred3[n:, ]) / 2
        test_loss1 = mse(y_pred1, y_true1).item()
        test_loss2 = mse(y_pred2, y_true2).item()
        synergy_result = {}
        sensitivity_result = {}
        synergy_result["MSE"] = test_loss1
        sensitivity_result["MSE"] = test_loss2
        synergy_result["RMSE"] = np.sqrt(test_loss1)
        sensitivity_result["RMSE"] = np.sqrt(test_loss2)
        y_true1 = y_true1.cpu()
        y_pred1 = y_pred1.cpu()
        y_true2 = y_true2.cpu()
        y_pred2 = y_pred2.cpu()
        synergy_result["Pearsonr"] = pearsonr(y_true1, y_pred1)[0]
        sensitivity_result["Pearsonr"] = pearsonr(y_true2, y_pred2)[0]
        synergy_result["CCE"] = cce(y_pred3, y_true3).item()
        sensitivity_result["CCE"] = cce(y_pred4, y_true4).item()
        y_true3 = y_true3.cpu()
        y_pred3 = y_pred3.cpu()
        y_true4 = y_true4.cpu()
        y_pred4 = y_pred4.cpu()
        y_pred3_prob = y_pred3[:, 1]
        y_pred4_prob = y_pred4[:, 1]
        synergy_result["ROC AUC"] = roc_auc_score(y_true3, y_pred3_prob)
        sensitivity_result["ROC AUC"] = roc_auc_score(y_true4, y_pred4_prob)
        y_pred3_label = y_pred3.argmax(axis=1)
        y_pred4_label = y_pred4.argmax(axis=1)
        y_pred3_prec, y_pred3_recall, y_pred3_threshold = precision_recall_curve(y_true3, y_pred3_prob)
        y_pred4_prec, y_pred4_recall, y_pred4_threshold = precision_recall_curve(y_true4, y_pred4_prob)
        synergy_result["PR AUC"] = auc(y_pred3_recall, y_pred3_prec)
        sensitivity_result["PR AUC"] = auc(y_pred4_recall, y_pred4_prec)
        synergy_result["ACC"] = accuracy_score(y_true3, y_pred3_label)
        sensitivity_result["ACC"] = accuracy_score(y_true4, y_pred4_label)
        synergy_result["PREC"] = precision_score(y_true3, y_pred3_label)
        sensitivity_result["PREC"] = precision_score(y_true4, y_pred4_label)
        synergy_result["Kappa"] = cohen_kappa_score(y_true3, y_pred3_label)
        sensitivity_result["Kappa"] = cohen_kappa_score(y_true4, y_pred4_label)
        print("test result:\n" + "Synergy:\n" + str(synergy_result) + "\nSensitivity:\n" + str(
            sensitivity_result) + "\n")
        with open(MTLSynergy_Result, 'a') as file:
            file.write("---------- Test ----------\n")
            file.write("test result:\n" + "Synergy:\n" + str(synergy_result) + "\nSensitivity:\n" + str(
                sensitivity_result) + "\n")
        return [synergy_result, sensitivity_result]


def calculate(result, name):
    tol_result = {}
    keys = result[0].keys()
    for key in keys:
        tol_result[key] = []
    for i in range(Fold):
        for key in keys:
            tol_result[key].append(result[i][key])
    print(str(name) + " result :")
    with open(MTLSynergy_Result, 'a') as file:
        file.write(str(name) + " result :\n")
    for key in keys:
        print(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]))
        with open(MTLSynergy_Result, 'a') as file:
            file.write(str(key) + ": " + str([np.mean(tol_result[key]), np.std(tol_result[key])]) + "\n")


epochs = 500
patience = 100
batch_size = 256
mse = MSELoss(reduction='mean').to(device)
cce = CategoricalCrossEntropyLoss().to(device)
drugs = pd.read_csv('data/drug_features.csv')
print("drugs.shape:", drugs.shape)
cell_lines = pd.read_csv('data/cell_line_features.csv')
print("cell_lines.shape:", cell_lines.shape)
summary = pd.read_csv('data/oneil_summary_idx.csv')
print("summary.shape:", summary.shape)

drugAE = DrugAE(output_dim=DrugAE_OutputDim).to(device)
print('---- start to load drugAE ----')
drug_path = DrugAE_SaveBase + str(DrugAE_OutputDim) + '.pth'
drugAE.load_state_dict(torch.load(drug_path))
drugAE.eval()
cell_path = CellAE_SaveBase + str(CellAE_OutputDim) + '.pth'
cellLineAE = CellLineAE(output_dim=CellAE_OutputDim).to(device)
print('---- start to load cellLineAE ----')
cellLineAE.load_state_dict(torch.load(cell_path))
cellLineAE.eval()
print(
    "--------- MTLSynergy with drugAE(" + str(DrugAE_OutputDim) + ") cellLineAE(" + str(CellAE_OutputDim) + ") ---------")
with open(MTLSynergy_Result, 'a') as file:
    file.write("--------- MTLSynergy with drugAE(" + str(DrugAE_OutputDim) + ") cellLineAE(" + str(
        CellAE_OutputDim) + ") ---------\n")
result_per_fold = []
model_input = DrugAE_OutputDim + CellAE_OutputDim
for fold_test in range(0, Fold):
    print("----- Test Fold " + str(fold_test) + " -----")
    with open(MTLSynergy_Result, 'a') as file:
        file.write("---------------- Test Fold " + str(fold_test) + " ----------------\n")
        file.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "\n")
    train_val_summary = summary.loc[summary['syn_fold'] != fold_test]
    hp_i = 0
    result_per_hp = []
    save_path = MTLSynergy_SaveBase + "fold_" + str(fold_test) + ".pth"
    for hyper_parameters in hyper_parameters_candidate:
        print("--- Hyper parameters " + str(hp_i) + ":" + str(hyper_parameters) + " ---")
        with open(MTLSynergy_Result, 'a') as file:
            file.write("--- Hyper parameters " + str(hp_i) + ":" + str(hyper_parameters) + " ---\n")
        result_per_inner_fold = []
        for inner_fold in range(0, Fold):
            if inner_fold == fold_test:
                continue
            set_seed(seed=1)
            inner_val_summary = summary.loc[summary['syn_fold'] == inner_fold]
            inner_train_summary = train_val_summary.loc[~train_val_summary.index.isin(inner_val_summary.index)]
            inner_val_dataset = MTLSynergyDataset(drugs, cell_lines, inner_val_summary)
            inner_train_dataset = MTLSynergyDataset(drugs, cell_lines, inner_train_summary)
            inner_val_loader = DataLoader(inner_val_dataset, batch_size=batch_size, shuffle=False)
            inner_train_loader = DataLoader(inner_train_dataset, batch_size=batch_size, shuffle=True, num_workers=2,
                                            pin_memory=True, drop_last=True)
            inner_val_num = len(inner_val_dataset)
            inner_train_num = len(inner_train_dataset)
            model = MTLSynergy(hyper_parameters['hidden_neurons'], model_input).to(device)
            model_es = EarlyStopping(patience=patience)
            optimizer = Adam(model.parameters(), lr=hyper_parameters['learning_rate'])
            start_time = time.time()
            inner_val_loss = []
            for epoch in range(epochs):
                fit(model, drugAE.encoder, cellLineAE.encoder, inner_train_loader, optimizer, mse,
                    cce, inner_fold)
                inner_val_result = validate(model, drugAE.encoder, cellLineAE.encoder, inner_val_loader,
                                            inner_val_num, mse, cce)
                inner_val_loss.append(inner_val_result)
                model_es(inner_val_result[0], model, save_path)
                if model_es.early_stop or epoch == epochs - 1:
                    result_per_inner_fold.append(model_es.best_loss)
                    with open(MTLSynergy_Result, 'a') as file:
                        file.write("When in epoch " + str(epoch - patience + 1) + ":\n")
                        file.write("Validation loss:" + str(inner_val_loss[epoch - patience]) + "\n")
                        file.write("Best loss:" + str(model_es.best_loss) + "\n")
                    break
        result_per_inner_fold_mean = np.array(result_per_inner_fold).mean()
        result_per_hp.append(result_per_inner_fold_mean)
        hp_i += 1
    best_hp_i = np.array(result_per_hp).argmin()
    best_hp = hyper_parameters_candidate[best_hp_i]
    print("--------- Best parameters: " + str(best_hp) + " ---------")
    with open(MTLSynergy_Result, 'a') as file:
        file.write("----------- Best parameters: " + str(best_hp) + " ----------\n")
    set_seed(seed=1)
    test_summary = summary.loc[summary['syn_fold'] == fold_test]
    validation_summary = train_val_summary.sample(frac=0.1, replace=False, random_state=1, axis=0)
    train_summary = train_val_summary.loc[~train_val_summary.index.isin(validation_summary.index)]
    train_dataset = MTLSynergyDataset(drugs, cell_lines, train_summary)
    train_num = len(train_dataset)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True,
                              num_workers=2, pin_memory=True)
    validation_dataset = MTLSynergyDataset(drugs, cell_lines, validation_summary)
    validation_num = len(validation_dataset)
    validation_loader = DataLoader(validation_dataset, batch_size=batch_size,
                                   shuffle=False)  # no shuffle
    test_dataset = MTLSynergyDataset(drugs, cell_lines, test_summary)
    test_num = len(test_dataset)
    test_loader = DataLoader(test_dataset, batch_size=batch_size,
                             shuffle=False)  # no shuffle

    model = MTLSynergy(best_hp['hidden_neurons'], model_input).to(device)
    model_es = EarlyStopping(patience=patience)
    optimizer = Adam(model.parameters(), lr=best_hp['learning_rate'])
    train_loss = []
    validation_loss = []
    start_time = time.time()
    for epoch in range(epochs):
        train_result = fit(model, drugAE.encoder, cellLineAE.encoder, train_loader, optimizer, mse, cce,
                           fold_test)
        train_loss.append(train_result)
        validation_result = validate(model, drugAE.encoder, cellLineAE.encoder, validation_loader, validation_num,
                                     mse, cce)
        validation_loss.append(validation_result)

        model_es(validation_result[0], model, save_path)
        if model_es.early_stop:
            with open(MTLSynergy_Result, 'a') as file:
                file.write("When in epoch " + str(epoch - patience + 1) + ":\n")
                file.write("Validation loss:" + str(validation_loss[epoch - patience]) + "\n")
                file.write("Best loss:" + str(model_es.best_loss) + "\n")
            break

    model = MTLSynergy(best_hp['hidden_neurons'], model_input).to(device)
    model.load_state_dict(torch.load(save_path))
    test_result = test(model, drugAE.encoder, cellLineAE.encoder, test_loader, test_num, mse, cce, fold_test)
    result_per_fold.append(test_result)
result = np.array(result_per_fold)
with open(MTLSynergy_Result, 'a') as file:
    file.write("------------------ Calculate ---------------\n")
calculate(result[:, 0], "Synergy")
calculate(result[:, 1], "Sensitivity")
with open(MTLSynergy_Result, 'a') as file:
    file.write("\n")
```

## File: README.md
```markdown
# MTLSynergy

## Requirements

- python=3.7
- cuda=10.2
- pytorch=1.8.1
- sklearn=1.0.2
- pandas=1.3.5

## Start

Run the AEtrain.py first to pre-train a drug encoder and a cell line encoder, and then run the MTLSynergytrain.py to train the model.

## Data

**drugs.csv**:  Information of 3118 drugs.

**cell_lines.csv**:  Information of 175 cell lines.

**drug_features.csv**:  Features of  3118 drugs, 1213-dimensional vector for each drug.

**cell_line_features.csv**:  Features of 175 cell lines, 5000-dimensional vector for each cell lines.

**oneil_summary_idx.csv**:  22 737 samples from O'Neil，each sample consists of two drugs id, a cell line id, synergy score of the drug combination on the cell line, respective sensitivity scores of the two drugs on the cell line.  

## Training files

**AEtrain.py**: used to pre-train a drug encoder and a cell line encoder.

**MTLSynergytrain.py**: used to train MTLSynergy in the *Leave Drug Combinations Out* scenario.

**MTLSynergy_LeaveCellOut.py**: used to train MTLSynergy in the *Leave Cell Lines Out* scenario.

**MTLSynergy_LeaveDrugOut.py**: used to train MTLSynergy in the *Leave Drugs Out* scenario.

**GBMtrain.py**: used to train Gradient Boosting Machine in the *Leave Drug Combinations Out* scenario.

**GBM_LeaveCellOut.py**: used to train Gradient Boosting Machine in the *Leave Cell Lines Out* scenario.

**GBM_LeaveDrugOut.py**: used to train Gradient Boosting Machine in the *Leave Drugs Out* scenario.

**RFtrain.py**: used to train Random Forest in the *Leave Drug Combinations Out* scenario.

**RF_LeaveCellOut.py**: used to train Random Forest in the *Leave Cell Lines Out* scenario.

**RF_LeaveDrugOut.py**: used to train Random Forest in the *Leave Drugs Out* scenario.



## Source code of the comparative methods

PRODeepSyn: https://github.com/TOJSSE-iData/PRODeepSyn

TranSynergy: https://github.com/qiaoliuhub/drug_combination

AuDnnSynergy: The authors did not provide the source code.

DeepSynergy: https://github.com/KristinaPreuer/DeepSynergy
```
