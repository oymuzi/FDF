#!/usr/bin/env python3
"""
调整余额数据的时间,将59分和01分的时间调整为最近的整点
"""
import csv
import re
from datetime import datetime, timedelta
from pathlib import Path


def adjust_time_to_hour(time_str: str) -> str:
    """
    将时间调整为最近的整点
    - 59分 -> 下一个整点
    - 01分 -> 当前整点
    - 其他非整点 -> 四舍五入到最近的整点
    """
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    minute = dt.minute
    second = dt.second

    # 如果已经是整点(00分00秒),直接返回
    if minute == 0 and second == 0:
        return time_str

    # 59分XX秒 -> 调整到下一小时
    if minute >= 58:
        dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    # 01分XX秒 -> 调整到当前小时
    elif minute <= 2:
        dt = dt.replace(minute=0, second=0, microsecond=0)
    # 其他情况四舍五入
    else:
        if minute >= 30:
            dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            dt = dt.replace(minute=0, second=0, microsecond=0)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def adjust_csv_file(file_path: Path, output_path: Path = None):
    """调整CSV文件中的时间列"""
    if output_path is None:
        output_path = file_path

    adjusted_count = 0
    rows = []

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)  # 保存表头
        rows.append(header)

        for row in reader:
            if len(row) > 0:
                original_time = row[0]
                adjusted_time = adjust_time_to_hour(original_time)

                if original_time != adjusted_time:
                    adjusted_count += 1
                    print(f"调整: {original_time} -> {adjusted_time}")

                row[0] = adjusted_time
                rows.append(row)

    # 写回文件
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\n文件 {file_path.name} 调整完成:")
    print(f"  总计调整: {adjusted_count} 条记录")
    print(f"  总记录数: {len(rows) - 1}")


def main():
    """主函数"""
    data_dir = Path(__file__).parent.parent / "data"

    print("=" * 60)
    print("开始调整余额数据时间")
    print("=" * 60)

    # 调整 mz_history.csv
    mz_file = data_dir / "mz_history.csv"
    if mz_file.exists():
        print(f"\n处理 {mz_file.name}...")
        adjust_csv_file(mz_file)
    else:
        print(f"文件不存在: {mz_file}")

    # 调整 wj_history.csv
    wj_file = data_dir / "wj_history.csv"
    if wj_file.exists():
        print(f"\n处理 {wj_file.name}...")
        adjust_csv_file(wj_file)
    else:
        print(f"文件不存在: {wj_file}")

    print("\n" + "=" * 60)
    print("所有文件调整完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
