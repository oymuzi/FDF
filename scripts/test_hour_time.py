#!/usr/bin/env python3
"""
测试整点时间函数
"""
from datetime import datetime, timedelta

def get_current_hour_time():
    """
    获取当前整点时间
    如果分钟数>=30,返回下一小时整点;否则返回当前小时整点
    """
    now = datetime.now()
    if now.minute >= 30:
        # 下一小时整点
        return (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        # 当前小时整点
        return now.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")


def test_time_logic():
    """测试不同时间点的转换逻辑"""
    test_cases = [
        ("2026-01-12 09:15:00", "2026-01-12 09:00:00", "15分 -> 当前整点"),
        ("2026-01-12 09:30:00", "2026-01-12 10:00:00", "30分 -> 下一整点"),
        ("2026-01-12 09:45:00", "2026-01-12 10:00:00", "45分 -> 下一整点"),
        ("2026-01-12 09:01:00", "2026-01-12 09:00:00", "01分 -> 当前整点"),
        ("2026-01-12 09:59:00", "2026-01-12 10:00:00", "59分 -> 下一整点"),
        ("2026-01-12 09:00:00", "2026-01-12 09:00:00", "00分 -> 当前整点"),
    ]

    print("=" * 70)
    print("时间转换逻辑测试")
    print("=" * 70)

    for input_time_str, expected_str, description in test_cases:
        input_time = datetime.strptime(input_time_str, "%Y-%m-%d %H:%M:%S")

        # 模拟函数逻辑
        if input_time.minute >= 30:
            result = (input_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            result = input_time.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

        status = "✓" if result == expected_str else "✗"
        print(f"{status} {description}")
        print(f"  输入: {input_time_str} => 输出: {result}")
        if result != expected_str:
            print(f"  期望: {expected_str}")
        print()

    print("=" * 70)
    print("当前时间测试")
    print("=" * 70)
    now = datetime.now()
    print(f"当前实际时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"脚本记录时间: {get_current_hour_time()}")
    print("=" * 70)


if __name__ == "__main__":
    test_time_logic()
