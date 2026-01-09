#!/usr/bin/env python3
"""
检测钱包地址的 $FUN 余额
支持 MZ 和 George 的所有地址
"""

import subprocess
import json
from typing import List, Dict
from datetime import datetime

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

# George 的钱包地址
GEORGE_ADDRESSES = [
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

# $FUN 合约地址（Base网络）
FUN_CONTRACT = '0x16EE7ecAc70d1028E7712751E2Ee6BA808a7dd92'


def get_fun_balance(address: str) -> float:
    """
    获取单个地址的 $FUN 余额
    使用 cast 命令调用合约
    """
    try:
        cmd = [
            'cast', 'call',
            FUN_CONTRACT,
            'balanceOf(address)(uint256)',
            address
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # 解析输出，提取余额
            output = result.stdout.strip()
            # 余额格式类似：1234567890000000000
            # $FUN 有 18 位小数
            balance_wei = int(output)
            balance = balance_wei / 10**18
            return balance
        else:
            print(f"✗ {address[:10]}... 查询失败")
            return 0.0

    except subprocess.TimeoutExpired:
        print(f"✗ {address[:10]}... 查询超时")
        return 0.0
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

    # 如果总数都为0，返回1（无变更）
    if mz_total == 0 and george_total == 0:
        print("ℹ️  两人余额均为 0，无数据变更")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
