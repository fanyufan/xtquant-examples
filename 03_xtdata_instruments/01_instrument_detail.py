# -*- coding: utf-8 -*-
"""
xtdata 品种详情查询示例

覆盖接口：
- get_instrument_detail：查询单个或多个品种的详细信息

覆盖品种：
- A 股股票
- 可转债
- ETF
- 期货/期权（如果 QMT 开通了对应权限）

运行前提：QMT 终端已启动并登录。
"""

import json
from xtquant import xtdata


# ==================== 基础配置 ====================
SAMPLES = {
    "A股股票": "000001.SZ",      # 平安银行
    "可转债": "128136.SZ",        # 可转债示例（请替换为实际品种）
    "ETF": "510050.SH",           # 上证50ETF
    "期货": "RB2501.SH",          # 螺纹钢期货示例（需开通期货权限）
    "期权": "10000001.SH",        # 期权示例（需开通期权权限）
}


def query_instrument_detail(stock_code):
    """
    查询单个品种的详细信息。

    返回内容通常包括：
    - 代码、名称、市场、类型
    - 上市日期、退市日期
    - 涨跌停限制、最小变动单位
    - 其他品种特有字段
    """
    print(f"\n查询品种：{stock_code}")

    if not hasattr(xtdata, "get_instrument_detail"):
        print("当前 xtdata 版本没有 get_instrument_detail 接口")
        return None

    try:
        detail = xtdata.get_instrument_detail(stock_code)
    except Exception as e:
        print(f"查询失败：{e}")
        return None

    if detail is None or (isinstance(detail, dict) and not detail):
        print("未获取到详情数据，可能是该品种无权限或未上市")
        return None

    # 打印返回类型和结构
    print(f"返回类型：{type(detail).__name__}")

    if isinstance(detail, dict):
        print("主要字段：")
        for key, value in list(detail.items())[:20]:
            print(f"  {key}: {value}")
        if len(detail) > 20:
            print(f"  ... 共 {len(detail)} 个字段")
    elif isinstance(detail, (list, tuple)):
        print(f"返回列表，长度：{len(detail)}")
        print(detail[:5])
    else:
        print(detail)

    return detail


def query_batch_details(stock_codes):
    """批量查询多个品种的详情。"""
    print("\n" + "=" * 60)
    print("批量查询品种详情")
    print("=" * 60)
    results = {}
    for code in stock_codes:
        detail = query_instrument_detail(code)
        results[code] = detail
    return results


def save_details_to_json(results, filename="instrument_details.json"):
    """把批量查询结果保存到 JSON 文件，方便查看。"""
    # 过滤掉 None 值，并把不能序列化的对象转成字符串
    clean_results = {}
    for code, detail in results.items():
        if detail is None:
            continue
        if isinstance(detail, dict):
            clean_results[code] = {
                k: str(v) if not isinstance(v, (int, float, str, bool, type(None))) else v
                for k, v in detail.items()
            }
        else:
            clean_results[code] = str(detail)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(clean_results, f, ensure_ascii=False, indent=2)
    print(f"\n详情已保存到：{filename}")


def main():
    print("=" * 60)
    print("xtdata 品种详情查询示例")
    print("=" * 60)

    # 1. 单个查询示例
    for name, code in SAMPLES.items():
        print("\n" + "-" * 60)
        print(f"类型：{name}")
        print("-" * 60)
        query_instrument_detail(code)

    # 2. 批量查询
    all_codes = list(SAMPLES.values())
    results = query_batch_details(all_codes)

    # 3. 保存到 JSON
    save_details_to_json(results)

    print("\n提示：")
    print("  1. 期货/期权示例需要开通对应权限才能查询到数据。")
    print("  2. 不同 QMT 版本返回的字段可能不同，请以实际返回为准。")
    print("  3. 可转债代码请替换为你当前能交易的真实品种。")


if __name__ == "__main__":
    main()
