# -*- coding: utf-8 -*-
"""
xtdata 不同复权方式示例

展示 get_market_data 的 dividend_type 参数：
- none        不复权
- front       前复权
- back        后复权
- front_ratio 等比前复权
- back_ratio  等比后复权

注意：dividend_type 只对 K 线数据有效，对 tick 等其他周期数据无效。

运行前提：QMT 终端已启动并登录。
"""

import pandas as pd
from xtquant import xtdata


STOCK_CODE = "000001.SZ"
START_DATE = "20240101"
END_DATE = "20240717"


def get_price_data(stock_code, start_time, end_time, dividend_type="none"):
    """获取指定复权类型的日 K 数据。"""
    xtdata.download_history_data(stock_code, period="1d", start_time=start_time, end_time=end_time)
    data = xtdata.get_market_data(
        stock_list=[stock_code],
        period="1d",
        start_time=start_time,
        end_time=end_time,
        dividend_type=dividend_type,
        fill_data=False,
    )
    df = pd.DataFrame({k: v.iloc[0] for k, v in data.items()})
    if "time" not in df.columns:
        df = df.reset_index().rename(columns={"index": "time"})
    df = df.sort_values("time").reset_index(drop=True)
    return df


def calculate_return(df, price_col="close"):
    """计算持有期收益率。"""
    start, end = df[price_col].iloc[0], df[price_col].iloc[-1]
    return (end - start) / start


def main():
    # 获取 5 种复权方式的数据
    df_none = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="none")
    df_front = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="front")
    df_back = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="back")
    df_front_ratio = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="front_ratio")
    df_back_ratio = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="back_ratio")

    # 展示最后 5 个交易日的收盘价
    print("不同复权方式收盘价对比（最后 5 个交易日）：")
    compare = pd.DataFrame({
        "time": df_none["time"],
        "none": df_none["close"],
        "front": df_front["close"],
        "back": df_back["close"],
        "front_ratio": df_front_ratio["close"],
        "back_ratio": df_back_ratio["close"],
    })
    print(compare.tail(5))
    print()

    # 展示不同复权方式的持有期收益率
    print("持有期收益率对比：")
    print(f"  不复权 (none):           {calculate_return(df_none):.4%}")
    print(f"  前复权 (front):          {calculate_return(df_front):.4%}")
    print(f"  后复权 (back):           {calculate_return(df_back):.4%}")
    print(f"  等比前复权 (front_ratio): {calculate_return(df_front_ratio):.4%}")
    print(f"  等比后复权 (back_ratio):  {calculate_return(df_back_ratio):.4%}")
    print()

    # 展示复权系数（相对不复权的比例）
    print("复权系数（相对不复权收盘价的比例，最后 5 个交易日）：")
    ratio = pd.DataFrame({
        "time": df_none["time"],
        "front_factor": df_front["close"] / df_none["close"],
        "back_factor": df_back["close"] / df_none["close"],
        "front_ratio_factor": df_front_ratio["close"] / df_none["close"],
        "back_ratio_factor": df_back_ratio["close"] / df_none["close"],
    })
    print(ratio.tail(5))
    print()

    # 说明
    print("说明：")
    print("  - dividend_type 只对 K 线数据（1m/5m/1d 等）有效，对 tick 数据无效。")
    print("  - 前复权/后复权：加减法调整，保持价格连续性。")
    print("  - 等比前复权/等比后复权：乘除法调整，保持收益率一致性。")
    print("  - 前复权适合分析当前视角，后复权适合计算长期真实收益。")


if __name__ == "__main__":
    main()
