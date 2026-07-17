# -*- coding: utf-8 -*-
"""
xtdata 历史行情数据示例
覆盖：A股股票、可转债、ETF
频率：日 K 线、分钟 K 线

运行前提：
1. 已安装 xtquant 包（QMT 内置 Python 或自行 pip 安装）。
2. QMT/迅投终端已启动并登录。
3. 首次运行某个品种时，xtdata 会先从服务端下载数据到本地缓存，
   请保持网络畅通并耐心等待。
"""

import time
import pandas as pd
from xtquant import xtdata


# ==================== 基础配置 ====================
# 品种示例：股票、可转债、ETF
# 代码规则：{代码}.{市场}，市场 SZ=深圳，SH=上海
STOCK_CODE = "000001.SZ"          # 平安银行（示例）
CONVERTIBLE_BOND_CODE = "128136.SZ"  # 可转债示例（请根据实际品种替换）
ETF_CODE = "510050.SH"            # 上证50ETF

# 时间范围（字符串格式：YYYYMMDD 或 YYYYMMDDhhmmss）
START_DATE = "20240101"
END_DATE = "20240717"


def fetch_history_kline(stock_code, period="1d", start_time="", end_time=""):
    """
    获取历史 K 线数据。

    参数：
        stock_code: 标的代码，如 "000001.SZ"
        period: 周期，可选 "1d"（日K）、"1m"（1分钟）等
        start_time/end_time: 时间范围

    返回：
        DataFrame，字段包含 time、open、high、low、close、volume 等
    """
    # 1. 先下载数据到本地缓存（如果本地已有，会较快返回）
    print(f"[下载] {stock_code} 周期={period}")
    xtdata.download_history_data(stock_code, period=period, start_time=start_time, end_time=end_time)

    # 2. 从本地读取数据
    # get_market_data 返回的是 dict，key 为字段名，value 为 DataFrame
    data = xtdata.get_market_data(
        stock_list=[stock_code],
        period=period,
        start_time=start_time,
        end_time=end_time,
        dividend_type="front",  # 前复权
        fill_data=False
    )

    # 将 dict 转置为常见的 DataFrame 格式（行：时间，列：字段）
    df = pd.DataFrame({k: v.iloc[0] for k, v in data.items()})
    df = df.reset_index().rename(columns={"index": "time"})
    return df


def main():
    print("=" * 60)
    print("示例 1：A 股股票日 K 线")
    print("=" * 60)
    df_stock_daily = fetch_history_kline(STOCK_CODE, period="1d", start_time=START_DATE, end_time=END_DATE)
    print(df_stock_daily.tail(5))
    print()

    print("=" * 60)
    print("示例 2：A 股股票 1 分钟 K 线")
    print("=" * 60)
    df_stock_min = fetch_history_kline(STOCK_CODE, period="1m", start_time="20240701", end_time="20240717")
    print(df_stock_min.tail(5))
    print()

    print("=" * 60)
    print("示例 3：可转债日 K 线")
    print("=" * 60)
    df_bond_daily = fetch_history_kline(CONVERTIBLE_BOND_CODE, period="1d", start_time=START_DATE, end_time=END_DATE)
    print(df_bond_daily.tail(5))
    print()

    print("=" * 60)
    print("示例 4：ETF 日 K 线")
    print("=" * 60)
    df_etf_daily = fetch_history_kline(ETF_CODE, period="1d", start_time=START_DATE, end_time=END_DATE)
    print(df_etf_daily.tail(5))
    print()

    # 保存到本地 CSV，方便查看
    df_stock_daily.to_csv("stock_000001_daily.csv", index=False, encoding="utf-8-sig")
    df_bond_daily.to_csv("bond_128136_daily.csv", index=False, encoding="utf-8-sig")
    df_etf_daily.to_csv("etf_510050_daily.csv", index=False, encoding="utf-8-sig")
    print("已保存 CSV 文件到当前目录，方便你查看数据结构。")


if __name__ == "__main__":
    main()
