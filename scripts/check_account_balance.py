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
import json

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
    "0xE64f5c33AefCfA536DdB9b726b6418D61757dC60",
    "0xeC39b33140cDb18c4C07ec5a0AC088651Ddcb574",
    "0xad81B5259f7EEfADa44fC64BE639C2453cEeB753",
    "0x363AF1939E06dA74e39E1a78C7e0754DA3EfE162",
    "0xCaf2A5D353CF0F3CadeC75E97b8c8196bc4C64fb",
    "0x04f24C62A4e2589f41648C1197fc69Dce0a95A1e",
    "0x4BcD08FC59718FeCA13F0e49ceee0Cc34c9e0C59",
    "0x0444A04f34c453CEc92C592126DFCc6927E948Bc",
    "0xCA786C4F1c446DD6F80595e2a183365feB0116Df",
    "0x926506E0b3816cE36C73528E267f4112c1EbF4c9",
    "0xE4d70a90B00C9798013ab906d295F3CDBdc77660",
    "0x50f14C2dD5be1730595FC4Db15E674EecDB708F8",
    "0x3418695BCa8A0879E2bE34BB5B7C588331aeEDea",
    "0x4F42b78aD9834fB5fDEE9A0Da66fa2b50614cc48",
    "0xA20Dc402f93Be90FF9479c0c0cF06d3006DD8F97",
    "0x7b5e7AD72C68b4424650Ef9358D25EDE081f25c8",
    "0xd7635A79d9F5348953062B13560c1e5A2c6a4754",
    "0x2B66b5D3186070E25330b3451bFBf3513105e772",
    "0xc564b9695A403162fEF3Ac8A15C2d2FeA4EBE468",
    "0x4fD3516adFD7e607BD894B8fD88fB71c02336966",
    "0xb3856614D3445C41c55C82fdcf2c5196c01D4fFe",
    "0x43b6Dcf98923555Bbd615E547a4A94a584627A47",
    "0x69138742bEfc4846b87497a7cff3f0EF5Aa8d463",
    "0x61a5f75C4390b5ecfB381630634Ac973E1701a99",
    "0x2C4388D92b0DD765CC01365DB34C90CeD93f3362",
    "0x0F52F8379CC6CCA91f2AA63c03129a971d2d02fb",
    "0xFA1CEc2EaaCeea4d5471C07bF7F406DeB621D859",
]
owner_address_list = [
        "0x7a8ab746cce1e1420d8ce01b35bb346384161111",
        "0x3824263A4556f6911Aa40Fe5AC595d990F064417",
        "0x382D9296b44b7B4739De7Dc9d3f498486a6fb963",
        "0x0764f7411F085f46852d5BCf3744F5A6EB2C4063",
        "0xC96A8f7bd61F9AB29C38350af340e70BB4FF5A3a",
        "0x4dB380f1162e4c8B25F5E20b3C77E43e4d340876",
        "0x0B7F314d439B80665daE443F1d69Ea164a6B82ee",
        "0xd065DF74Cea804a94389AB2824D4f26fB44BD6cA",
        "0xad0bE3E7103c950C149150bD18d4502fF4e99E42",
        "0x0485A75970FEFaB7Be120F548737CD6B4b2B5439",
        "0x9d509DE831CB84b8fB39e28eC4218E361d0Bfc29",
        "0xa48CC299513f1bb14C1DF76183f029bE957688f1",
        "0x00d28e56AEcaFEC3423f92Fa4e9f361f092E4323",
        "0xd0f91524C0F7fa2767a783F92d795e2d3ae63402",
        "0xE36485207487e151c108a29ddA428D5C94aE83f0",
        "0x91c096b314B789CB71aE19D5640BDA0767A7a0a4",
        "0x6eA890D123A6F5DB9acA2BC936748Ec5d87c51DF",
        "0x3923A50b5Bb86a3230e1f496BC111D9326ce9d76",
        "0x55d040A29380a9f73305421c18D5632Fb93772E6",
        "0xF96Ee0791863149b1c0F4862Fa334853c63aBd66",
        "0x2491e8D78a3c2C8C84d65Ad4952E6A6641BCa090",
        "0x87E2F922d409Ce3f61Eb260e5d6761B046bb4e4D",
        "0xbea7cD35Eed114eA2C0016e6448BeC1F675400Fb",
        "0x9C969cd78cA4Dd0c96CaDcdC1808F84e35B6B8D3",
        "0x0ef2AAe9c4eD0612c990C22bFB47Afd3c950f933",
        "0xC2795bc2357d209f6376D452FDFe895b9B7A4495",
        "0x8910f40422B4E0605B409Af677EF6c1508898252",
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
                          csv_path: str = "check_history.csv") -> None:
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


def read_balance_history(csv_path: str = "check_history.csv") -> list:
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

    # 读取历史记录并计算涨跌幅（从data目录读取完整历史）
    records = read_balance_history("data/mz_history.csv")

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
    url = f"https://api.day.app/89ADUXPYHnYeoW85XFAsaD/{message}?isArchive=1&sound=minuet&icon=https://s2.loli.net/2025/12/31/2LT4GfJ8gc59jaw.png"
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
    send(owner_total, game_total, holding_total)
