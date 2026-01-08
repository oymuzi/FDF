#!/usr/bin/env python3
"""
FDF数据更新脚本
在fdf项目内完成所有操作:运行账号检查 + 生成CSV + 复制到data目录
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil

# fdf项目目录
FDF_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = FDF_DIR / 'scripts'
DATA_DIR = FDF_DIR / 'data'

def run_account_checks():
    """运行所有账号检查脚本"""
    print("🚀 运行账号检查脚本...")

    # 要运行的脚本列表
    scripts_to_run = [
        ('check_account_balance.py', 'MZ账号'),
        ('check_wj_account_balance.py', 'George账号'),
    ]

    all_success = True

    for script_name, description in scripts_to_run:
        script_path = SCRIPTS_DIR / script_name

        if not script_path.exists():
            print(f"⚠️  {description}脚本不存在: {script_path}")
            all_success = False
            continue

        print(f"\n{'='*60}")
        print(f"📊 检查{description}...")
        print(f"{'='*60}")

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(FDF_DIR),
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print("错误输出:", result.stderr)

            if result.returncode == 0:
                print(f"✅ {description}检查完成")
            else:
                print(f"❌ {description}检查失败,返回码: {result.returncode}")
                all_success = False

        except subprocess.TimeoutExpired:
            print(f"❌ {description}检查超时")
            all_success = False
        except Exception as e:
            print(f"❌ {description}检查异常: {e}")
            all_success = False

    return all_success


def copy_csv_files():
    """将生成的CSV文件复制到data目录（追加模式）"""
    print(f"\n📁 复制CSV文件到data目录... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 确保data目录存在
    DATA_DIR.mkdir(exist_ok=True)

    # CSV文件路径
    mz_source = FDF_DIR / 'check_history.csv'
    mz_target = DATA_DIR / 'mz_history.csv'
    wj_source = FDF_DIR / 'check_history_wj.csv'
    wj_target = DATA_DIR / 'wj_history.csv'

    files_to_copy = [
        (mz_source, mz_target, 'MZ'),
        (wj_source, wj_target, 'George'),
    ]

    all_success = True

    for source, target, name in files_to_copy:
        if not source.exists():
            print(f"⚠️  {name}源文件不存在: {source}")
            all_success = False
            continue

        try:
            # 读取源文件内容
            source_content = source.read_text(encoding='utf-8-sig')
            source_lines = source_content.strip().split('\n')

            # 跳过表头，只保留数据行
            data_lines = source_lines[1:] if len(source_lines) > 1 else []

            if not data_lines:
                print(f"⚠️  {name}源文件没有数据")
                continue

            # 如果目标文件不存在，创建并写入表头
            if not target.exists():
                target.write_text(source_content, encoding='utf-8-sig')
                print(f"✅ {name}数据已创建 ({len(data_lines)} 行)")
            else:
                # 追加新数据（不包含表头）
                with open(target, 'a', encoding='utf-8-sig') as f:
                    for line in data_lines:
                        f.write(line + '\n')
                print(f"✅ {name}数据已追加 ({len(data_lines)} 行)")

        except Exception as e:
            print(f"❌ 复制{name}数据失败: {e}")
            all_success = False

    return all_success


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔄 FDF数据更新脚本")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 步骤1: 运行账号检查
    check_success = run_account_checks()

    # 步骤2: 复制CSV文件
    copy_success = copy_csv_files()

    # 汇总结果
    print("\n" + "="*60)
    print("📋 执行结果")
    print("="*60)
    print(f"账号检查: {'✅ 成功' if check_success else '❌ 失败'}")
    print(f"文件复制: {'✅ 成功' if copy_success else '❌ 失败'}")
    print("="*60)

    if copy_success:
        print("\n✅ 数据更新完成!")
        return 0
    else:
        print("\n❌ 数据更新失败")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
