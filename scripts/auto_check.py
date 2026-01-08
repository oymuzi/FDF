import schedule
import time
import subprocess
import sys
import os
import random
from datetime import datetime, timedelta


def get_random_offset():
    """
    每次生成新的随机偏移时间(30-90秒)
    确保每次执行时间都不一样
    """
    return random.randint(30, 90)


def calculate_next_run_time():
    """计算下一次执行时间(每小时的随机时间)"""
    now = datetime.now()

    # 每次生成新的随机偏移
    offset_seconds = get_random_offset()

    # 计算下一个小时的00:XX时间
    if now.minute < 1:
        # 如果在整点附近,就在当前小时执行
        next_hour = now.replace(minute=0, second=0, microsecond=0)
    else:
        # 否则在下一个小时执行
        next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))

    # 添加随机偏移秒数
    next_run = next_hour + timedelta(seconds=offset_seconds)

    return next_run


def run_script():
    """执行目标Python脚本的函数"""
    script_path = "check_account_balance.py"

    # 记录开始时间
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{start_time}] 开始执行脚本: {script_path}")

    try:
        # 执行Python脚本
        result = subprocess.run([sys.executable, script_path],
                                capture_output=True,
                                text=True,
                                encoding='utf-8')

        # 输出脚本的执行结果
        if result.stdout:
            print("脚本输出:")
            print(result.stdout)

        if result.stderr:
            print("脚本错误:")
            print(result.stderr)

        # 检查返回码
        if result.returncode == 0:
            print(f"✅ 脚本执行成功 (返回码: {result.returncode})")
        else:
            print(f"❌ 脚本执行失败 (返回码: {result.returncode})")

    except FileNotFoundError:
        print(f"❌ 错误: 找不到脚本文件 {script_path}")
    except Exception as e:
        print(f"❌ 执行脚本时发生错误: {str(e)}")

    # 记录结束时间
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{end_time}] 脚本执行完成\n")


def main():
    """主函数，设置定时任务"""
    print("=== Python 定时任务调度器 ===")
    print("目标脚本: check_account_balance.py")
    print("执行频率: 每小时执行一次(整点后30-90秒之间的随机时间)")
    print("=" * 40)

    # 立即执行一次（可选）
    print("正在执行第一次任务...")
    run_script()

    print("定时任务已启动，按 Ctrl+C 停止...")

    # 持续运行，计算并等待下次执行时间
    while True:
        try:
            # 计算下次执行时间
            next_run = calculate_next_run_time()
            now = datetime.now()
            wait_seconds = (next_run - now).total_seconds()

            if wait_seconds > 0:
                print(f"\n下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"等待时间: {int(wait_seconds)}秒 ({int(wait_seconds/60)}分{wait_seconds%60:.0f}秒)")

                # 等待到下次执行时间
                time.sleep(wait_seconds)

                # 执行脚本
                run_script()
            else:
                # 如果计算时间已过,立即执行并重新计算
                print("执行时间已到,开始执行...")
                run_script()

        except KeyboardInterrupt:
            print("\n用户中断，停止定时任务...")
            break
        except Exception as e:
            print(f"定时任务异常: {str(e)}")
            time.sleep(60)


if __name__ == "__main__":
    main()