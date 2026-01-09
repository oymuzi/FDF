#!/usr/bin/env python3
"""
FDF自动检查和提交脚本
每小时运行一次：更新数据 + 检查变更 + 自动提交推送
每个小时的 58分45秒 开始执行
"""

import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# fdf项目目录
FDF_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = FDF_DIR / 'scripts'
DATA_DIR = FDF_DIR / 'data'


def calculate_next_run_time():
    """计算下一次执行时间(每个小时的58分45秒)"""
    now = datetime.now()

    # 计算下一个小时的58分45秒
    if now.minute < 58 or (now.minute == 58 and now.second < 45):
        # 如果还没到当前小时的58:45，就在当前小时执行
        next_run = now.replace(minute=58, second=45, microsecond=0)
    else:
        # 否则在下一个小时执行
        next_run = (now.replace(minute=58, second=45, microsecond=0) + timedelta(hours=1))

    return next_run


def run_update():
    """运行数据更新脚本"""
    script_path = SCRIPTS_DIR / 'update.py'

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"[{start_time}] 开始数据更新")
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
            print("✅ 数据更新成功")
            return True
        else:
            print(f"❌ 数据更新失败 (返回码: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print("❌ 数据更新超时")
        return False
    except Exception as e:
        print(f"❌ 数据更新异常: {e}")
        return False


def check_and_commit():
    """检查是否有数据变更，如果有则提交并推送"""
    print(f"\n{'='*60}")
    print("检查数据变更...")
    print(f"{'='*60}")

    try:
        # 检查data目录是否有变更
        result = subprocess.run(
            ['git', 'diff', '--quiet', 'data/'],
            cwd=str(FDF_DIR),
            capture_output=True
        )

        # 如果有变更（返回码非0）
        if result.returncode != 0:
            print("✅ 检测到数据变更，开始提交...")

            # 添加data目录
            subprocess.run(['git', 'add', 'data/'], cwd=str(FDF_DIR))

            # 提交
            commit_msg = f"🤖自动更新数据"
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=str(FDF_DIR)
            )
            print("✅ 数据已提交")

            # 推送
            print("⬆️  推送到远程仓库...")
            push_result = subprocess.run(
                ['git', 'push'],
                cwd=str(FDF_DIR),
                capture_output=True,
                text=True
            )

            if push_result.returncode == 0:
                print("✅ 推送成功")
                return True
            else:
                print(f"❌ 推送失败: {push_result.stderr}")
                return False
        else:
            print("ℹ️  没有数据变更，跳过提交")
            return True

    except Exception as e:
        print(f"❌ 提交异常: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔄 FDF 自动检查和提交服务")
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("执行频率: 每小时 58分45秒 运行一次")
    print("="*60)

    print("\n✅ 定时任务已启动，等待到下一个执行时间...")
    print("按 Ctrl+C 停止...")

    # 持续运行
    while True:
        try:
            # 计算下次执行时间
            next_run = calculate_next_run_time()
            now = datetime.now()
            wait_seconds = (next_run - now).total_seconds()

            print(f"\n⏰ 下次执行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏳ 等待: {int(wait_seconds)}秒 ({int(wait_seconds/60)}分{int(wait_seconds%60)}秒)")

            # 等待到下次执行时间
            time.sleep(wait_seconds)

            # 执行更新和提交
            update_success = run_update()
            if update_success:
                check_and_commit()

        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断，停止定时任务...")
            break
        except Exception as e:
            print(f"\n❌ 定时任务异常: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
