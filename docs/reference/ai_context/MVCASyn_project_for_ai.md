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
benchmark_dataset.xlsx
custom_loss.py
cv_train.py
data_preprocessing.py
data/cn_sample.csv
data/exp_sample.csv
data/folds/folds0/test_sample.csv
data/folds/folds0/train_sample.csv
data/folds/folds1/test_sample.csv
data/folds/folds1/train_sample.csv
data/folds/folds2/test_sample.csv
data/folds/folds2/train_sample.csv
data/folds/folds3/test_sample.csv
data/folds/folds3/train_sample.csv
data/folds/folds4/test_sample.csv
data/folds/folds4/train_sample.csv
data/oneil_drug_two_smiles_sample.csv
layers.py
models.py
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

## File: custom_loss.py
```python
import torch
from torch import nn
import torch.nn.functional as F


class SigmoidLoss(nn.Module):
    def __init__(self, adv_temperature=None):
        super().__init__()
        self.adv_temperature = adv_temperature
    
    def forward(self, p_scores, n_scores):
        if self.adv_temperature:
            weights = F.softmax(self.adv_temperature * n_scores, dim=-1).detach()
            n_scores = weights * n_scores
        p_loss = - F.logsigmoid(p_scores).mean()
        n_loss = - F.logsigmoid(-n_scores).mean()
        
        return (p_loss + n_loss) / 2, p_loss, n_loss
```

## File: cv_train.py
```python
from datetime import datetime
import time 
import argparse
import torch

from torch import optim
from sklearn import metrics
import pandas as pd
import numpy as np
import models
import custom_loss
from data_preprocessing import DrugDataset, DrugDataLoader
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

######################### Parameters ######################
parser = argparse.ArgumentParser()
parser.add_argument('--n_atom_feats', type=int, default=55, help='num of input features')
parser.add_argument('--n_atom_hid', type=int, default=128, help='num of hidden features')
parser.add_argument('--kge_dim', type=int, default=128, help='dimension of interaction matrix')
parser.add_argument('--pooling_ratio', type=float, default=0.6, help='pooling_ratio')
parser.add_argument('--conv_channel1', type=int, default=16, help='conv_channel1')
parser.add_argument('--conv_channel2', type=int, default=16, help='conv_channel2')

parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
parser.add_argument('--n_epochs', type=int, default=125, help='num of epochs')
parser.add_argument('--batch_size', type=int, default=512, help='batch size')
parser.add_argument('--weight_decay', type=float, default=5e-4)
parser.add_argument('--data_size_ratio', type=int, default=1)
parser.add_argument('--use_cuda', type=bool, default=True, choices=[0, 1])

args = parser.parse_args()
n_atom_feats = args.n_atom_feats
n_atom_hid = args.n_atom_hid
kge_dim = args.kge_dim
pooling_ratio = args.pooling_ratio
conv_channel1 = args.conv_channel1
conv_channel2 = args.conv_channel2

lr = args.lr
n_epochs = args.n_epochs
batch_size = args.batch_size
weight_decay = args.weight_decay
data_size_ratio = args.data_size_ratio
device = 'cuda:0' if torch.cuda.is_available() and args.use_cuda else 'cpu'
print(args)


def save_metrics(metrics, filename):
    with open(filename, 'a') as f:
        f.write(','.join(map(str, metrics)) + '\n')

def do_compute(batch, device, model):

    probas_pred, ground_truth = [], []
    pos_tri, neg_tri = batch

    pos_tri = [tensor.to(device=device) for tensor in pos_tri]
    p_score = model(pos_tri)
    probas_pred.append(torch.sigmoid(p_score.detach()).cpu())
    ground_truth.append(np.ones(len(p_score)))

    neg_tri = [tensor.to(device=device) for tensor in neg_tri]
    n_score = model(neg_tri)
    probas_pred.append(torch.sigmoid(n_score.detach()).cpu())
    ground_truth.append(np.zeros(len(n_score)))

    probas_pred = np.concatenate(probas_pred)
    ground_truth = np.concatenate(ground_truth)

    return p_score, n_score, probas_pred, ground_truth


def do_compute_metrics(probas_pred, target):
    pred = (probas_pred >= 0.5).astype(int)
    acc = metrics.accuracy_score(target, pred)
    auroc = metrics.roc_auc_score(target, probas_pred)
    f1_score = metrics.f1_score(target, pred)
    precision = metrics.precision_score(target, pred)
    recall = metrics.recall_score(target, pred)
    p, r, t = metrics.precision_recall_curve(target, probas_pred)
    int_ap = metrics.auc(r, p)  # PR_AUC
    ap = metrics.average_precision_score(target, probas_pred)
    bacc = (recall + (1 - precision)) / 2
    prec = sum(target) / len(target)
    tnr = sum((target == 0) & (pred == 0)) / sum(target == 0)
    kappa = metrics.cohen_kappa_score(target, pred)

    return acc, auroc, f1_score, precision, recall, int_ap, ap, bacc, prec, tnr, kappa


def train(model, train_data_loader, loss_fn, optimizer, n_epochs, device, scheduler=None, model_save_path='model.pkl'):
    max_acc = 0
    print('Starting training at', datetime.today())
    for i in range(1, n_epochs + 1):
        start = time.time()
        train_loss = 0
        train_probas_pred = []
        train_ground_truth = []

        for batch in train_data_loader:
            model.train()
            p_score, n_score, probas_pred, ground_truth = do_compute(batch, device, model)
            train_probas_pred.append(probas_pred)
            train_ground_truth.append(ground_truth)
            loss, loss_p, loss_n = loss_fn(p_score, n_score)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * len(p_score)
        train_loss /= len(train_data)

        with torch.no_grad():
            train_probas_pred = np.concatenate(train_probas_pred)
            train_ground_truth = np.concatenate(train_ground_truth)

            train_acc, train_auc_roc, train_f1, train_precision, train_recall, train_int_ap, train_ap, train_bacc, train_prec, train_tnr, train_kappa = do_compute_metrics(
                train_probas_pred, train_ground_truth)

            if train_acc > max_acc:
                max_acc = train_acc
                torch.save(model, model_save_path)

        if scheduler:
            scheduler.step()

        print(f'Epoch: {i} ({time.time() - start:.4f}s), train_loss: {train_loss:.4f}'
              f' train_acc: {train_acc:.4f}')
        # print(f'\t\ttrain_roc: {train_auc_roc:.4f}, train_precision: {train_precision:.4f}')
        # print(f'\t\ttrain_bacc: {train_bacc:.4f}, train_prec: {train_prec:.4f}')
        # print(f'\t\ttrain_tnr: {train_tnr:.4f}, train_kappa: {train_kappa:.4f}')

def test(test_data_loader, model, fold):
    path = 'results/score/' + str(fold)
    test_probas_pred = []
    test_ground_truth = []
    with torch.no_grad():
        for batch in test_data_loader:
            model.eval()
            p_score, n_score, probas_pred, ground_truth = do_compute(batch, device, model)
            test_probas_pred.append(probas_pred)
            test_ground_truth.append(ground_truth)
        test_probas_pred = np.concatenate(test_probas_pred)
        test_ground_truth = np.concatenate(test_ground_truth)
        np.savetxt(path + '_probas_pred.txt', test_probas_pred)
        np.savetxt(path + '_ground_truth.txt', test_ground_truth)
        test_acc, test_auc_roc, test_f1, test_precision, test_recall, test_int_ap, test_ap, test_bacc, test_prec, test_tnr, test_kappa = do_compute_metrics(
            test_probas_pred, test_ground_truth)

    test_metrics = [test_acc, test_auc_roc, test_int_ap, test_ap, test_precision, test_kappa, test_f1, test_recall, test_bacc, test_prec, test_tnr]

    print('\n')
    print('============================== Test Result ==============================')
    print(f'\t\ttest_acc: {test_acc:.4f}, test_auc_roc: {test_auc_roc:.4f},test_f1: {test_f1:.4f},test_precision:{test_precision:.4f}')
    print(f'\t\ttest_recall: {test_recall:.4f}, test_int_ap: {test_int_ap:.4f},test_ap: {test_ap:.4f}')
    print(f'\t\ttest_bacc: {test_bacc:.4f}, test_prec: {test_prec:.4f}')
    print(f'\t\ttest_tnr: {test_tnr:.4f}, test_kappa: {test_kappa:.4f}')

    return test_metrics

file_result = 'results/folds.txt'
all_metrics = ('fold\ttest_acc\ttest_auc_roc\ttest_int_ap\ttest_ap\ttest_precision\ttest_kappa\ttest_f1\ttest_recall\ttest_bacc\ttest_prec\ttest_tnr')
with open(file_result, 'w') as f:
    f.write(all_metrics + '\n')
for i in range(5):
    train_file = 'data/folds/folds' + str(i) + '/train.csv'
    test_file = 'data/folds/folds' + str(i) + '/test.csv'
    model_save_path = f'results/model/fold{i}_model.pkl'
    print(f'数据集文件为{train_file, test_file}')

    df_train = pd.read_csv(train_file)
    df_test = pd.read_csv(test_file)

    train_tup = [(da, db, cell, label) for da, db, cell, label in zip(df_train['drug_a_name'], df_train['drug_b_name'], df_train['cell_line'], df_train['label'])]
    test_tup = [(da, db, cell, label) for da, db, cell, label in zip(df_test['drug_a_name'], df_test['drug_b_name'], df_test['cell_line'], df_test['label'])]

    train_data = DrugDataset(train_tup, ratio=data_size_ratio)
    test_data = DrugDataset(test_tup)

    print(f"Training with {len(train_data)} samples, and testing with {len(test_data)}")

    train_data_loader = DrugDataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=2)
    test_data_loader = DrugDataLoader(test_data, batch_size=batch_size * 3, num_workers=2)

    model = models.DVRL(n_atom_feats, n_atom_hid, kge_dim, pooling_ratio, conv_channel1, conv_channel2,
                        heads_out_feat_params=[64, 64, 64], blocks_params=[2, 2, 2])
    loss = custom_loss.SigmoidLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.LambdaLR(optimizer, lambda epoch: 0.96 ** (epoch))
    model.to(device=device)
    train(model, train_data_loader, loss, optimizer, n_epochs, device, scheduler, model_save_path)
    test_model = torch.load(model_save_path)
    test_metrics = test(test_data_loader, test_model, i)
    fold_num = 'fold' + str(i)
    test_metrics.insert(0, fold_num)
    save_metrics(test_metrics, file_result)
```

## File: data_preprocessing.py
```python
import random
import math

import torch
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset, DataLoader
from torch_geometric.data import Data, Batch
from rdkit import Chem
import pandas as pd
import numpy as np


def one_of_k_encoding_unk(x, allowable_set):
    if x not in allowable_set:
        x = allowable_set[-1]
    return list(map(lambda s: x == s, allowable_set))


def atom_features(atom, explicit_H=True, use_chirality=False):
    """
    用于生成单个原子特征表示的函数。该函数接受一个 RDKit 中的原子对象作为输入，并返回一个包含该原子特征表示的 NumPy 数组。
    原子的元素符号（one-of-k 编码）；44
    原子的度数归一化值（GetDegree() 函数除以10）；1
    原子的隐式价、形式电荷和自由基电子数；3
    原子的杂化轨道类型（one-of-k 编码）；5
    原子是否为芳香环上的原子；1
    原子的显式氢数（如果 explicit_H 参数为 True）；1
    原子的立体异构信息（如果 use_chirality 参数为 True）。没有使用
    """
    results = one_of_k_encoding_unk(
        atom.GetSymbol(),
        ['C','N','O', 'S','F','Si','P', 'Cl','Br','Mg','Na','Ca','Fe','As','Al','I','B','V','K','Tl',
            'Yb','Sb','Sn','Ag','Pd','Co','Se','Ti','Zn','H', 'Li','Ge','Cu','Au','Ni','Cd','In',
            'Mn','Zr','Cr','Pt','Hg','Pb','Unknown'
        ]) + [atom.GetDegree()/10, atom.GetImplicitValence(),
                atom.GetFormalCharge(), atom.GetNumRadicalElectrons()] + \
                one_of_k_encoding_unk(atom.GetHybridization(), [
                Chem.rdchem.HybridizationType.SP, Chem.rdchem.HybridizationType.SP2,
                Chem.rdchem.HybridizationType.SP3, Chem.rdchem.HybridizationType.
                                    SP3D, Chem.rdchem.HybridizationType.SP3D2
                ]) + [atom.GetIsAromatic()]
    # In case of explicit hydrogen(QM8, QM9), avoid calling `GetTotalNumHs`
    if explicit_H:
        results = results + [atom.GetTotalNumHs()]

    if use_chirality:
        try:
            results = results + one_of_k_encoding_unk(
            atom.GetProp('_CIPCode'),
            ['R', 'S']) + [atom.HasProp('_ChiralityPossible')]
        except:
            results = results + [False, False
                            ] + [atom.HasProp('_ChiralityPossible')]

    results = np.array(results).astype(np.float32)

    return torch.from_numpy(results)


def get_mol_edge_list_and_feat_mtx(mol_graph):
    n_features = [(atom.GetIdx(), atom_features(atom)) for atom in mol_graph.GetAtoms()]
    n_features.sort() # to make sure that the feature matrix is aligned according to the idx of the atom
    _, n_features = zip(*n_features)
    n_features = torch.stack(n_features)

    edge_list = torch.LongTensor([(b.GetBeginAtomIdx(), b.GetEndAtomIdx()) for b in mol_graph.GetBonds()])
    undirected_edge_list = torch.cat([edge_list, edge_list[:, [1, 0]]], dim=0) if len(edge_list) else edge_list
    return undirected_edge_list.T, n_features


def get_bipartite_graph(mol_graph_1, mol_graph_2):
    x1 = np.arange(0, len(mol_graph_1.GetAtoms()))
    x2 = np.arange(0, len(mol_graph_2.GetAtoms()))
    edge_list = torch.LongTensor(np.meshgrid(x1, x2))
    edge_list = torch.stack([edge_list[0].reshape(-1), edge_list[1].reshape(-1)])
    return edge_list


class BipartiteData(Data):
    def __init__(self, edge_index=None, x_s=None, x_t=None):
        super().__init__()
        self.edge_index = edge_index
        self.x_s = x_s
        self.x_t = x_t
    def __inc__(self, key, value, *args, **kwargs):
        if key == 'edge_index':
            return torch.tensor([[self.x_s.size(0)], [self.x_t.size(0)]])
        else:
            return super().__inc__(key, value, *args, **kwargs)

# 细胞系数据读取和标准化
cell_cn = pd.read_csv('data/cn.csv', sep=',')
cell_exp = pd.read_csv('data/exp.csv', sep=',')

# 提取细胞系名称列
cn_names = cell_cn.iloc[:, 0]
exp_names = cell_exp.iloc[:, 0]

# 去除细胞系名称列，进行标准化
cn_data = cell_cn.iloc[:, 1:]
exp_data = cell_exp.iloc[:, 1:]

# 对基因表达数据进行 z-score 标准化
scaler_exp = StandardScaler()
exp_features = pd.DataFrame(scaler_exp.fit_transform(exp_data), columns=exp_data.columns)
exp_features.insert(0, 'cell_line_name', exp_names)

# 对拷贝数数据进行 z-score 标准化
scaler_cn = StandardScaler()
cn_features = pd.DataFrame(scaler_cn.fit_transform(cn_data), columns=cn_data.columns)
cn_features.insert(0, 'cell_line_name', cn_names)

# 细胞系数据读取和标准化

df_drugs_smiles = pd.read_csv('data/oneil_drug_two_smiles.csv')

drug_id_mol_graph_tup = [(id, Chem.MolFromSmiles(smiles.strip())) for id, smiles in zip(df_drugs_smiles['drug_name'], df_drugs_smiles['smiles'])]

drug_to_mol_graph = {id:Chem.MolFromSmiles(smiles.strip()) for id, smiles in zip(df_drugs_smiles['drug_name'], df_drugs_smiles['smiles'])}

ATOM_MAX_NUM = np.max([m[1].GetNumAtoms() for m in drug_id_mol_graph_tup])

MOL_EDGE_LIST_FEAT_MTX = {drug_id: get_mol_edge_list_and_feat_mtx(mol)
                                for drug_id, mol in drug_id_mol_graph_tup}

MOL_EDGE_LIST_FEAT_MTX = {drug_id: mol for drug_id, mol in MOL_EDGE_LIST_FEAT_MTX.items() if mol is not None}

class DrugDataset(Dataset):
    def __init__(self, tri_list, ratio=1.0, shuffle=True):
        self.tri_list = []
        self.ratio = ratio

        for da, db, cell, label, *_ in tri_list:
            if ((da in MOL_EDGE_LIST_FEAT_MTX) and (db in MOL_EDGE_LIST_FEAT_MTX)):
                self.tri_list.append((da, db, cell, label))

        if shuffle:
            random.shuffle(self.tri_list)
        limit = math.ceil(len(self.tri_list) * ratio)
        self.tri_list = self.tri_list[:limit]

    def __len__(self):
        return len(self.tri_list)

    def __getitem__(self, index):
        return self.tri_list[index]

    def collate_fn(self, batch):

        pos_cn = []
        pos_exp = []
        pos_h_samples = []
        pos_t_samples = []
        pos_b_samples = []

        neg_cn = []
        neg_exp = []
        neg_h_samples = []
        neg_t_samples = []
        neg_b_samples = []

        for da, db, cell, label in batch:
            if label == 1:

                cn_data = cn_features.loc[
                    cn_features['cell_line_name'] == cell, cn_features.columns != 'cell_line_name']
                cn_data = cn_data.values

                exp_data = exp_features.loc[
                    exp_features['cell_line_name'] == cell, exp_features.columns != 'cell_line_name']
                exp_data = exp_data.values

                pos_cn.append(cn_data)
                pos_exp.append(exp_data)

                h_data = self.__create_graph_data(da)
                t_data = self.__create_graph_data(db)
                h_graph = drug_to_mol_graph[da]
                t_graph = drug_to_mol_graph[db]

                pos_b_graph = self._create_b_graph(get_bipartite_graph(h_graph, t_graph), h_data.x, t_data.x)

                pos_h_samples.append(h_data)
                pos_t_samples.append(t_data)
                pos_b_samples.append(pos_b_graph)

            if label == 0:

                cn_data = cn_features.loc[
                    cn_features['cell_line_name'] == cell, cn_features.columns != 'cell_line_name']
                cn_data = cn_data.values

                exp_data = exp_features.loc[
                    exp_features['cell_line_name'] == cell, exp_features.columns != 'cell_line_name']
                exp_data = exp_data.values

                neg_cn.append(cn_data)
                neg_exp.append(exp_data)

                h_data = self.__create_graph_data(da)
                t_data = self.__create_graph_data(db)
                h_graph = drug_to_mol_graph[da]
                t_graph = drug_to_mol_graph[db]

                neg_b_graph = self._create_b_graph(get_bipartite_graph(h_graph, t_graph), h_data.x, t_data.x)

                neg_h_samples.append(h_data)
                neg_t_samples.append(t_data)
                neg_b_samples.append(neg_b_graph)

        pos_h_samples = Batch.from_data_list(pos_h_samples)
        pos_t_samples = Batch.from_data_list(pos_t_samples)
        pos_b_samples = Batch.from_data_list(pos_b_samples)
        pos_cn = torch.tensor(pos_cn)
        pos_exp = torch.tensor(pos_exp)

        pos_tri = (pos_h_samples, pos_t_samples, pos_cn, pos_exp, pos_b_samples)

        neg_h_samples = Batch.from_data_list(neg_h_samples)
        neg_t_samples = Batch.from_data_list(neg_t_samples)
        neg_b_samples = Batch.from_data_list(neg_b_samples)
        neg_cn = torch.tensor(neg_cn)
        neg_exp = torch.tensor(neg_exp)

        neg_tri = (neg_h_samples, neg_t_samples, neg_cn, neg_exp, neg_b_samples)

        return pos_tri, neg_tri

    def __create_graph_data(self, id):
        edge_index = MOL_EDGE_LIST_FEAT_MTX[id][0]
        n_features = MOL_EDGE_LIST_FEAT_MTX[id][1]
        return Data(x=n_features, edge_index=edge_index)

    def _create_b_graph(self, edge_index, x_s, x_t):
        return BipartiteData(edge_index, x_s, x_t)


class DrugDataLoader(DataLoader):
    def __init__(self, data, **kwargs):
        super().__init__(data, collate_fn=data.collate_fn, **kwargs)
```

## File: data/cn_sample.csv
```
cell_line_name,NOC2L,AGRN,TAS1R3
NIHOVCAR3,1.4657841806331222,1.4657841806331222,1.4657841806331222
KPL1,0.9208663847456344,0.9208663847456344,0.9120175362403604
NCIH1650,0.5567242583364402,0.5567242583364402,0.5567242583364402
```

## File: data/exp_sample.csv
```
cell_line_name,ACTR1B,CDK5,CDH3
A2058,5.0699973175,5.5675617325,0.1386374215
NCIH460,4.0140830625,3.9960064152,0.0075134118
ES2,4.9754573273,4.9576097252,0.1005485332
```

## File: data/folds/folds0/test_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
L778123,SUNITINIB,A375,17.4868393184
ERLOTINIB,SN-38,PA1,30.9067752487
VINORELBINE,BORTEZOMIB,CAOV3,-42.792628008
```

## File: data/folds/folds0/train_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
SN-38,SORAFENIB,UWB1289,-2.4709970343
L778123,SUNITINIB,ES2,10.2848792415
MRK-003,LAPATINIB,RPMI7951,32.8857601486
```

## File: data/folds/folds1/test_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
MK-4827,MK-8776,VCAP,18.5837193932
PACLITAXEL,SUNITINIB,HT144,11.3272419473
ZOLINZA,BORTEZOMIB,NIHOVCAR3,-15.5733931502
```

## File: data/folds/folds1/train_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
PACLITAXEL,SORAFENIB,KPL1,-1.5230836373
BORTEZOMIB,GELDANAMYCIN,ZR751,-65.7598137284
CARBOPLATIN,ZOLINZA,SKMEL30,-1.2378847438
```

## File: data/folds/folds2/test_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
MK-4827,DASATINIB,HT29,26.4330759778
PACLITAXEL,ERLOTINIB,HT144,26.0766641236
ZOLINZA,BEZ-235,CAOV3,42.9375071637
```

## File: data/folds/folds2/train_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
PACLITAXEL,ZOLINZA,LOVO,10.3749746515
BORTEZOMIB,MK-8776,A427,-7.5617437623
CYCLOPHOSPHAMIDE,ABT-888,LOVO,-4.9527410642
```

## File: data/folds/folds3/test_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
MK-4827,TOPOTECAN,A2058,-1.5630949819
PACLITAXEL,MK-4827,A427,-6.7556370809
ZOLINZA,AZD1775,A375,21.045055923
```

## File: data/folds/folds3/train_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
PACLITAXEL,TEMOZOLOMIDE,ES2,10.2946553392
BORTEZOMIB,MK-8669,SW620,-2.606203184
CYCLOPHOSPHAMIDE,ABT-888,SW837,-15.4205582186
```

## File: data/folds/folds4/test_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
MK-4827,SORAFENIB,CAOV3,-16.7616786742
PACLITAXEL,PD325901,T47D,-2.6639648783
ZOLINZA,BEZ-235,MDAMB436,25.203435883
```

## File: data/folds/folds4/train_sample.csv
```
drug_a_name,drug_b_name,cell_line,synergy
PACLITAXEL,SORAFENIB,RPMI7951,-13.172091948
BORTEZOMIB,MK-8669,UACC62,-13.513874525
CARBOPLATIN,ZOLINZA,SW620,-12.7625390062
```

## File: data/oneil_drug_two_smiles_sample.csv
```
drug_name,smiles
5-FU,C1=C(C(=O)NC(=O)N1)F
ABT-888,C[C@@]1(CCCN1)C2=NC3=C(C=CC=C3N2)C(=O)N.Cl.Cl
AZD1775,CC(C)(C1=NC(=CC=C1)N2C3=NC(=NC=C3C(=O)N2CC=C)NC4=CC=C(C=C4)N5CCN(CC5)C)O
```

## File: layers.py
```python
import math

import torch
from torch import nn
import torch.nn.functional as F

from torch_geometric.nn import GATConv, GraphConv
from torch_geometric.nn.pool.topk_pool import filter_adj, topk


class CrossAttentionLayer(nn.Module):
    def __init__(self, embed_dim):
        super().__init__()
        self.embed_dim = embed_dim
        self.query_proj = nn.Linear(embed_dim, embed_dim)
        self.key_proj = nn.Linear(embed_dim, embed_dim)
        self.value_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, queries, keys, values):
        # Project the inputs
        queries = self.query_proj(queries)
        keys = self.key_proj(keys)
        values = self.value_proj(values)

        # Compute attention scores
        attention_scores = torch.bmm(queries, keys.transpose(1, 2)) / self.embed_dim ** 0.5
        attention_weights = F.softmax(attention_scores, dim=-1)

        # Compute the output
        attended_values = torch.bmm(attention_weights, values)
        output = self.out_proj(attended_values)

        return output


class MLPLayer(nn.Module):
    def __init__(self, input_dim, embed_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),  # 可以调整这些层的大小
            nn.ReLU(),
            nn.Linear(512, embed_dim)  # 输出嵌入的维度
        )
        self.decoder = nn.Sequential(
            nn.Linear(embed_dim, 512),
            nn.ReLU(),
            nn.Linear(512, input_dim)  # 输出的维度恢复到输入维度
        )

    def forward(self, x):
        x = x.to(torch.float32)
        embedding = self.encoder(x)
        return embedding


# Define a linear transformation to adjust `attendant` dimensions
class AttendantTransformer(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(AttendantTransformer, self).__init__()
        self.linear = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.linear(x)


class IntraGraphAttention(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.input_dim = input_dim
        self.intra = GATConv(input_dim, 32, 2)

    def forward(self, data):
        input_feature, edge_index = data.x, data.edge_index
        input_feature = F.elu(input_feature)
        intra_rep = self.intra(input_feature, edge_index)
        return intra_rep


class InterGraphAttention(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.input_dim = input_dim
        self.inter = GATConv((input_dim, input_dim), 32, 2)

    def forward(self, h_data, t_data, b_graph):
        edge_index = b_graph.edge_index
        h_input = F.elu(h_data.x)
        t_input = F.elu(t_data.x)
        t_rep = self.inter((h_input, t_input), edge_index)
        h_rep = self.inter((t_input, h_input), edge_index[[1, 0]])
        return h_rep, t_rep


class Pool(nn.Module):
    def __init__(self, in_dim: int, ratio=0.5, conv_op=GraphConv, non_linearity=F.tanh):
        super().__init__()
        self.in_dim = in_dim
        self.ratio = ratio
        self.score_layer1 = conv_op(in_dim, 1)
        self.score_layer2 = nn.Linear(in_dim, 1)
        self.non_linearity = non_linearity
        self.reset_parameters()

    def reset_parameters(self):
        self.score_layer1.reset_parameters()
        self.score_layer2.reset_parameters()

    def forward(self, x, edge_index, edge_attr=None, batch=None):
        score1 = self.score_layer1(x, edge_index).squeeze()
        score2 = self.score_layer2(x).squeeze()
        score = torch.max(torch.cat((score1.unsqueeze(1), score2.unsqueeze(1)), dim=1), dim=1)[0]

        perm = topk(score, self.ratio, batch)

        x = x[perm] * self.non_linearity(score[perm]).view(-1, 1)
        edge_index, edge_attr = filter_adj(edge_index, edge_attr, perm,
                                           num_nodes=score.size(0))
        batch = batch[perm]

        return x, edge_index, batch


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, dim_in, dim_k, dim_v, num_heads=8):
        super().__init__()
        assert dim_k % num_heads == 0 and dim_v % num_heads == 0, "dim_k and dim_v must be multiple of num_heads"
        self.dim_in = dim_in
        self.dim_k = dim_k
        self.dim_v = dim_v
        self.num_heads = num_heads
        self.linear_q = nn.Linear(dim_in, dim_k, bias=False)
        self.linear_k = nn.Linear(dim_in, dim_k, bias=False)
        self.linear_v = nn.Linear(dim_in, dim_v, bias=False)
        self._norm_fact = 1 / math.sqrt(dim_k // num_heads)
        self.norm = nn.LayerNorm(dim_v)
        self.reset_parameters()

    def reset_parameters(self):
        self.linear_q.reset_parameters()
        self.linear_k.reset_parameters()
        self.linear_v.reset_parameters()
        self.norm.reset_parameters()

    def forward(self, x):
        batch, n, dim_in = x.shape
        assert dim_in == self.dim_in

        nh = self.num_heads
        dk = self.dim_k // nh
        dv = self.dim_v // nh

        q = self.linear_q(x).reshape(batch, n, nh, dk).transpose(1, 2)
        k = self.linear_k(x).reshape(batch, n, nh, dk).transpose(1, 2)
        v = self.linear_v(x).reshape(batch, n, nh, dv).transpose(1, 2)

        dist = torch.matmul(q, k.transpose(2, 3)) * self._norm_fact
        dist = torch.softmax(dist, dim=-1)

        att = torch.matmul(dist, v)
        att = att.transpose(1, 2).reshape(batch, n, self.dim_v)
        att_n = self.norm(att)
        return att_n


class CoAttentionLayer(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.n_features = n_features
        self.w_q = nn.Parameter(torch.zeros(n_features, n_features // 2))
        self.w_k = nn.Parameter(torch.zeros(n_features, n_features // 2))
        self.bias = nn.Parameter(torch.zeros(n_features // 2))
        self.a = nn.Parameter(torch.zeros(n_features // 2))

        nn.init.xavier_uniform_(self.w_q)
        nn.init.xavier_uniform_(self.w_k)
        nn.init.xavier_uniform_(self.bias.view(*self.bias.shape, -1))
        nn.init.xavier_uniform_(self.a.view(*self.a.shape, -1))

    def forward(self, receiver, attendant):
        keys = receiver @ self.w_k
        queries = attendant @ self.w_q
        values = receiver

        e_activations = queries.unsqueeze(-3) + keys.unsqueeze(-2) + self.bias
        e_scores = torch.tanh(e_activations) @ self.a
        attentions = e_scores
        return attentions


class RESCAL(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.n_features = n_features

    def forward(self, heads, tails, rels, alpha_scores):
        rels = F.normalize(rels, dim=-1)
        heads = F.normalize(heads, dim=-1)
        tails = F.normalize(tails, dim=-1)

        rels = rels.view(-1, self.n_features, self.n_features)
        scores = heads @ rels @ tails.transpose(-2, -1)

        if alpha_scores is not None:
            scores = alpha_scores * scores
        scores = scores.sum(dim=(-2, -1))

        return scores

    def __repr__(self):
        return f"{self.__class__.__name__}({self.n_rels}, {self.rel_emb.weight.shape})"
```

## File: models.py
```python
from math import ceil

import torch
from torch import nn
import torch.nn.functional as F
from torch.nn import Conv2d, MaxPool2d
from torch.nn.modules.container import ModuleList

from torch_geometric.utils import to_dense_batch
from torch_geometric.nn import GATConv, LayerNorm

from layers import (
    CoAttentionLayer,
    RESCAL,
    IntraGraphAttention,
    InterGraphAttention, Pool, MultiHeadSelfAttention, AttendantTransformer, MLPLayer, CrossAttentionLayer,
)

from data_preprocessing import ATOM_MAX_NUM


class DVRL(nn.Module):
    def __init__(self, in_features, hidd_dim, kge_dim, pooling_ratio, conv_channel1, conv_channel2,
                 heads_out_feat_params, blocks_params):
        super().__init__()
        self.in_features = in_features
        self.hidd_dim = hidd_dim
        self.kge_dim = kge_dim
        self.n_blocks = len(blocks_params)
        self.pooling_ratio = pooling_ratio
        self.max_num_nodes = ATOM_MAX_NUM
        self.dims = ceil(self.max_num_nodes * self.pooling_ratio)
        self.conv_channel1 = conv_channel1
        self.conv_channel2 = conv_channel2

        self.initial_norm = LayerNorm(self.in_features)
        self.blocks = []
        self.net_norms = ModuleList()
        for i, (head_out_feats, n_heads) in enumerate(zip(heads_out_feat_params, blocks_params)):
            block = DVRL_Block(n_heads, in_features, head_out_feats, final_out_feats=self.hidd_dim)
            self.add_module(f"block{i}", block)
            self.blocks.append(block)
            self.net_norms.append(LayerNorm(head_out_feats * n_heads))
            in_features = head_out_feats * n_heads

        self.conv1 = Conv2d(3, self.conv_channel1, (self.dims, 1))
        self.maxpool2d = MaxPool2d((1, 2), (1, 2))
        self.conv2 = Conv2d(self.conv_channel1, self.conv_channel2, (1, self.hidd_dim // 2), 1)

        # Initialize MLPLayer for cn, exp, mut
        self.mlp_cn = MLPLayer(input_dim=3895, embed_dim=256)
        self.mlp_exp = MLPLayer(input_dim=4004, embed_dim=256)
        # Add Cross Attention Layer
        self.cross_attention = CrossAttentionLayer(256)
        self.fc = nn.Linear(256 * 2, 256)

        self.co_attention = CoAttentionLayer(self.conv_channel1)

        self.transformer = AttendantTransformer(256, 16)
        self.KGE = RESCAL(self.conv_channel1)

    def reset_parameters(self):
        self.conv1.reset_parameters()
        self.conv2.reset_parameters()

    def forward(self, triples):
        h_data, t_data, cn_data, exp_data, b_graph = triples

        batch_size = h_data.num_graphs

        h_data.x = self.initial_norm(h_data.x, h_data.batch)
        t_data.x = self.initial_norm(t_data.x, t_data.batch)
        repr_h = []
        repr_t = []

        for i, block in enumerate(self.blocks):
            out = block(h_data, t_data, b_graph)

            h_data = out[0]
            t_data = out[1]
            r_h = out[2]
            r_t = out[3]
            repr_h.append(r_h)
            repr_t.append(r_t)

            h_data.x = F.elu(self.net_norms[i](h_data.x, h_data.batch))
            t_data.x = F.elu(self.net_norms[i](t_data.x, t_data.batch))

        repr_h = torch.stack(repr_h, dim=-3)
        repr_t = torch.stack(repr_t, dim=-3)

        repr_h = F.relu(self.conv1(repr_h))
        repr_h = self.maxpool2d(repr_h)
        repr_h = F.relu(self.conv2(repr_h))
        repr_h = repr_h.view(batch_size, -1)
        repr_h = repr_h.unsqueeze(1)

        repr_t = F.relu(self.conv1(repr_t))
        repr_t = self.maxpool2d(repr_t)
        repr_t = F.relu(self.conv2(repr_t))
        repr_t = repr_t.view(batch_size, -1)
        repr_t = repr_t.unsqueeze(1)

        kge_heads = repr_h
        kge_tails = repr_t

        dd_attentions = self.co_attention(kge_heads, kge_tails)

        # Encode cn, exp to 256-dimensional embeddings
        cn_embeddings = self.mlp_cn(cn_data)
        exp_embeddings = self.mlp_exp(exp_data)

        # Attention between cn_embeddings and exp_embeddings
        att_cn_exp = self.cross_attention(cn_embeddings, exp_embeddings, exp_embeddings)

        # Attention between exp_embeddings and cn_embeddings
        att_exp_cn = self.cross_attention(exp_embeddings, cn_embeddings, cn_embeddings)

        concatenated = torch.cat([att_cn_exp, att_exp_cn], dim=-1)
        cell = self.fc(concatenated)

        cell_16 = self.transformer(cell)
        d1c_attentions = self.co_attention(kge_heads, cell_16)
        d2c_attentions = self.co_attention(kge_tails, cell_16)

        alpha = 0.4
        beta = 0.3
        gamma = 0.3

        # 融合注意力分数
        attentions = (alpha * dd_attentions +
                      beta * d1c_attentions +
                      gamma * d2c_attentions)

        scores = self.KGE(kge_heads, kge_tails, cell, attentions)

        return scores


class DVRL_Block(nn.Module):
    def __init__(self, n_heads, in_features, head_out_feats, final_out_feats):
        super().__init__()
        self.n_heads = n_heads
        self.in_features = in_features
        self.out_features = head_out_feats
        self.pooling_ratio = 0.6
        self.max_num_nodes = ATOM_MAX_NUM
        self.dims = ceil(self.max_num_nodes * self.pooling_ratio)

        self.feature_conv = GATConv(in_features, head_out_feats, n_heads)
        self.intraAtt = IntraGraphAttention(head_out_feats * n_heads)
        self.interAtt = InterGraphAttention(head_out_feats * n_heads)
        self.pool = Pool(final_out_feats, ratio=self.pooling_ratio)
        self.att = MultiHeadSelfAttention(final_out_feats, final_out_feats, final_out_feats, 8)

    def reset_parameters(self):
        self.pool.reset_parameters()
        self.att.reset_parameters()

    def forward(self, h_data, t_data, b_graph):
        h_data.x = self.feature_conv(h_data.x, h_data.edge_index)
        t_data.x = self.feature_conv(t_data.x, t_data.edge_index)

        h_intraRep = self.intraAtt(h_data)
        t_intraRep = self.intraAtt(t_data)

        h_interRep, t_interRep = self.interAtt(h_data, t_data, b_graph)

        h_rep = torch.cat([h_intraRep, h_interRep], 1)
        t_rep = torch.cat([t_intraRep, t_interRep], 1)
        h_data.x = h_rep
        t_data.x = t_rep

        h_pool_x, pool_edge_index, h_pool_batch = self.pool(h_data.x, h_data.edge_index, batch=h_data.batch)
        t_pool_x, pool_edge_index, t_pool_batch = self.pool(t_data.x, t_data.edge_index, batch=t_data.batch)

        h_batch_data, h_mask = to_dense_batch(h_pool_x, h_pool_batch, max_num_nodes=self.dims)
        t_batch_data, t_mask = to_dense_batch(t_pool_x, t_pool_batch, max_num_nodes=self.dims)

        h_att_x = self.att(h_batch_data)
        t_att_x = self.att(t_batch_data)

        return h_data, t_data, h_att_x, t_att_x
```
