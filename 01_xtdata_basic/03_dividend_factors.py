# -*- coding: utf-8 -*-
"""
xtdata 复权因子手动计算示例

实现 4 种复权方式：
- 等比前复权 (front_ratio)
- 等比后复权 (back_ratio)
- 前复权 (front)
- 后复权 (back)

运行前提：QMT 终端已启动并登录。
"""

import numpy as np
import pandas as pd
from xtquant import xtdata


# ==================== 复权计算核心函数 ====================

def gen_cumulative_factor(quote_datas, divid_datas):
    """
    生成累积复权因子序列。

    参数：
        quote_datas: DataFrame，行情数据（index 为时间）
        divid_datas: DataFrame，除权除息数据（index 为除权日）

    返回：
        DataFrame，与 quote_datas 同形状，每个交易日对应累积复权因子
    """
    if divid_datas.empty:
        return pd.DataFrame(1.0, index=quote_datas.index, columns=quote_datas.columns)

    factor_list = []
    factor = 1.0
    quote_idx = 0
    divid_idx = 0
    quote_len = len(quote_datas)
    divid_len = len(divid_datas)

    # 按时间对齐，生成每个交易日的累积因子
    while quote_idx < quote_len and divid_idx < divid_len:
        qd = quote_datas.index[quote_idx]
        dd = divid_datas.index[divid_idx]

        if qd >= dd:
            factor *= divid_datas.iloc[divid_idx]["dr"]
            divid_idx += 1
        if qd <= dd:
            factor_list.append(factor)
            quote_idx += 1

    # 处理剩余交易日
    while quote_idx < quote_len:
        factor_list.append(factor)
        quote_idx += 1

    return pd.DataFrame(factor_list, index=quote_datas.index, columns=quote_datas.columns)


def process_forward_ratio(quote_datas, divid_datas):
    """
    等比前复权：以最新价为基准，乘除法调整。

    公式：close_front_ratio = close * (cum_factor / latest_cum_factor)
    """
    cum_factor = gen_cumulative_factor(quote_datas, divid_datas)
    if cum_factor.empty or cum_factor.iloc[-1].isna().all():
        return quote_datas

    latest_factor = cum_factor.iloc[-1]
    result = quote_datas * (cum_factor / latest_factor)
    return result.round(2)


def process_backward_ratio(quote_datas, divid_datas):
    """
    等比后复权：以历史价为基准，乘除法调整。

    公式：close_back_ratio = close * cum_factor
    """
    cum_factor = gen_cumulative_factor(quote_datas, divid_datas)
    result = quote_datas * cum_factor
    return result.round(2)


def calc_forward_price(v, d):
    """前复权单日价格调整公式。"""
    return ((v - d["interest"] + d["allotPrice"] * d["allotNum"])
            / (1 + d["allotNum"] + d["stockBonus"] + d["stockGift"]))


def calc_backward_price(v, d):
    """后复权单日价格调整公式。"""
    return (v * (1.0 + d["stockGift"] + d["stockBonus"] + d["allotNum"])
            + d["interest"] - d["allotNum"] * d["allotPrice"])


def process_forward(quote_datas, divid_datas):
    """
    前复权（加减法）：以最新价为基准，逐日调整历史价格。

    公式：close_front = (close - interest + allotPrice * allotNum)
                        / (1 + allotNum + stockBonus + stockGift)
    """
    if divid_datas.empty:
        return quote_datas.copy()

    result = quote_datas.copy()
    for qi in range(len(result)):
        q_time = result.index[qi]
        for di in range(len(divid_datas)):
            d = divid_datas.iloc[di]
            d_time = divid_datas.index[di]
            if d_time <= q_time:
                continue
            result.iloc[qi] = result.iloc[qi].apply(lambda v: calc_forward_price(v, d))
    return result.round(2)


def process_backward(quote_datas, divid_datas):
    """
    后复权（加减法）：以历史价为基准，逐日调整未来价格。

    公式：close_back = close * (1 + stockGift + stockBonus + allotNum)
                        + interest - allotNum * allotPrice
    """
    if divid_datas.empty:
        return quote_datas.copy()

    result = quote_datas.copy()
    for qi in range(len(result)):
        q_time = result.index[qi]
        for di in range(len(divid_datas) - 1, -1, -1):
            d = divid_datas.iloc[di]
            d_time = divid_datas.index[di]
            if d_time > q_time:
                continue
            result.iloc[qi] = result.iloc[qi].apply(lambda v: calc_backward_price(v, d))
    return result.round(2)


# ==================== 示例 ====================

def get_price_data(stock_code, start_time, end_time, dividend_type="none"):
    """获取 QMT API 返回的复权行情数据。"""
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
    return df


def compare_with_api(df_manual, df_api, name):
    """对比手工计算结果和 API 结果。"""
    # 处理 df_api 的时间：毫秒时间戳 -> 北京时间 -> 日期
    df_api = df_api.copy()
    if pd.api.types.is_numeric_dtype(df_api["time"]):
        # 毫秒时间戳：先转 UTC，再转北京时间，最后去掉时区
        df_api["time"] = pd.to_datetime(df_api["time"], unit="ms", utc=True) \
            .dt.tz_convert("Asia/Shanghai") \
            .dt.tz_localize(None)
    else:
        df_api["time"] = pd.to_datetime(df_api["time"])
    df_api["time"] = df_api["time"].dt.normalize()

    # 处理 df_manual：统一转成 Series，index 为时间
    df_manual = df_manual.copy()
    if isinstance(df_manual, pd.DataFrame):
        if df_manual.shape[1] == 1:
            # index 是时间，columns 是股票代码
            df_manual = df_manual.iloc[:, 0]
        else:
            # index 是股票代码，columns 是时间
            df_manual = df_manual.iloc[0]
    df_manual.name = "close"

    # 把 df_manual 的 index 转成 datetime（兼容毫秒时间戳和 YYYYMMDD）
    if pd.api.types.is_numeric_dtype(df_manual.index):
        sample = df_manual.index[0]
        if sample > 1e12:
            # 毫秒时间戳：转 UTC -> 北京时间 -> 去掉时区
            df_manual.index = pd.to_datetime(df_manual.index, unit="ms", utc=True) \
                .tz_convert("Asia/Shanghai") \
                .tz_localize(None)
        else:
            # YYYYMMDD 整数
            df_manual.index = pd.to_datetime(df_manual.index, format="%Y%m%d")
    else:
        df_manual.index = pd.to_datetime(df_manual.index)
    df_manual.index = df_manual.index.normalize()

    # 转成 DataFrame
    df_manual = df_manual.reset_index()
    df_manual.columns = ["time", "close"]

    # 对齐时间范围
    common_start = max(df_manual["time"].min(), df_api["time"].min())
    common_end = min(df_manual["time"].max(), df_api["time"].max())
    df_manual = df_manual[(df_manual["time"] >= common_start) & (df_manual["time"] <= common_end)]
    df_api = df_api[(df_api["time"] >= common_start) & (df_api["time"] <= common_end)]

    # merge 对比
    compare = df_manual.merge(df_api[["time", "close"]].rename(columns={"close": "api"}), on="time", how="left")
    compare["diff"] = compare["close"] - compare["api"]

    # 过滤 NaN 后计算最大差异
    valid_diff = compare["diff"].dropna()
    max_diff = valid_diff.abs().max() if not valid_diff.empty else float("nan")

    print(f"{name} 对比（最后 5 行，共同时间范围：{common_start.date()} ~ {common_end.date()}）：")
    print(compare.tail(5))
    print(f"有效数据最大差异：{max_diff:.6f}")
    print()


def main():
    stock_code = "002594.SZ"   # 比亚迪（示例）
    start_time = "20260601"
    end_time = "20260717"

    # 1. 获取除权除息数据
    divid_datas = xtdata.get_divid_factors(stock_code)
    print("除权除息数据：")
    print(divid_datas)
    print()

    # 2. 获取不复权行情（只取价格字段）
    field_list = ["open", "high", "low", "close"]
    datas_ori = xtdata.get_market_data(
        field_list, [stock_code], "1d", dividend_type="none"
    )["close"].T

    print("不复权行情（close）：")
    print(datas_ori.tail())
    print()

    # 3. 手工计算 4 种复权方式
    datas_forward_ratio = process_forward_ratio(datas_ori, divid_datas)
    datas_backward_ratio = process_backward_ratio(datas_ori, divid_datas)
    datas_forward = process_forward(datas_ori, divid_datas)
    datas_backward = process_backward(datas_ori, divid_datas)

    # 打印手工计算结果最新 5 天数据
    print("手工等比前复权（front_ratio）最新 5 天：")
    print(datas_forward_ratio.tail())
    print()
    print("手工等比后复权（back_ratio）最新 5 天：")
    print(datas_backward_ratio.tail())
    print()
    print("手工前复权（front）最新 5 天：")
    print(datas_forward.tail())
    print()
    print("手工后复权（back）最新 5 天：")
    print(datas_backward.tail())
    print()

    api_front = get_price_data(stock_code, start_time, end_time, dividend_type="front")
    api_back = get_price_data(stock_code, start_time, end_time, dividend_type="back")
    api_front_ratio = get_price_data(stock_code, start_time, end_time, dividend_type="front_ratio")
    api_back_ratio = get_price_data(stock_code, start_time, end_time, dividend_type="back_ratio")

    # 打印 API 复权行情最新 5 天数据
    print("API 前复权（front）最新 5 天：")
    print(api_front[["time", "close"]].tail(5))
    print()
    print("API 后复权（back）最新 5 天：")
    print(api_back[["time", "close"]].tail(5))
    print()
    print("API 等比前复权（front_ratio）最新 5 天：")
    print(api_front_ratio[["time", "close"]].tail(5))
    print()
    print("API 等比后复权（back_ratio）最新 5 天：")
    print(api_back_ratio[["time", "close"]].tail(5))
    print()

    # 5. 对比手工计算和 API 结果
    compare_with_api(datas_forward_ratio, api_front_ratio, "等比前复权 (front_ratio)")
    compare_with_api(datas_backward_ratio, api_back_ratio, "等比后复权 (back_ratio)")
    compare_with_api(datas_forward, api_front, "前复权 (front)")
    compare_with_api(datas_backward, api_back, "后复权 (back)")


if __name__ == "__main__":
    main()
