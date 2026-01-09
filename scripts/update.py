#!/usr/bin/env python3
"""
FDF数据更新脚本
直接在data目录写入CSV数据
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

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
        ('check_fun_balance.py', '$FUN余额'),
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


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔄 FDF数据更新脚本")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 确保data目录存在
    DATA_DIR.mkdir(exist_ok=True)

    # 运行账号检查（直接写入data目录）
    check_success = run_account_checks()

    # 汇总结果
    print("\n" + "="*60)
    print("📋 执行结果")
    print("="*60)
    print(f"账号检查: {'✅ 成功' if check_success else '❌ 失败'}")
    print("="*60)

    if check_success:
        print("\n✅ 数据更新完成!")
        return 0
    else:
        print("\n❌ 数据更新失败")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
