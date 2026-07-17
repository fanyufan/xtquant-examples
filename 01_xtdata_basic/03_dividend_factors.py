# -*- coding: utf-8 -*-
"""
xtdata 复权因子示例

覆盖内容：
1. 获取复权因子 get_divid_factors（完整历史）
2. 获取不复权 / 前复权 / 后复权行情
3. 用复权因子手动计算前复权 / 后复权价格
4. 计算不同复权方式的持有期收益率
5. 解释 dr 的含义和除权日参考价计算

运行前提：QMT 终端已启动并登录。
"""

import pandas as pd
from xtquant import xtdata


STOCK_CODE = "000001.SZ"
START_DATE = "20230101"
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


def get_dividend_factors(stock_code):
    """
    获取上市以来所有除权除息数据。
    注意：必须获取完整历史，才能正确计算累积复权因子。

    参数说明：
    - start_time=""、end_time=""：多数 xtdata 版本中表示"全部历史"。
    - 如果返回数据不完整，可尝试改为 "20000101" ~ "20991231"。
    """
    # 下载全部历史数据
    xtdata.download_history_data(stock_code, period="1d", start_time="", end_time="")
    factors = xtdata.get_divid_factors(stock_code, "", "")
    if isinstance(factors, dict):
        factors = pd.DataFrame(factors)
    return factors


def normalize_time(s):
    """把时间列统一转换为 datetime。"""
    if pd.api.types.is_datetime64_any_dtype(s):
        return pd.to_datetime(s)

    try:
        # 尝试转成数值时间戳
        s_num = pd.to_numeric(s)
        sample = s_num.dropna().iloc[0]
        unit = "ms" if sample > 1e12 else "s"
        return pd.to_datetime(s_num, unit=unit)
    except (ValueError, TypeError):
        # 否则按字符串/日期解析
        return pd.to_datetime(s)


def calculate_adjusted_price(df_raw, factors):
    """
    用完整历史复权因子计算复权收盘价。
    dr 是除权日当天的后复权调整系数，累积后得到累积后复权因子。

    返回：
    - close_front: 前复权价格 = 原始价格 / 累积后复权因子
    - close_back: 后复权价格 = 原始价格 * 累积后复权因子
    """
    factors = factors.copy()
    factors["time"] = normalize_time(factors["time"]).dt.normalize()

    df = df_raw.copy()
    df["time"] = normalize_time(df["time"]).dt.normalize()

    # 将 dr 列重命名为统一名称
    factor_col = next(
        (c for c in ["dr", "factor", "factors"] if c in factors.columns),
        None,
    )
    if factor_col is None:
        print(f"警告：未找到复权因子列，可用列名：{list(factors.columns)}")
        return df_raw

    factors = factors.rename(columns={factor_col: "dr"})[["time", "dr"]]
    factors = factors.sort_values("time").reset_index(drop=True)

    # 关键：累积上市以来所有除权日的 dr
    factors["cum_factor"] = factors["dr"].cumprod()

    # 关键：merge_asof 让每个交易日匹配之前最近的除权日因子
    df = df.sort_values("time").reset_index(drop=True)
    df = pd.merge_asof(df, factors[["time", "cum_factor"]], on="time")
    df["cum_factor"] = df["cum_factor"].fillna(1.0)

    # dr 是后复权因子
    df["close_front"] = df["close"] / df["cum_factor"]   # 前复权
    df["close_back"] = df["close"] * df["cum_factor"]    # 后复权
    return df


def calculate_return(df, price_col="close"):
    """计算持有期收益率。"""
    start, end = df[price_col].iloc[0], df[price_col].iloc[-1]
    return (end - start) / start


def main():
    # 1. 获取上市以来所有除权除息数据
    factors = get_dividend_factors(STOCK_CODE)
    print("除权除息数据（全部历史）：")
    print(factors)
    print()

    # 2. 不复权 / 前复权 / 后复权行情
    df_none = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="none")
    df_front = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="front")
    df_back = get_price_data(STOCK_CODE, START_DATE, END_DATE, dividend_type="back")

    print("不复权收盘价：")
    print(df_none[["time", "close"]].tail(5))
    print("\n前复权收盘价：")
    print(df_front[["time", "close"]].tail(5))
    print("\n后复权收盘价：")
    print(df_back[["time", "close"]].tail(5))
    print()

    # 3. 收益率对比
    print("持有期收益率：")
    print(f"  不复权：{calculate_return(df_none):.4%}")
    print(f"  前复权：{calculate_return(df_front):.4%}")
    print(f"  后复权：{calculate_return(df_back):.4%}")
    print()

    # 4. 手动用 get_divid_factors 计算前复权/后复权，并与 API 结果对比
    df_manual = calculate_adjusted_price(df_none, factors)
    if "close_front" in df_manual.columns and "close_back" in df_manual.columns:
        # 展示除权日因子和累积因子
        factors_show = factors.copy()
        factors_show["time"] = normalize_time(factors_show["time"]).dt.normalize()
        factors_show["cum_factor"] = factors_show["dr"].cumprod()
        print("除权日因子与累积后复权因子：")
        print(factors_show)
        print()

        # 诊断：对比 API 后复权因子和手动累积因子
        df_back = df_back.copy()
        df_back["time"] = normalize_time(df_back["time"]).dt.normalize()
        df_back["api_back_factor"] = df_back["close"] / df_none["close"]
        print("API 后复权因子 vs 手动累积因子（诊断）：")
        print(df_back[["time", "api_back_factor"]].tail(5))
        print(f"手动累积因子（最新）: {factors_show['cum_factor'].iloc[-1]:.6f}")
        print()

        # 对比手动前复权 vs API 前复权
        df_front = df_front.copy()
        df_front["time"] = normalize_time(df_front["time"]).dt.normalize()
        df_compare_front = df_front[["time", "close"]].rename(columns={"close": "close_front_api"})
        df_compare_front = df_manual[["time", "close", "close_front"]].merge(df_compare_front, on="time", how="left")
        df_compare_front["diff"] = df_compare_front["close_front"] - df_compare_front["close_front_api"]
        print("手动前复权 vs API 前复权对比：")
        print(df_compare_front.tail(10))
        print(f"最大差异：{df_compare_front['diff'].abs().max():.6f}")
        print()

        # 对比手动后复权 vs API 后复权
        df_compare_back = df_back[["time", "close"]].rename(columns={"close": "close_back_api"})
        df_compare_back = df_manual[["time", "close", "close_back"]].merge(df_compare_back, on="time", how="left")
        df_compare_back["diff"] = df_compare_back["close_back"] - df_compare_back["close_back_api"]
        print("手动后复权 vs API 后复权对比：")
        print(df_compare_back.tail(10))
        print(f"最大差异：{df_compare_back['diff'].abs().max():.6f}")
        print()

        # 解释
        latest_cum = factors_show["cum_factor"].iloc[-1]
        print(f"说明：get_divid_factors 当前返回 {len(factors_show)} 条除权记录，")
        print(f"      累积后复权因子 = {latest_cum:.6f}")
        print("      如果和 API 结果差异很大，可能是 get_divid_factors 没有返回完整历史，")
        print("      或 QMT 的复权算法和 dr 的累积方式不同。")
    else:
        print("无法手动计算复权价格，跳过对比。")


if __name__ == "__main__":
    main()
