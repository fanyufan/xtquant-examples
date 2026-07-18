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

import os
import json
from xtquant import xtdata


def get_output_dir():
    """获取当前文件所在目录下的 outputs 目录。"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


# ==================== 基础配置 ====================
SAMPLES = {
    "A股股票": "000001.SZ",      # 平安银行
    "可转债": "128136.SZ",        # 可转债示例（请替换为实际品种）
    "ETF": "510050.SH",           # 上证50ETF
    "期货": "RB2501.SH",          # 螺纹钢期货示例（需开通期货权限）
    "期权": "10000001.SH",        # 期权示例（需开通期权权限）
}


# ==================== 合约信息字段中英文对照表 ====================
# 来源：xtdata.get_instrument_detail 返回字典的字段名及中文说明
INSTRUMENT_FIELDS = {
    "ExchangeID":               "合约市场代码",
    "InstrumentID":             "合约代码",
    "InstrumentName":           "合约名称",
    "Abbreviation":             "合约名称的拼音简写",
    "ProductID":                "合约的品种ID（期货）",
    "ProductName":              "合约的品种名称（期货）",
    "UnderlyingCode":           "标的合约",
    "ExtendName":               "扩位名称",
    "ExchangeCode":             "交易所代码",
    "RzrkCode":                 "rzrk代码",
    "UniCode":                  "统一规则代码",
    "CreateDate":               "上市日期（期货）",
    "OpenDate":                 "IPO日期（股票）",
    "ExpireDate":               "退市日或者到期日",
    "PreClose":                 "前收盘价格",
    "SettlementPrice":          "前结算价格",
    "UpStopPrice":              "当日涨停价",
    "DownStopPrice":            "当日跌停价",
    "FloatVolume":              "流通股本",
    "TotalVolume":              "总股本",
    "AccumulatedInterest":      "自上市付息日起的累积未付利息额（债券）",
    "LongMarginRatio":          "多头保证金率",
    "ShortMarginRatio":         "空头保证金率",
    "PriceTick":                "最小变价单位",
    "VolumeMultiple":           "合约乘数（对期货以外的品种，默认是1）",
    "MainContract":             "主力合约标记，1/2/3分别表示第一/二/三主力合约",
    "MaxMarketOrderVolume":     "市价单最大下单量",
    "MinMarketOrderVolume":     "市价单最小下单量",
    "MaxLimitOrderVolume":      "限价单最大下单量",
    "MinLimitOrderVolume":      "限价单最小下单量",
    "MaxMarginSideAlgorithm":   "上期所大单边的处理算法",
    "DayCountFromIPO":          "自IPO起经历的交易日总数",
    "LastVolume":               "昨日持仓量",
    "InstrumentStatus":         "合约停牌状态",
    "IsTrading":                "合约是否可交易",
    "IsRecent":                 "是否是近月合约",
    "IsContinuous":             "是否是连续合约",
    "bNotProfitable":           "是否非盈利状态",
    "bDualClass":               "是否同股不同权",
    "ContinueType":             "连续合约类型",
    "secuCategory":             "证券分类",
    "secuAttri":                "证券属性",
    "MaxMarketSellOrderVolume": "市价卖单最大单笔下单量",
    "MinMarketSellOrderVolume": "市价卖单最小单笔下单量",
    "MaxLimitSellOrderVolume":  "限价卖单最大单笔下单量",
    "MinLimitSellOrderVolume":  "限价卖单最小单笔下单量",
    "MaxFixedBuyOrderVol":      "盘后定价委托数量的上限（买）",
    "MinFixedBuyOrderVol":      "盘后定价委托数量的下限（买）",
    "MaxFixedSellOrderVol":     "盘后定价委托数量的上限（卖）",
    "MinFixedSellOrderVol":     "盘后定价委托数量的下限（卖）",
    "HSGTFlag":                 "沪/深港通标的标识，0-非标的，1/3-标的，2/4-历史标的，5-沪港通也是深港通",
    "BondParValue":             "债券面值",
    "QualifiedType":            "投资者适当性管理分类",
    "PriceTickType":            "价差类别（港股用），1-股票，3-债券，4-期权，5-交易所买卖基金",
    "tradingStatus":            "交易状态",
    "OptUnit":                  "期权合约单位",
    "MarginUnit":               "期权单位保证金",
    "OptUndlCode":              "期权标的证券代码或可转债正股标的证券代码",
    "OptUndlMarket":            "期权标的证券市场或可转债正股标的证券市场",
    "OptLotSize":               "期权整手数",
    "OptExercisePrice":         "期权行权价或可转债转股价",
    "NeeqExeType":              "全国股转转让类型，1-协议，2-做市，3-集合竞价+连续竞价，4-集合竞价",
    "OptExchFixedMargin":       "交易所期权合约保证金不变部分",
    "OptExchMiniMargin":        "交易所期权合约最小保证金",
    "Ccy":                      "币种",
    "IbSecType":                "IB安全类型，期货或股票",
    "OptUndlRiskFreeRate":      "期权标的无风险利率",
    "OptUndlHistoryRate":       "期权标的历史波动率",
    "EndDelivDate":             "期权行权终止日",
    "RegisteredCapital":        "注册资本（单位:百万）",
    "MaxOrderPriceRange":       "最大有效申报范围",
    "MinOrderPriceRange":       "最小有效申报范围",
    "VoteRightRatio":           "同股同权比例",
    "m_nMinRepurchaseDaysLimit": "最小回购天数",
    "m_nMaxRepurchaseDaysLimit": "最大回购天数",
    "DeliveryYear":             "交割年份",
    "DeliveryMonth":            "交割月",
    "ContractType":             "标识期权，1-过期，2-当月，3-下月，4-下季，5-隔季，6-隔下季",
    "ProductTradeQuota":        "期货品种交易配额",
    "ContractTradeQuota":       "期货合约交易配额",
    "ProductOpenInterestQuota": "期货品种持仓配额",
    "ContractOpenInterestQuota": "期货合约持仓配额",
    "ChargeType":               "期货和期权手续费方式，0-未知，1-按元/手，2-按费率",
    "ChargeOpen":               "开仓手续费率，-1表示没有",
    "ChargeClose":              "平仓手续费率，-1表示没有",
    "ChargeTodayOpen":          "开今仓（日内开仓）手续费率，-1表示没有",
    "ChargeTodayClose":         "平今仓（日内平仓）手续费率，-1表示没有",
    "OptionType":               "期权类型，-1为非期权，0为期权认购，1为期权认沽",
    "OpenInterestMultiple":     "交割月持仓倍数",
}


def get_field_label(field_name):
    """获取字段对应的中文名称，未在映射表中的字段返回空字符串。"""
    return INSTRUMENT_FIELDS.get(field_name, "")


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
        print(f"主要字段（共 {len(detail)} 个）：")
        # 按映射表顺序输出已知字段，未知字段追加在末尾
        known_keys = [k for k in INSTRUMENT_FIELDS.keys() if k in detail]
        unknown_keys = [k for k in detail.keys() if k not in INSTRUMENT_FIELDS]
        for key in known_keys + unknown_keys:
            value = detail[key]
            label = get_field_label(key)
            if label:
                print(f"  {key}（{label}）: {value}")
            else:
                print(f"  {key}: {value}")
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


def save_details_to_json(results, filename=None):
    """把批量查询结果保存到 JSON 文件，方便查看。"""
    if filename is None:
        filename = os.path.join(get_output_dir(), "instrument_details.json")
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
