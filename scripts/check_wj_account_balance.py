import time

from web3 import Web3
from typing import List, Dict
import csv
import os
from datetime import datetime
from typing import Optional
from urllib.parse import quote

# Base网络RPC端点（免费公共节点，可替换为Alchemy或Infura的端点以提高稳定性）
BASE_RPC_URL = "https://base.gateway.tenderly.co/7f0UNrRDYc9KIKb37mopLL"

# USDC在Base网络上的合约地址
USDC_CONTRACT_ADDRESS = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"

# ERC-20标准ABI（仅包含balanceOf函数，简化版）
USDC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]


def get_single_balance_with_retry(contract, checksum_addr, addr, max_retries=5, retry_interval=5):
    """
    获取单个地址的USDC余额,支持重试机制

    Args:
        contract: USDC合约实例
        checksum_addr: 标准化地址
        addr: 原始地址
        max_retries: 最大重试次数,默认5次
        retry_interval: 重试间隔(秒),默认5秒

    Returns:
        余额(USDC),失败返回0
    """
    for attempt in range(1, max_retries + 1):
        try:
            # 调用balanceOf获取原始余额(wei-like单位)
            raw_balance = contract.functions.balanceOf(checksum_addr).call()

            # 转换为USDC单位(USDC有6位小数)
            balance_usdc = raw_balance / 10 ** 6

            if attempt > 1:
                print(f"✓ {addr} 第{attempt}次尝试成功,余额: {balance_usdc:.2f} USDC")

            return balance_usdc

        except Exception as e:
            print(f"✗ {addr} 第{attempt}/{max_retries}次尝试出错: {e}")

            # 如果不是最后一次尝试,等待后重试
            if attempt < max_retries:
                print(f"  等待{retry_interval}秒后重试...")
                time.sleep(retry_interval)

    # 所有重试都失败
    print(f"✗✗✗ {addr} 已重试{max_retries}次仍然失败,返回0")
    return 0.0


def get_usdc_balances(addresses: List[str]) -> Dict[str, float]:
    """
    查询Base网络上给定地址列表的USDC余额(带重试机制)

    Args:
        addresses: 地址列表,例如 ['0x123...', '0x456...']

    Returns:
        字典:{地址: 余额(USDC)}, 以及总余额。
    """
    # 连接到Base网络
    w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
    if not w3.is_connected():
        raise ConnectionError("无法连接到Base网络,请检查RPC端点。")

    # 创建USDC合约实例
    usdc_contract = w3.eth.contract(
        address=Web3.to_checksum_address(USDC_CONTRACT_ADDRESS),
        abi=USDC_ABI
    )

    balances = {}
    total_balance = 0.0

    for addr in addresses:
        # 标准化地址
        checksum_addr = w3.to_checksum_address(addr)

        # 使用带重试机制的方法获取余额
        balance_usdc = get_single_balance_with_retry(
            usdc_contract,
            checksum_addr,
            addr,
            max_retries=5,
            retry_interval=5
        )

        balances[addr] = balance_usdc
        total_balance += balance_usdc

    balances['total'] = total_balance
    return balances


from datetime import datetime, timedelta

import requests
import time
import random

# List of sample User-Agent strings to randomize
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    # Add more if needed
]

# Wallet list - fill this with your wallet addresses
game_wallet_list = [
    '0x2987026DBc818609a247A0041e653E5B0019a3AA',
    '0xB2695721b18F2BF5dF0639d6976F8Fb6667B1dC9',
    '0x9c48AD8B2CA62F8BcACA6496013Dd5BC65885602',
    '0x13E2D6A728BC07Fa14D6d973c9D2fa59eacf3B8f',
    '0x4c8FE056E1FBb83813918c981d9475ec429767d8',
    '0x1bD036Ebc162d2CD22CC7D225E9B784Fa1FDE125',
    '0xd1E5Eaa24b2D79f3a5eB6DFf45Ce95B45517dc02',
    '0xF15cc93d352702d595E4B7D0887Ea7B382c426B6',
    '0xAbFde8A04c43ACb0826470250b2E1B3F2D693e7f',
    '0x1018A7F4236F00F36787fAF7720A3959fc0ED54c',
    '0x29383e0455B6E7130136d20D92c9288376504EC3',
    '0x35a53Ad3530Ae5184102dd9dF1F5dD3c21d9752a',
    '0x2d99a228395D2001aAF92627d204291AA995adbe',
    '0x7b6e3b3bA03fDEFb70F627e142983bFEE327C527',
    '0x922D2918651002930816C72BaD4984ebFc214b4f',
    '0xb3A05A8c0E9D0992C196556CF3C3C3Ebf1065074',
    '0x9d81699bC27b953D250BAd645d80ae235aD2913b',
    '0x670B62634404E72F465f088b3A7e01E032B9C568',
    '0x1d52582edeC201EF6B8Ed588C1eE9e90Db9d09F7',
    '0xeed210f175757D2020bD35C1DBc15Fc8a65b60c9',
    '0x587c3743bC3EFf4A7D515B58C2B23b52615f8824',
    '0xF6E59cE6f115B5d0E6B4212fB9B5df1EEc59574C',
    '0xC5a494ce722dEB3Fc1D4C0A8b32172912A8DB403',
    '0xfbe33761507E4C4d50E790Cb35e62Ef45cc0cAd4',
    '0x571c8AD16B408A901CB684d471A1c6394D4d294f'
]
owner_address_list = [
        '0x716D631F3Bd07E5d65F3967871fB0711261419c9',
        '0xa1B9624e9bC5538A1EE46B9f3D83dc501B175D23',
        '0xDcc2D4af2c3B866226463ca50835099689Db4b0c',
        '0x7E286fE235281AA43aB5402EBC6E3dB71cba5f9d',
        '0x081c655eAd8421D5BFA7E3DE3E51719a340a64Ad',
        '0x289a694f0102c0b7d9a2e1b5e5191Cc89BEC2C44',
        '0x04C03736e8954162c7e4D02F6f8EfCb987F6023f',
        '0xC9474f1a08dA5e4E488438E74E112063eCf9ef2B',
        '0xBCf730d0dC167c0b483C5ab80A186708Ce03ca32',
        '0xC8CDf86af478544d9d4543DF15516269316eD9e2',
        '0x70c9A93db66704Dc2E0cea83BEeA695CB60aDb7e',
        '0x89c9dA85eaeb92E5131744d1127D46d936f87f07',
        '0xEa976407f284A88021C9bFde01a8Eabf3D1DE033',
        '0xF30215088bF4a8B37D9724c27A2F4e9000c3FC8D',
        '0x4eeC62c64bB213eaFEBA562E8e891fd83ACb4B23',
        '0x453E810D7efb79A5DCDe3cA18b5BA87A9bB7a716',
        '0x24a4BF08a82bf0063DcD453a56D3Ed4fD907Da63',
        '0x2F1bD5e3f2d233Cd08bEF8dDaF3899a559082C9b',
        '0x8bA558c8743db80e700a2a2eD50A92eBFf237d79',
        '0xeeD05a7eC3b36dd7DF814167003F733d6Bbbb98E',
        '0x13c43E25349A76489bA48e9189d1Ca9D1DB8c897',
        '0x8ef6BFD078939193690755787D24D4Fc05AD2733',
        '0xc2a25Dfe99796e55914BC5eAb728f7EC1D76C5C6',
        '0xdf6BAe03Ac4c83F7eF823581D57Ba0C3501C77Ed',
        '0x0550567807fD6e73215F1f4D8554a42e2d28C598'
    ]

def get_wallet_balance(wallet, max_retries=5, retry_interval=5):
    """
    获取钱包余额,支持重试机制

    Args:
        wallet: 钱包地址
        max_retries: 最大重试次数,默认5次
        retry_interval: 重试间隔(秒),默认5秒

    Returns:
        余额(USDC),失败返回0
    """
    url = f"https://api.tenero.io/v1/sportsfun/wallets/{wallet}/holdings_value"

    for attempt in range(1, max_retries + 1):
        # Randomly select a User-Agent
        user_agent = random.choice(user_agents)
        headers = {'User-Agent': user_agent}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Raise error for bad status codes
            data = response.json()

            if data['statusCode'] == 200:
                balance = data['data']['total_value_usd']
                if attempt > 1:
                    print(f"✓ {wallet} 第{attempt}次尝试成功,余额: {balance:.2f} USDC")
                return balance
            else:
                print(f"✗ {wallet} 第{attempt}/{max_retries}次尝试失败: {data['message']}")

        except requests.exceptions.Timeout:
            print(f"✗ {wallet} 第{attempt}/{max_retries}次尝试超时")

        except requests.exceptions.RequestException as e:
            print(f"✗ {wallet} 第{attempt}/{max_retries}次尝试失败: {e}")

        except Exception as e:
            print(f"✗ {wallet} 第{attempt}/{max_retries}次尝试未知错误: {e}")

        # 如果不是最后一次尝试,等待后重试
        if attempt < max_retries:
            print(f"  等待{retry_interval}秒后重试...")
            time.sleep(retry_interval)

    # 所有重试都失败
    print(f"✗✗✗ {wallet} 已重试{max_retries}次仍然失败,返回0")
    return 0


def write_balance_history(balance: float, gold_balance: float, holding_value: float,
                          csv_path: str = "check_history_wj.csv") -> None:
    """
    写入余额历史记录到CSV文件

    Args:
        balance: 链上余额
        gold_balance: 金币价值
        holding_value: 持有价值
        csv_path: CSV文件路径，默认为当前目录下的check_history.csv
    """
    # 计算总价值
    total_value = balance + gold_balance + holding_value

    # 准备数据行
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_data = {
        "时间": current_time,
        "链上余额": f"{balance:.2f}",
        "金币价值": f"{gold_balance:.2f}",
        "持有价值": f"{holding_value:.2f}",
        "总价值": f"{total_value:.2f}"
    }

    # 检查文件是否存在
    file_exists = os.path.exists(csv_path)

    # 写入CSV文件
    try:
        with open(csv_path, mode='a', newline='', encoding='utf-8-sig') as csvfile:
            # 定义表头顺序
            fieldnames = ["时间", "链上余额", "金币价值", "持有价值", "总价值"]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 如果文件不存在，写入表头
            if not file_exists:
                writer.writeheader()

            # 写入数据行
            writer.writerow(row_data)

    except PermissionError:
        print(f"错误: 无法写入文件 {csv_path}，请检查文件是否被其他程序占用")
    except Exception as e:
        print(f"错误: 写入文件时发生异常 - {str(e)}")


def read_balance_history(csv_path: str = "check_history_wj.csv") -> list:
    """
    读取余额历史记录

    Args:
        csv_path: CSV文件路径

    Returns:
        包含所有记录的列表
    """
    if not os.path.exists(csv_path):
        print(f"文件不存在: {csv_path}")
        return []

    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            records = list(reader)
            print(f"成功读取 {len(records)} 条记录")
            return records
    except Exception as e:
        print(f"错误: 读取文件时发生异常 - {str(e)}")
        return []


def calculate_percentage_change(records: list, hours: int, current_value: float) -> Optional[float]:
    """
    计算指定时间段的涨跌幅

    Args:
        records: 历史记录列表
        hours: 时间段(小时)
        current_value: 当前总价值

    Returns:
        涨跌幅百分比,如果没有找到对应时间的记录则返回None
    """
    if not records:
        return None

    try:
        current_time = datetime.now()
        target_time = current_time - timedelta(hours=hours)

        # 寻找最接近目标时间的记录
        closest_record = None
        min_time_diff = None

        for record in records:
            record_time = datetime.strptime(record["时间"], "%Y-%m-%d %H:%M:%S")
            time_diff = abs((record_time - target_time).total_seconds())

            # 只考虑目标时间之前的记录
            if record_time <= target_time:
                if min_time_diff is None or time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_record = record

        if closest_record:
            old_value = float(closest_record["总价值"])
            if old_value > 0:
                percentage_change = ((current_value - old_value) / old_value) * 100
                return percentage_change

        return None
    except Exception as e:
        print(f"计算涨跌幅时出错: {e}")
        return None


def get_yesterday_last_record(records: list) -> Optional[float]:
    """
    获取昨天的最后一条记录的总价值

    Args:
        records: 历史记录列表

    Returns:
        昨天最后一条记录的总价值,如果没有找到则返回None
    """
    if not records:
        return None

    try:
        today = datetime.now().date()
        yesterday_last_value = None

        for record in records:
            record_time = datetime.strptime(record["时间"], "%Y-%m-%d %H:%M:%S")
            record_date = record_time.date()

            # 如果是昨天的记录
            if record_date < today:
                yesterday_last_value = float(record["总价值"])

        return yesterday_last_value
    except Exception as e:
        print(f"获取昨天最后记录时出错: {e}")
        return None


def send(balance, gold_balance, holding_value):
    total = balance + gold_balance + holding_value

    # 读取历史记录并计算涨跌幅
    records = read_balance_history()

    # 计算今天相比昨天最后一次的涨跌幅
    yesterday_last = get_yesterday_last_record(records)
    if yesterday_last is not None:
        change_pct = ((total - yesterday_last) / yesterday_last) * 100
        sign = "+" if change_pct >= 0 else ""
        icon = "📈" if change_pct >= 0 else "📉"
        title = f"${total:.2f} {sign}{change_pct:.2f}%{icon}"
    else:
        title = f"${total:.2f}"

    content = f"----------------------\n余额: ${balance:.2f}\n金币: ${gold_balance:.2f}\n球员: ${holding_value:.2f}"
    message = quote(f"{title}/{content}")
    url = f"https://api.day.app/NB9EBMYHCd3mRwqaqquvP5/{message}?isArchive=1&sound=minuet&icon=https://s2.loli.net/2025/12/31/2LT4GfJ8gc59jaw.png"
    try:
        response = requests.get(url)
    except Exception as e:
        pass

# 示例使用
if __name__ == "__main__":
    owner_account_result = get_usdc_balances(owner_address_list)
    for addr, bal in owner_account_result.items():
        if addr != 'total':
            print(f"{addr} 链上地址余额 {bal:.2f} USDC")
    owner_total = owner_account_result['total']
    game_account_result = get_usdc_balances(game_wallet_list)
    for addr, bal in game_account_result.items():
        if addr != 'total':
            print(f"{addr} 游戏地址金币余额 {bal:.2f} USDC")
    game_total = game_account_result['total']
    holding_total = 0.0
    for wallet in game_wallet_list:
        balance = get_wallet_balance(wallet, max_retries=5, retry_interval=5)
        holding_total += balance
        print(f"{wallet} 持有球员价值 {balance:.2f} USDC")
        # 重试机制已内置等待,这里不需要额外sleep

    print("========================")
    print(f"链上地址余额: {owner_total:.2f} USDC")
    print(f"FDF地址金币: {game_total:.2f} USDC")
    print(f"FDF持有价值: {holding_total:.2f} USDC")
    print("========================")
    total = owner_total + game_total + holding_total
    print(f"总价值: {total:.2f} USDC")
    write_balance_history(owner_total, game_total, holding_total)
    # send(owner_total, game_total, holding_total)  # 已禁用消息发送
