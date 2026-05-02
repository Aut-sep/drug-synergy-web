# O'Neil数据源与四模型补齐清单

更新时间：2026-04-13

## 1. 这次核对的目的

这份文档用于回答两个问题：

1. 你当前工程里，`O'Neil` 数据集到底应该以哪一份文件作为统一源数据。
2. 如果要把完整 `O'Neil` 适配到 `DualSyn`、`MFSynDCP`、`MVCASyn`、`MTLSynergy` 四个原始模型，各自还缺哪些数据需要补齐。

本次核对完全以四个模型原始代码的读入方式为准，而不是以之前人工做过的交集文件为准。

---

## 2. 建议采用的O'Neil本地源数据

### 2.1 当前工程里最可靠的本地O'Neil来源

建议把下面三份文件一起当作当前工程里的本地 `O'Neil` 主源数据：

1. `MTLSynergy/data/oneil_summary_idx_original_backup.csv`
2. `MTLSynergy/data/drugs.csv`
3. `MTLSynergy/data/cell_lines.csv`

原因是：

1. `oneil_summary_idx_original_backup.csv` 当前统计到 `22737` 条样本。
2. `MTLSynergy/README.md` 和 `md_for_ai/MTLSynergy_project_for_ai.md` 都明确写到 `oneil_summary_idx.csv` 原始应为 `22,737 samples`。
3. 但你当前目录下实际的 `MTLSynergy/data/oneil_summary_idx.csv` 只有 `7144` 条，明显已经不是最原始的完整版本，更像是后续处理过的子集。

因此，后面做统一 benchmark 时，不建议把当前的 `MTLSynergy/data/oneil_summary_idx.csv` 直接当成完整 `O'Neil` 原始源表。

### 2.2 这份本地完整O'Neil对应的规模

按 `oneil_summary_idx_original_backup.csv + drugs.csv + cell_lines.csv` 还原后，可得到：

1. 样本数：`22737`
2. 药物数：`38`
3. 细胞系数：`39`

这和很多后续方法论文对 `O'Neil` 的描述是一致的。

---

## 3. 外部资料和文献上的对应关系

为了后面论文写作更自然，可以这样理解：

1. `DrugComb` 文档中把 `ONEIL` 描述为 `583` 个药物组合在 `39` 个细胞系上的 pan-cancer 组合筛选研究。
2. 一些后续方法论文在加入表达谱等特征后，会进一步筛成 `29` 个有完整表达特征的细胞系，最后保留大约 `16907` 条样本。

可引用的外部页面：

1. DrugComb 帮助页：<https://www.drugcomb.org/help/>
2. DrugComb 下载页：<https://drugcomb.org/download/>
3. eLife 方法文献中对 O'Neil 数据的说明：<https://elifesciences.org/articles/100071>

需要注意：

1. 外部公开库里常见的是原始或标准化后的 `ONEIL` 数据。
2. 你当前项目真正最方便直接用的，仍然是本地已经存在的 `MTLSynergy/data/oneil_summary_idx_original_backup.csv` 这套索引化版本，因为它和另外几个原始项目已经放在同一个工作区里，后续适配最省事。

---

## 4. 四个模型原始代码各自真正读取什么

### 4.1 DualSyn

原始代码实际依赖：

1. `DualSyn/DualSyn/data/smiles.csv`
2. `DualSyn/DualSyn/data/cell_features_954.csv`
3. `DualSyn/DualSyn/data/fold*/train.csv`
4. `DualSyn/DualSyn/data/fold*/test.csv`

### 4.2 MFSynDCP

原始代码实际依赖：

1. `MFSynDCP/MFSynDCP/data/smiles.csv`
2. `MFSynDCP/MFSynDCP/data/cell_features.csv`
3. `MFSynDCP/MFSynDCP/data/fold/fold*/train.csv`
4. `MFSynDCP/MFSynDCP/data/fold/fold*/test.csv`

### 4.3 MVCASyn

原始代码实际依赖：

1. `MVCASyn/data/oneil_drug_two_smiles.csv`
2. `MVCASyn/data/exp.csv`
3. `MVCASyn/data/cn.csv`
4. `MVCASyn/data/folds/folds*/train.csv`
5. `MVCASyn/data/folds/folds*/test.csv`

注意：`MVCASyn` 不是只要表达谱就能跑，它同时需要 `exp.csv` 和 `cn.csv`。

### 4.4 MTLSynergy

原始代码实际依赖：

1. `MTLSynergy/data/drug_features.csv`
2. `MTLSynergy/data/cell_line_features.csv`
3. `MTLSynergy/data/oneil_summary_idx.csv`

并且它是通过 `summary` 里的整数索引，直接去 `drug_features.csv` 和 `cell_line_features.csv` 按行取数据，不是靠药物名和细胞名去匹配。

---

## 5. 核对后发现的关键名称问题

### 5.1 药物名别名问题：Carboplatinum 与 CARBOPLATIN

在本地完整 `O'Neil` 源表中，实际出现的名字是：

- `Carboplatinum`

而在另外三个模型的药物 SMILES 文件里，使用的是：

- `CARBOPLATIN`

这说明这里主要不是“药物数据缺失”，而是一个**药物别名不统一**的问题。

因此，做四模型统一处理时，必须增加一个药物别名字典，至少包含：

```text
Carboplatinum -> CARBOPLATIN
```

### 5.2 MVCASyn中的细胞名别名问题：NIHOVCAR3 与 OVCAR3

`MVCASyn` 的本地 `exp.csv` / `cn.csv` 里使用的是：

- `NIHOVCAR3`

而 `O'Neil` 统一源表使用的是：

- `OVCAR3`

所以这里也需要做一个细胞系名称映射：

```text
NIHOVCAR3 -> OVCAR3
```

这同样不属于“真缺失”，而是“命名不统一”。

---

## 6. 每个模型还需要补齐什么

下面的“缺失”都是相对于**完整 O'Neil 38药物、39细胞系**而言。

| 模型 | 药物是否缺失 | 细胞特征是否缺失 | 需要补齐的核心内容 |
|---|---|---|---|
| DualSyn | 不缺真实药物信息，只需做 `Carboplatinum -> CARBOPLATIN` 映射 | 缺 10 个细胞系 | 主要要补细胞特征 |
| MFSynDCP | 不缺真实药物信息，只需做 `Carboplatinum -> CARBOPLATIN` 映射 | 缺 8 个细胞系 | 主要要补细胞特征 |
| MVCASyn | 不缺真实药物信息，只需做 `Carboplatinum -> CARBOPLATIN` 映射 | 缺 6 个细胞系，另有 `NIHOVCAR3 -> OVCAR3` 别名问题 | 主要要补表达谱和拷贝数特征 |
| MTLSynergy | 就本地原始文件来说不缺 | 不缺 | 主要要在统一导出时处理药物名规范化 |

---

## 7. 具体缺失清单

### 7.1 DualSyn 缺失的细胞系

`DualSyn` 当前缺失以下 `10` 个细胞系特征：

1. `COLO320DM`
2. `DLD1`
3. `EFM192B`
4. `LNCAP`
5. `MSTO`
6. `OCUBM`
7. `OVCAR3`
8. `PA1`
9. `UWB1289`
10. `UWB1289BRCA1`

补齐含义：

需要为这些细胞系准备与 `cell_features_954.csv` 同结构、同维度的细胞特征。

### 7.2 MFSynDCP 缺失的细胞系

`MFSynDCP` 当前缺失以下 `8` 个细胞系特征：

1. `COLO320DM`
2. `DLD1`
3. `EFM192B`
4. `OCUBM`
5. `OVCAR3`
6. `PA1`
7. `UWB1289`
8. `UWB1289BRCA1`

补齐含义：

需要为这些细胞系准备与 `cell_features.csv` 同结构、同维度的细胞特征。

### 7.3 MVCASyn 缺失的细胞系

在先做了 `NIHOVCAR3 -> OVCAR3` 名称统一，并且要求细胞系同时存在于 `exp.csv` 和 `cn.csv` 后，`MVCASyn` 当前仍缺以下 `6` 个细胞系：

1. `COLO320DM`
2. `EFM192B`
3. `LNCAP`
4. `MSTO`
5. `OCUBM`
6. `UWB1289BRCA1`

补齐含义：

这 6 个细胞系都需要同时补：

1. 表达谱特征
2. 拷贝数特征

也就是说，不能只补一个 `exp` 或只补一个 `cn`。

### 7.4 MTLSynergy 的情况

`MTLSynergy` 就当前本地原始文件而言，不缺运行所需特征，原因是：

1. `drug_features.csv` 行数为 `3118`
2. 完整 O'Neil 源表中最大的 `drug_idx` 为 `117`
3. `cell_line_features.csv` 行数为 `175`
4. 完整 O'Neil 源表中最大的 `cell_idx` 为 `174`

因此，从“原始代码能否读到对应特征”这个角度看，`MTLSynergy` 是完整的。

但从“跨模型统一对齐”角度看，仍然要把：

```text
Carboplatinum -> CARBOPLATIN
```

这个药物名映射做进去。

---

## 8. 不补新特征时，当前最稳的统一比较子集

如果你现在不额外去外部补新的细胞特征，只利用当前四个原始项目中已经有的数据，那么最稳的四模型共同可用集合是：

1. `38` 个共同药物
2. `29` 个共同细胞系
3. 从完整 `22737` 条 O'Neil 样本中可保留 `16907` 条

这 `16907` 条样本的意义很重要：

1. 它不是随便删出来的。
2. 它正好对应“在四个模型现有原始输入条件下，四者都真的能读到”的那部分样本。
3. 这也是很多后续工作把 `O'Neil` 限制到 `29` 个细胞系时常见的规模量级。

因此，如果你现在的目标是先把本科毕业设计主线做稳，那么：

**优先建议先做这套 38药物 + 29细胞系 + 16907样本 的统一 benchmark。**

---

## 9. 如果想尽量保留完整O'Neil，后面还要补什么

如果你后面不满足于 `16907` 的共同子集，而是想尽量逼近完整 `22737` 条样本，那么后续补齐方向应该是：

1. 先统一药物别名
   - `Carboplatinum -> CARBOPLATIN`
2. 再统一细胞系别名
   - `NIHOVCAR3 -> OVCAR3`
3. 重点补 `DualSyn` 缺的 10 个细胞系特征
4. 再补 `MFSynDCP` 缺的 8 个细胞系特征
5. 再补 `MVCASyn` 缺的 6 个细胞系表达谱和拷贝数特征

从工程量看，真正麻烦的不是药物，而是**细胞特征补齐**。

---

## 10. 本次核对对应的可复用脚本

为了避免后面只剩手工描述，本次核对已经整理成脚本：

- `benchmark_factory/audit_oneil_coverage.py`

这个脚本会输出：

1. 本地完整 O'Neil 源文件位置
2. `22737` 与 `7144` 两份 summary 的规模差异
3. 四个模型分别缺哪些药物和细胞
4. 统一别名后四模型共同可用的药物数、细胞系数和保留样本数

运行方式：

```powershell
python D:\codex\bishe_base\benchmark_factory\audit_oneil_coverage.py
```

---

## 11. 可直接写进论文的方法性表述

下面这段话后面可以直接改写后放进论文正文：

> 为保证四个药物协同预测模型在统一数据集上的比较尽可能公平，本文首先回到各模型原始代码的输入层，对其实际依赖的数据文件进行了逐项核对。在此基础上，以本地保留的完整 O'Neil 索引化样本表 `oneil_summary_idx_original_backup.csv` 为统一源数据，并结合 `drugs.csv` 与 `cell_lines.csv` 还原出完整的药物和细胞系集合。核对结果表明，四个模型在药物信息层面基本不存在真实缺失，主要问题集中在个别药物和细胞系命名不统一以及细胞特征覆盖范围不同。其中，DualSyn、MFSynDCP 和 MVCASyn 均存在不同程度的细胞特征缺失，因此若不额外引入新的细胞特征数据，当前四模型可共同使用的最稳定子集为 38 个药物、29 个细胞系和 16907 条样本。该子集既保留了 O'Neil 数据集的主体规模，也满足四个原始模型在统一条件下进行公平比较的要求。

