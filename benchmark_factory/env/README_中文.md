# 四模型环境文件说明

本目录保存四个模型对应的 Conda 环境导出文件，用于项目打包、环境恢复和后续复现。

## 文件对应关系

| 文件名 | 对应模型 | 推荐环境名 |
| --- | --- | --- |
| `ddi.yml` | `DualSyn` | `ddi` |
| `mf.yml` | `MFSynDCP` | `mf` |
| `mvc.yml` | `MVCASyn` | `mvc` |
| `mtl.yml` | `MTLSynergy` | `mtl` |

## 用途说明

这些 `yml` 文件表示各模型运行时所需的 Python、PyTorch、CUDA 及相关依赖环境。

它们主要用于以下场景：

- 在新机器上恢复四个模型的运行环境
- 在论文答辩或项目交付时说明环境配置
- 在 Streamlit 系统中为真实推理或重新训练提供环境依据

## 环境恢复方法

在 Linux 或 Windows 的 Conda 终端中，进入本目录后可执行：

```bash
conda env create -f ddi.yml
conda env create -f mf.yml
conda env create -f mvc.yml
conda env create -f mtl.yml
```

如果环境已存在，需要先删除旧环境或改名后再创建。

## 激活方法

```bash
conda activate ddi
conda activate mf
conda activate mvc
conda activate mtl
```

## 在系统中的推荐对应关系

如果后续需要在统一系统中调用四个模型，建议使用以下环境名：

- `DualSyn` 使用 `ddi`
- `MFSynDCP` 使用 `mf`
- `MVCASyn` 使用 `mvc`
- `MTLSynergy` 使用 `mtl`

## 说明

- 当前这些环境文件已经去除了机器相关的 `prefix` 字段，更适合随项目一起打包。
- 这些文件更偏向“可复现环境导出”，不一定是最小精简依赖集合。
- 如果后续需要做项目发布版，可以在此基础上再整理一套更精简的 `runtime` 环境文件。
