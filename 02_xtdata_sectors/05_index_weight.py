# -*- coding: utf-8 -*-
"""
xtdata 指数成分股权重示例

覆盖内容：
- 获取指数成分股列表（get_index_stock_list）
- 获取指数成分股权重（get_index_weight）
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
    获取指数成分股列表。

    参数：
        index_code: 指数代码，如 "000300.SH"

    返回值：
        list: 成分股代码列表
    """
    stocks = xtdata.get_index_stock_list(index_code)
    print(f"指数 '{index_code}' 共有 {len(stocks)} 只成分股")
    print(f"前 10 只：{stocks[:10]}")
    print()
    return stocks


def get_index_weights(index_code):
    """
    获取指数成分股权重。

    参数：
        index_code: 指数代码，如 "000300.SH"

    返回值：
        dict: {股票代码: 权重}
    """
    # 注意：不同 QMT 版本接口可能略有差异，如果 get_index_weight 不存在，
    # 可以尝试 get_index_weight 或 get_index_weights（带 s）
    try:
        weights = xtdata.get_index_weight(index_code)
    except AttributeError:
        print("当前 QMT 版本没有 get_index_weight，尝试 get_index_weights...")
        weights = xtdata.get_index_weights(index_code)

    if weights is None:
        print(f"未能获取到 '{index_code}' 的权重数据，请检查指数代码是否正确。")
        return {}

    print(f"指数 '{index_code}' 权重数据：")
    print(f"  共获取到 {len(weights)} 条权重记录")
    print(f"  前 10 条：{dict(list(weights.items())[:10])}")
    print()
    return weights


def analyze_weights(weights):
    """
    对权重数据进行简单统计分析。

    参数：
        weights: dict, {股票代码: 权重}
    """
    if not weights:
        return

    df = pd.DataFrame(list(weights.items()), columns=["stock_code", "weight"])
    df = df.sort_values("weight", ascending=False).reset_index(drop=True)

    print("=" * 60)
    print("权重统计")
    print("=" * 60)
    print(f"成分股数量：{len(df)}")
    print(f"权重总和：{df['weight'].sum():.4f}")
    print(f"最大权重：{df['weight'].max():.4f}")
    print(f"最小权重：{df['weight'].min():.4f}")
    print(f"平均权重：{df['weight'].mean():.4f}")
    print()

    print("权重 Top 10：")
    print(df.head(10).to_string(index=False))
    print()

    return df


def save_weights_to_csv(df, index_code):
    """将权重数据保存到 CSV 文件。"""
    filename = os.path.join(get_output_dir(), f"index_weight_{index_code.replace('.', '_')}.csv")
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"[已保存] 权重数据 CSV：{filename}")
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
    print("  1. 不同 QMT 版本对 get_index_weight 的命名可能不同（如 get_index_weights）。")
    print("  2. 部分指数可能不支持权重查询，返回空时请尝试其他指数。")
    print("  3. 权重数据通常为日度更新，实盘前请确认数据日期。")


if __name__ == "__main__":
    main()
