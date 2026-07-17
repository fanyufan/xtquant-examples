# -*- coding: utf-8 -*-
"""
xtdata 复权因子示例

覆盖内容：
1. get_divid_factors 接口：获取复权因子数据
2. 前复权 / 后复权价格计算
3. 基于复权因子的持有期真实收益率
4. 与 get_market_data 的 dividend_type 参数结果对比

运行前提：
1. QMT/迅投终端已启动并登录。
2. 已安装 xtquant 和 pandas。
3. 复权因子数据通常只在股票上有意义，可转债和 ETF 一般不需要复权。
"""

import pandas as pd
from xtquant import xtdata


# ==================== 基础配置 ====================
STOCK_CODE = "000001.SZ"   # 平安银行（示例）
START_DATE = "20230101"
END_DATE = "20240717"


def get_dividend_factors(stock_code, start_time, end_time):
    """
    获取复权因子数据。
    不同 xtquant 版本接口可能存在差异，如果 get_divid_factors 不存在，
    可尝试 get_divid_factors 的别名或从 get_market_data 直接获取复权行情。
    """
    if not hasattr(xtdata, "get_divid_factors"):
        print("当前 xtdata 版本没有 get_divid_factors 接口，将使用 get_market_data 的复权行情对比。")
        return None

    # 下载复权因子数据（部分版本需要显式下载）
    try:
        xtdata.download_history_data(stock_code, period="1d", start_time=start_time, end_time=end_time)
    except Exception as e:
        print(f"download_history_data 提示：{e}")

    # 获取复权因子
    factors = xtdata.get_divid_factors(stock_code, start_time, end_time)
    return factors


def get_price_data(stock_code, start_time, end_time, dividend_type="none"):
    """
    通过 get_market_data 获取指定复权类型的行情数据。
    dividend_type 可选："none"（不复权）、"front"（前复权）、"back"（后复权）
    """
    # 下载数据
    xtdata.download_history_data(stock_code, period="1d", start_time=start_time, end_time=end_time)

    # 获取行情数据
    data = xtdata.get_market_data(
        stock_list=[stock_code],
        period="1d",
        start_time=start_time,
        end_time=end_time,
        dividend_type=dividend_type,
        fill_data=False
    )

    # 转换为 DataFrame
    df = pd.DataFrame({k: v.iloc[0] for k, v in data.items()})
    df = df.reset_index().rename(columns={"index": "time"})
    df = df.sort_values("time").reset_index(drop=True)
    return df


def calculate_adjusted_price(df_raw, factors, adjust_type="front"):
    """
    使用复权因子手动计算复权价格。

    假设 factors 是 DataFrame，包含字段：
    - time / date: 日期
    - factor: 复权因子

    adjust_type:
    - front: 前复权（以最新价格为基准）
    - back: 后复权（以历史价格为基准）
    """
    if factors is None or len(factors) == 0:
        return df_raw

    # 确保 factors 有统一的列名
    factors = factors.copy()
    if "date" in factors.columns and "time" not in factors.columns:
        factors = factors.rename(columns={"date": "time"})

    # 合并复权因子到原始价格数据
    df = df_raw.merge(factors[["time", "factor"]], on="time", how="left")
    df["factor"] = df["factor"].fillna(1.0)

    if adjust_type == "front":
        # 前复权价格 = 原始价格 * 前复权因子
        df["close_adj"] = df["close"] * df["factor"]
    elif adjust_type == "back":
        # 后复权价格 = 原始价格 * 后复权因子
        # 注意：这里假设 factor 已经是后复权因子；
        # 如果接口返回的是前复权因子，则需要取倒数转换。
        df["close_adj"] = df["close"] * df["factor"]
    else:
        df["close_adj"] = df["close"]

    return df


def calculate_return(df, price_col="close"):
    """计算持有期收益率。"""
    start_price = df[price_col].iloc[0]
    end_price = df[price_col].iloc[-1]
    total_return = (end_price - start_price) / start_price
    return total_return


def main():
    print("=" * 60)
    print("示例 1：获取复权因子")
    print("=" * 60)

    factors = get_dividend_factors(STOCK_CODE, START_DATE, END_DATE)
    if factors is not None:
        if isinstance(factors, pd.DataFrame):
            print(f"复权因子数据形状：{factors.shape}")
            print(factors.head(10))
        else:
            print(f"复权因子数据类型：{type(factors)}")
            print(factors)
    print()

    print("=" * 60)
    print("示例 2：获取不复权 / 前复权 / 后复权行情")
    print("=" * 60)

    df_none = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="none")
    df_front = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="front")
    df_back = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="back")

    print("不复权前 5 行：")
    print(df_none[["time", "open", "high", "low", "close", "volume"]].tail(5))
    print()

    print("前复权前 5 行：")
    print(df_front[["time", "close"]].tail(5))
    print()

    print("后复权前 5 行：")
    print(df_back[["time", "close"]].tail(5))
    print()

    print("=" * 60)
    print("示例 3：基于不同复权方式计算持有期收益率")
    print("=" * 60)

    ret_none = calculate_return(df_none, price_col="close")
    ret_front = calculate_return(df_front, price_col="close")
    ret_back = calculate_return(df_back, price_col="close")

    print(f"不复权收益率：{ret_none:.4%}")
    print(f"前复权收益率：{ret_front:.4%}")
    print(f"后复权收益率：{ret_back:.4%}")
    print()

    print("=" * 60)
    print("示例 4：手动用复权因子计算前复权收盘价（与 get_market_data 对比）")
    print("=" * 60)

    if factors is not None and isinstance(factors, pd.DataFrame) and not factors.empty:
        df_manual = calculate_adjusted_price(df_none, factors, adjust_type="front")
        df_compare = df_front[["time", "close"]].rename(columns={"close": "close_front_api"})
        df_compare = df_manual[["time", "close", "close_adj"]].merge(df_compare, on="time", how="left")
        df_compare["diff"] = df_compare["close_adj"] - df_compare["close_front_api"]
        print(df_compare.tail(10))
        print(f"最大差异：{df_compare['diff'].abs().max():.6f}")
    else:
        print("当前无法获取复权因子，跳过手动对比。")
    print()

    print("提示：")
    print("  1. 如果 get_divid_factors 不存在，说明你的 xtquant 版本较旧。")
    print("  2. 复权因子主要用于股票，可转债/ETF 通常不需要复权。")
    print("  3. 前复权以最新价为基准，适合分析当前视角；")
    print("     后复权以历史发行价为基准，适合计算长期真实收益。")


if __name__ == "__main__":
    main()
