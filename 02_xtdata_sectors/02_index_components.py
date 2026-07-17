# -*- coding: utf-8 -*-
"""
xtdata 指数成分股示例

覆盖接口：
- get_index_stock_list：获取指数成分股（部分 xtquant 版本提供）
- get_stock_list_in_sector：指数通常也作为板块存储，可用此接口获取
- 结合 get_market_data 获取成分股的最新行情

运行前提：
1. QMT/迅投终端已启动并登录。
2. 指数数据需要对应权限，部分券商可能对某些指数数据有限制。
3. 不同 xtquant 版本接口差异较大，本示例已做兼容处理。
"""

import pandas as pd
from xtquant import xtdata


# ==================== 基础配置 ====================
# 指数代码示例
# 注意：部分版本需要把指数名称（如 "沪深300"）当作板块名传入 get_stock_list_in_sector
INDEX_CODES = {
    "沪深300": "000300.SH",
    "中证500": "000905.SH",
    "上证50":  "000016.SH",
    "创业板指": "399006.SZ",   # 创业板指，如需要创业板50请改为 "创业板50" / "399673.SZ"
    "科创50":  "000688.SH",
}


def get_index_components(index_name, index_code):
    """
    兼容获取指数成分股。
    尝试顺序：
    1. xtdata.get_index_stock_list(index_code)
    2. xtdata.get_stock_list_in_sector(index_code)
    3. xtdata.get_stock_list_in_sector(index_name)
    """
    # 1. 尝试专用接口（如果存在）
    if hasattr(xtdata, "get_index_stock_list"):
        try:
            stocks = xtdata.get_index_stock_list(index_code)
            if stocks:
                return stocks, "get_index_stock_list"
        except Exception as e:
            print(f"  get_index_stock_list({index_code}) 失败：{e}")

    # 2. 尝试把指数代码当作板块名
    try:
        stocks = xtdata.get_stock_list_in_sector(index_code)
        if stocks:
            return stocks, f"get_stock_list_in_sector({index_code})"
    except Exception as e:
        print(f"  get_stock_list_in_sector({index_code}) 失败：{e}")

    # 3. 尝试把指数名称当作板块名
    try:
        stocks = xtdata.get_stock_list_in_sector(index_name)
        if stocks:
            return stocks, f"get_stock_list_in_sector({index_name})"
    except Exception as e:
        print(f"  get_stock_list_in_sector({index_name}) 失败：{e}")

    return [], ""


def demo_index_components(index_name, index_code):
    """获取指数成分股。"""
    print("=" * 60)
    print(f"示例：{index_name} ({index_code}) 成分股")
    print("=" * 60)

    stocks, method = get_index_components(index_name, index_code)
    print(f"使用接口：{method if method else '未找到可用接口'}")
    print(f"指数 {index_name} 共有 {len(stocks)} 只成分股")
    print(f"前 20 只：{stocks[:20]}")
    print()

    return stocks


def demo_index_components_quote(stocks, period="1d", count=5):
    """获取成分股的最新行情快照。"""
    print("=" * 60)
    print(f"示例：获取前 {count} 只成分股的最新 {period} 行情")
    print("=" * 60)

    target_stocks = stocks[:count]

    # 下载并获取行情数据
    for code in target_stocks:
        xtdata.download_history_data(code, period=period, start_time="", end_time="")

    data = xtdata.get_market_data(
        stock_list=target_stocks,
        period=period,
        dividend_type="front",
        fill_data=False
    )

    # 转换为 DataFrame
    # 兼容处理：如果字段中已包含 time，则直接 reset_index(drop=True)；否则把 index 作为 time
    df = pd.DataFrame({k: v.iloc[0] for k, v in data.items()})
    if "time" in df.columns:
        df = df.reset_index(drop=True)
    else:
        df = df.reset_index().rename(columns={"index": "time"})
    print(df)
    print()


def main():
    for name, code in INDEX_CODES.items():
        stocks = demo_index_components(name, code)

        # 只对沪深300演示行情快照，避免所有指数都下载一次太慢
        if name == "沪深300":
            demo_index_components_quote(stocks, period="1d", count=5)

    print("提示：如果某个指数返回空列表，请确认指数代码正确，")
    print("      并检查 QMT 终端是否已登录且具备对应指数数据权限。")


if __name__ == "__main__":
    main()
