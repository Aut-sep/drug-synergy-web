import csv
from pathlib import Path
import argparse

def process_csv_file(csv_path: Path, max_rows: int = 4, max_cols: int = 4):
    """处理单个CSV文件：只保留前4行和前4列，保存在同一目录下，文件名加 _sample"""
    try:
        # 生成样本文件名：原文件名_sample.csv
        sample_path = csv_path.with_name(csv_path.stem + "_sample" + csv_path.suffix)
        
        # 如果样本文件已存在，先删除（避免旧数据干扰）
        if sample_path.exists():
            sample_path.unlink()
        
        rows = []
        with open(csv_path, 'r', encoding='utf-8', errors='ignore', newline='') as infile:
            reader = csv.reader(infile)
            for i, row in enumerate(reader):
                if i >= max_rows:
                    break
                # 只保留前 max_cols 列
                truncated_row = row[:max_cols]
                rows.append(truncated_row)
        
        if not rows:
            print(f"警告: {csv_path} 是空文件")
            return False
        
        # 写入样本文件（保存在原目录）
        with open(sample_path, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows)
        
        # 打印处理信息
        col_count = len(rows[0]) if rows else 0
        print(f"✓ 已生成: {sample_path.name}  ({len(rows)} 行 × {col_count} 列)")
        return True
        
    except Exception as e:
        print(f"✗ 处理失败 {csv_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="处理CSV文件：只保留前4行×前4列，并生成 _sample 文件在同一目录")
    parser.add_argument("path", nargs="?", default=".", help="项目根目录（默认: 当前目录）")
    parser.add_argument("--max-rows", type=int, default=4, help="保留的最大行数（默认: 4）")
    parser.add_argument("--max-cols", type=int, default=4, help="每行保留的最大列数（默认: 4）")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"错误: 路径 '{root}' 不存在或不是目录")
        return

    print(f"开始扫描 CSV 文件: {root}")
    print(f"规则: 每个 CSV 只保留 前 {args.max_rows} 行 × 前 {args.max_cols} 列")
    print(f"样本文件将保存在原目录，名称加上 _sample\n")

    csv_files = list(root.rglob("*.csv"))
    if not csv_files:
        print("未找到任何 .csv 文件")
        return

    processed = 0
    for csv_file in csv_files:
        # 跳过已生成的 _sample 文件，避免重复处理
        if "_sample" in csv_file.name.lower():
            continue
        
        if process_csv_file(csv_file, args.max_rows, args.max_cols):
            processed += 1

    print(f"\n✅ 处理完成！共处理 {processed} 个 CSV 文件")
    print("\n接下来推荐使用 Repomix 的方式：")
    print("1. 在项目根目录创建或编辑 .repomixignore 文件，推荐添加以下内容：")
    print("""   data/
   datasets/
   raw_data/
   *.csv
   !*_sample.csv""")
    print("2. 运行 Repomix 生成给 AI 的上下文：")
    print("   npx repomix@latest --style markdown --compress")
    print("\n这样 AI 就能只看到每个 CSV 的格式（表头 + 前4行前4列示例），而不会读取全部数据。")


if __name__ == "__main__":
    main()