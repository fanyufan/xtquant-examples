# -*- coding: utf-8 -*-
"""
xtdata 实时行情订阅示例
覆盖：A股股票、可转债、ETF
类型：实时 tick / 分时 / 五档盘口

运行前提：
1. 已安装 xtquant 包，QMT 终端已启动并登录。
2. 实时订阅需要保持程序运行，回调函数会在新数据到达时被触发。
3. 本示例运行 30 秒后自动退出，实际生产中可改为无限循环或按条件退出。
"""

import time
from xtquant import xtdata


# ==================== 基础配置 ====================
STOCK_CODE = "000001.SZ"          # 平安银行
CONVERTIBLE_BOND_CODE = "128136.SZ"  # 可转债示例
ETF_CODE = "510050.SH"            # 上证50ETF

# 订阅周期：tick（逐笔）、1m（1分钟）、5m（5分钟）等
PERIOD = "tick"

# 运行时长（秒）
RUN_SECONDS = 30


def on_tick(data):
    """
    tick 回调函数。
    data 格式：{ stock_code: { field: value } }
    """
    for code, fields in data.items():
        print(f"[TICK] {code} 时间={fields.get('time')} 最新价={fields.get('lastPrice')} 成交量={fields.get('volume')}")


def on_bar(data):
    """
    分钟/日线回调函数。
    data 格式：{ stock_code: { field: value } }
    """
    for code, fields in data.items():
        print(f"[BAR] {code} 时间={fields.get('time')} 开={fields.get('open')} 高={fields.get('high')} 低={fields.get('low')} 收={fields.get('close')}")


def main():
    print("=" * 60)
    print(f"开始订阅实时行情，周期={PERIOD}，运行 {RUN_SECONDS} 秒后自动退出")
    print("=" * 60)

    # 选择回调函数：tick 用 on_tick，分钟线用 on_bar
    callback = on_tick if PERIOD == "tick" else on_bar

    # 订阅多个标的
    subscribe_codes = [STOCK_CODE, CONVERTIBLE_BOND_CODE, ETF_CODE]
    for code in subscribe_codes:
        print(f"[订阅] {code}")
        xtdata.subscribe_quote(code, period=PERIOD, callback=callback)

    # 阻塞运行，等待数据回调
    print("等待实时推送中，请查看输出...")
    time.sleep(RUN_SECONDS)

    # 取消订阅（可选，程序退出时会自动清理）
    for code in subscribe_codes:
        xtdata.unsubscribe_quote(code)
        print(f"[取消订阅] {code}")

    print("示例运行结束。")


if __name__ == "__main__":
    main()
