# -*- coding: utf-8 -*-
"""
xtdata 品种类型查询示例

覆盖接口：
- get_instrument_type：查询单个品种的类型

覆盖品种：
- A 股股票
- 可转债
- ETF
- 期货/期权（如果 QMT 开通了对应权限）

运行前提：QMT 终端已启动并登录。
"""

from xtquant import xtdata


# ==================== 基础配置 ====================
SAMPLES = {
    "A股股票": "000001.SZ",      # 平安银行
    "可转债": "128136.SZ",        # 可转债示例（请替换为实际品种）
    "ETF": "510050.SH",           # 上证50ETF
    "期货": "RB2501.SH",          # 螺纹钢期货示例（需开通期货权限）
    "期权": "10000001.SH",        # 期权示例（需开通期权权限）
}


def query_instrument_type(stock_code):
    """
    查询单个品种的类型。

    返回类型说明（常见）：
    - 'STOCK' / 0：A 股股票
    - 'FUND' / 1：基金（包括 ETF）
    - 'BOND' / 2：债券（包括可转债）
    - 'INDEX' / 3：指数
    - 'FUTURES' / 4：期货
    - 'OPTION' / 5：期权

    具体返回值因 xtquant 版本而异，运行后请查看实际输出。
    """
    print(f"\n查询品种：{stock_code}")

    if not hasattr(xtdata, "get_instrument_type"):
        print("当前 xtdata 版本没有 get_instrument_type 接口")
        return None

    try:
        inst_type = xtdata.get_instrument_type(stock_code)
    except Exception as e:
        print(f"查询失败：{e}")
        return None

    print(f"返回类型：{type(inst_type).__name__}")
    print(f"返回结果：{inst_type}")
    return inst_type


def main():
    print("=" * 60)
    print("xtdata 品种类型查询示例")
    print("=" * 60)

    # 单个查询示例
    for name, code in SAMPLES.items():
        print("\n" + "-" * 60)
        print(f"预期类型：{name}")
        print("-" * 60)
        query_instrument_type(code)

    print("\n提示：")
    print("  1. 期货/期权示例需要开通对应权限才能查询到数据。")
    print("  2. 不同 QMT 版本返回的类型值可能不同（字符串或整数）。")
    print("  3. 请以实际输出为准，本示例中的类型说明仅供参考。")


if __name__ == "__main__":
    main()
