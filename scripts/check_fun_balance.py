#!/usr/bin/env python3
"""
检测钱包地址的 $FUN 余额
支持 MZ 和 George 的所有地址
"""

from web3 import Web3
import json
from typing import List, Dict
from datetime import datetime

# Base网络RPC端点
BASE_RPC_URL = "https://base.gateway.tenderly.co/7f0UNrRDYc9KIKb37mopLL"

# $FUN 合约地址（Base网络）
FUN_CONTRACT = '0x16EE7ecAc70d1028E7712751E2Ee6BA808a7dd92'

# ERC-20 balanceOf ABI
FUN_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

# MZ 的钱包地址
MZ_ADDRESSES = [
    '0xE64f5c33AefCfA536DdB9b726b6418D61757dC60',
    '0xeC39b33140cDb18c4C07ec5a0AC088651Ddcb574',
    '0xad81B5259f7EEfADa44fC64BE639C2453cEeB753',
    '0x363AF1939E06dA74e39E1a78C7e0754DA3EfE162',
    '0xCaf2A5D353CF0F3CadeC75E97b8c8196bc4C64fb',
    '0x04f24C62A4e2589f41648C1197fc69Dce0a95A1e',
    '0x4BcD08FC59718FeCA13F0e49ceee0Cc34c9e0C59',
    '0x0444A04f34c453CEc92C592126DFCc6927E948Bc',
    '0xCA786C4F1c446DD6F80595e2a183365feB0116Df',
    '0x926506E0b3816cE36C73528E267f4112c1EbF4c9',
    '0xE4d70a90B00C9798013ab906d295F3CDBdc77660',
    '0x50f14C2dD5be1730595FC4Db15E674EecDB708F8',
    '0x3418695BCa8A0879E2bE34BB5B7C588331aeEDea',
    '0x4F42b78aD9834fB5fDEE9A0Da66fa2b50614cc48',
    '0xA20Dc402f93Be90FF9479c0c0cF06d3006DD8F97',
    '0x7b5e7AD72C68b4424650Ef9358D25EDE081f25c8',
    '0xd7635A79d9F5348953062B13560c1e5A2c6a4754',
    '0x2B66b5D3186070E25330b3451bFBf3513105e772',
    '0xc564b9695A403162fEF3Ac8A15C2d2FeA4EBE468',
    '0x4fD3516adFD7e607BD894B8fD88fB71c02336966',
    '0xb3856614D3445C41c55C82fdcf2c5196c01D4fFe',
    '0x43b6Dcf98923555Bbd615E547a4A94a584627A47',
    '0x69138742bEfc4846b87497a7cff3f0EF5Aa8d463',
    '0x61a5f75C4390b5ecfB381630634Ac973E1701a99',
    '0x2C4388D92b0DD765CC01365DB34C90CeD93f3362',
    '0x0F52F8379CC6CCA91f2AA63c03129a971d2d02fb',
    '0xFA1CEc2EaaCeea4d5471C07bF7F406DeB621D859'
]

# George 的钱包地址（游戏地址）
GEORGE_ADDRESSES = [
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

# $FUN 合约地址（Base网络）
FUN_CONTRACT = '0x16EE7ecAc70d1028E7712751E2Ee6BA808a7dd92'


def get_fun_balance(address: str, contract) -> float:
    """
    获取单个地址的 $FUN 余额
    使用 web3.py 调用合约
    """
    try:
        # 标准化地址
        checksum_addr = Web3.to_checksum_address(address)

        # 调用 balanceOf
        balance_wei = contract.functions.balanceOf(checksum_addr).call()

        # $FUN 有 18 位小数
        balance = balance_wei / 10**18
        return balance

    except Exception as e:
        print(f"✗ {address[:10]}... 错误: {e}")
        return 0.0


def check_all_balances(addresses: List[str]) -> Dict[str, float]:
    """
    检查所有地址的 $FUN 余额
    返回 {地址: 余额} 字典
    """
    balances = {}

    print(f"\n开始检查 {len(addresses)} 个地址的 $FUN 余额...")

    for i, address in enumerate(addresses, 1):
        balance = get_fun_balance(address)
        if balance > 0:
            balances[address] = balance
            print(f"[{i}/{len(addresses)}] {address[:10]}... : {balance:.2f} $FUN")
        else:
            print(f"[{i}/{len(addresses)}] {address[:10]}... : 0 $FUN")

    return balances


def main():
    """主函数"""
    print("="*60)
    print("🪙 $FUN 余额检测")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 检查 MZ 的余额
    print("\n📊 检查 MZ 的地址...")
    mz_balances = check_all_balances(MZ_ADDRESSES)
    mz_total = sum(mz_balances.values())

    print(f"\n✅ MZ 总计: {mz_total:.2f} $FUN")
    print(f"   有余额地址数: {len(mz_balances)}")

    # 检查 George 的余额
    print("\n📊 检查 George 的地址...")
    george_balances = check_all_balances(GEORGE_ADDRESSES)
    george_total = sum(george_balances.values())

    print(f"\n✅ George 总计: {george_total:.2f} $FUN")
    print(f"   有余额地址数: {len(george_balances)}")

    # 保存结果到 JSON
    result = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'mz': {
            'total': mz_total,
            'addresses': {addr: bal for addr, bal in mz_balances.items() if bal > 0}
        },
        'george': {
            'total': george_total,
            'addresses': {addr: bal for addr, bal in george_balances.items() if bal > 0}
        }
    }

    with open('data/fun_balance.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 结果已保存到 data/fun_balance.json")
    print("="*60)

    # 无论余额是否为0，都返回0（成功）
    # 这样即使没有$FUN余额，也不会阻止主更新流程
    return 0


if __name__ == '__main__':
    exit(main())
