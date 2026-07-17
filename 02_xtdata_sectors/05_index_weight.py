# -*- coding: utf-8 -*-
"""
xtdata 指数成分股权重分析示例

覆盖内容：
- 获取指数成分股列表（get_index_stock_list）
- 获取指数成分股权重（get_index_weight）
- 对权重进行多角度分析：
  - 基础统计（数量、总和、最大/最小/平均）
  - 头部集中度（Top 5/10/20/50 权重占比）
  - 权重分布（按区间分组）
  - 与等权对比（最大个股权重是等权的多少倍）
- 将权重数据保存到本地 CSV，方便查看

常用指数代码：
- 沪深300：000300.SH
- 中证500：000905.SH
- 上证50：000016.SH
- 创业板指：399006.SZ
- 科创50：000688.SH

运行前提：QMT/迅投终端已启动并登录。
"""

import os
import pandas as pd
from xtquant import xtdata


def get_output_dir():
    """获取当前文件所在目录下的 outputs 目录。"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_index_components(index_code):
    """
    兼容获取指数成分股列表。

    尝试顺序：
    1. xtdata.get_index_stock_list(index_code)
    2. xtdata.get_stock_list_in_sector(index_code)

    参数：
        index_code: 指数代码，如 "000300.SH"

    返回值：
        list: 成分股代码列表
    """
    # 1. 尝试专用接口（部分 QMT 版本提供）
    if hasattr(xtdata, "get_index_stock_list"):
        try:
            stocks = xtdata.get_index_stock_list(index_code)
            if stocks:
                print(f"使用接口 get_index_stock_list，指数 '{index_code}' 共有 {len(stocks)} 只成分股")
                print(f"前 10 只：{stocks[:10]}")
                print()
                return stocks
        except Exception as e:
            print(f"  get_index_stock_list({index_code}) 失败：{e}")

    # 2. 尝试把指数代码当作板块名
    try:
        stocks = xtdata.get_stock_list_in_sector(index_code)
        if stocks:
            print(f"使用接口 get_stock_list_in_sector，指数 '{index_code}' 共有 {len(stocks)} 只成分股")
            print(f"前 10 只：{stocks[:10]}")
            print()
            return stocks
    except Exception as e:
        print(f"  get_stock_list_in_sector({index_code}) 失败：{e}")

    print(f"未能获取到 '{index_code}' 的成分股列表。")
    return []


def get_index_weights(index_code):
    """
    获取指数成分股权重。

    参数：
        index_code: 指数代码，如 "000300.SH"

    返回值：
        dict: {股票代码: 权重}
    """
    try:
        weights = xtdata.get_index_weight(index_code)
    except Exception as e:
        print(f"  get_index_weight({index_code}) 失败：{e}")
        return {}

    if not weights:
        print(f"未能获取到 '{index_code}' 的权重数据，请检查指数代码是否正确。")
        return {}

    print(f"指数 '{index_code}' 共获取到 {len(weights)} 条权重记录")
    print(f"  前 10 条：{dict(list(weights.items())[:10])}")
    print()
    return weights


def analyze_weights(weights):
    """
    对权重数据进行多角度统计分析。

    参数：
        weights: dict, {股票代码: 权重}

    返回值：
        pd.DataFrame: 按权重降序排列的成分股权重表
    """
    if not weights:
        return None

    df = pd.DataFrame(list(weights.items()), columns=["stock_code", "weight"])
    df = df.sort_values("weight", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    df["cumulative_weight"] = df["weight"].cumsum()

    n = len(df)
    equal_weight = 1.0 / n if n > 0 else 0.0

    print("=" * 60)
    print("一、基础权重统计")
    print("=" * 60)
    print(f"成分股数量：{n}")
    print(f"权重总和：{df['weight'].sum():.4f}")
    print(f"最大权重：{df['weight'].max():.4f}  ({df.loc[0, 'stock_code']})")
    print(f"最小权重：{df['weight'].min():.4f}  ({df.loc[n - 1, 'stock_code']})")
    print(f"平均权重：{df['weight'].mean():.4f}")
    print(f"中位数权重：{df['weight'].median():.4f}")
    print(f"等权基准（1/{n}）：{equal_weight:.4f}")
    print(f"最大权重 / 等权基准：{df['weight'].max() / equal_weight:.2f} 倍")
    print()

    print("=" * 60)
    print("二、头部集中度分析")
    print("=" * 60)
    for top_n in [5, 10, 20, 50]:
        if n >= top_n:
            ratio = df["weight"].head(top_n).sum()
            print(f"Top {top_n:2d} 权重占比：{ratio:.2%}")
    print()

    print("=" * 60)
    print("三、权重分布（按区间分组）")
    print("=" * 60)
    bins = [0, 0.001, 0.005, 0.01, 0.02, 0.05, 1.0]
    labels = ["<0.1%", "0.1%~0.5%", "0.5%~1%", "1%~2%", "2%~5%", ">=5%"]
    df["weight_group"] = pd.cut(df["weight"], bins=bins, labels=labels, include_lowest=True)
    group_counts = df["weight_group"].value_counts().sort_index()
    group_sum = df.groupby("weight_group", observed=True)["weight"].sum().sort_index()
    distribution = pd.DataFrame({
        "股票数量": group_counts,
        "权重合计": group_sum,
    })
    print(distribution.to_string())
    print()

    print("=" * 60)
    print("四、权重 Top 20")
    print("=" * 60)
    top20 = df[["rank", "stock_code", "weight", "cumulative_weight"]].head(20).copy()
    top20["weight"] = top20["weight"].apply(lambda x: f"{x:.4f}")
    top20["cumulative_weight"] = top20["cumulative_weight"].apply(lambda x: f"{x:.4f}")
    print(top20.to_string(index=False))
    print()

    return df


def save_weights_to_csv(df, index_code):
    """将权重分析结果保存到 CSV 文件。"""
    if df is None:
        return
    filename = os.path.join(get_output_dir(), f"index_weight_{index_code.replace('.', '_')}.csv")
    # 选择主要字段保存
    save_df = df[["rank", "stock_code", "weight", "cumulative_weight"]].copy()
    save_df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"[已保存] 权重分析结果 CSV：{filename}")
    print()


def main():
    # 示例指数：沪深300
    index_code = "000300.SH"

    print("=" * 60)
    print(f"示例：获取指数 '{index_code}' 的成分股与权重")
    print("=" * 60)
    print()

    # 1. 获取成分股
    stocks = get_index_components(index_code)

    # 2. 获取权重
    weights = get_index_weights(index_code)

    # 3. 分析权重
    df = analyze_weights(weights)

    # 4. 保存到 CSV
    if df is not None:
        save_weights_to_csv(df, index_code)

    print("提示：")
    print("  1. 部分指数可能不支持权重查询，返回空时请尝试其他指数。")
    print("  2. 权重数据通常为日度更新，实盘前请确认数据日期。")
    print("  3. analyze_weights 中演示了集中度、分布、等权对比等常见分析方法。")


if __name__ == "__main__":
    main()
