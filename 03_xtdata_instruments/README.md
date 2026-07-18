# xtdata 品种信息查询示例

本目录展示 `xtquant.xtdata` 中品种详情和类型相关的接口。

## 文件说明

| 文件 | 内容 |
|------|------|
| `01_instrument_detail.py` | `get_instrument_detail` 品种详情查询 |
| `02_instrument_type.py` | `get_instrument_type` 品种类型查询 |

## 运行前准备

1. QMT/迅投终端已启动并登录。
2. 已安装 `xtquant` 包。
3. 期货/期权示例需要开通对应权限才能查询到数据。

## 运行方式

```bash
python 03_xtdata_instruments/01_instrument_detail.py
python 03_xtdata_instruments/02_instrument_type.py
```

## 品种代码规则

| 品种 | 代码示例 | 说明 |
|------|---------|------|
| A 股股票 | `000001.SZ` | 深交所 |
| A 股股票 | `600000.SH` | 上交所 |
| 可转债 | `128136.SZ` | 深交所可转债 |
| ETF | `510050.SH` | 上交所 ETF |
| 期货 | `RB2501.SH` | 上期所螺纹钢（示例）|
| 期权 | `10000001.SH` | 上交所期权（示例）|

> 提示：期货/期权代码规则因交易所而异，实际使用前请确认你账户可交易的品种代码。

## 接口说明

### `get_instrument_detail(stock_code)`

返回单个品种的详细信息，常见字段包括：

- 基础信息：代码、名称、市场、类型
- 交易信息：上市日期、退市日期、涨跌停限制、最小变动单位
- 品种特有字段：因股票/可转债/ETF/期货/期权而异

#### 合约信息字段列表

下表列出 `get_instrument_detail` 返回字典中可能包含的字段及中文说明
（不同 QMT 版本与品种类型实际返回的字段会有差异，请以实际输出为准）：

| 字段名 | 说明 |
|--------|------|
| `ExchangeID` | 合约市场代码 |
| `InstrumentID` | 合约代码 |
| `InstrumentName` | 合约名称 |
| `Abbreviation` | 合约名称的拼音简写 |
| `ProductID` | 合约的品种ID（期货） |
| `ProductName` | 合约的品种名称（期货） |
| `UnderlyingCode` | 标的合约 |
| `ExtendName` | 扩位名称 |
| `ExchangeCode` | 交易所代码 |
| `RzrkCode` | rzrk代码 |
| `UniCode` | 统一规则代码 |
| `CreateDate` | 上市日期（期货） |
| `OpenDate` | IPO日期（股票） |
| `ExpireDate` | 退市日或者到期日 |
| `PreClose` | 前收盘价格 |
| `SettlementPrice` | 前结算价格 |
| `UpStopPrice` | 当日涨停价 |
| `DownStopPrice` | 当日跌停价 |
| `FloatVolume` | 流通股本 |
| `TotalVolume` | 总股本 |
| `AccumulatedInterest` | 自上市付息日起的累积未付利息额（债券） |
| `LongMarginRatio` | 多头保证金率 |
| `ShortMarginRatio` | 空头保证金率 |
| `PriceTick` | 最小变价单位 |
| `VolumeMultiple` | 合约乘数（对期货以外的品种，默认是1） |
| `MainContract` | 主力合约标记，1/2/3分别表示第一/二/三主力合约 |
| `MaxMarketOrderVolume` | 市价单最大下单量 |
| `MinMarketOrderVolume` | 市价单最小下单量 |
| `MaxLimitOrderVolume` | 限价单最大下单量 |
| `MinLimitOrderVolume` | 限价单最小下单量 |
| `MaxMarginSideAlgorithm` | 上期所大单边的处理算法 |
| `DayCountFromIPO` | 自IPO起经历的交易日总数 |
| `LastVolume` | 昨日持仓量 |
| `InstrumentStatus` | 合约停牌状态 |
| `IsTrading` | 合约是否可交易 |
| `IsRecent` | 是否是近月合约 |
| `IsContinuous` | 是否是连续合约 |
| `bNotProfitable` | 是否非盈利状态 |
| `bDualClass` | 是否同股不同权 |
| `ContinueType` | 连续合约类型 |
| `secuCategory` | 证券分类 |
| `secuAttri` | 证券属性 |
| `MaxMarketSellOrderVolume` | 市价卖单最大单笔下单量 |
| `MinMarketSellOrderVolume` | 市价卖单最小单笔下单量 |
| `MaxLimitSellOrderVolume` | 限价卖单最大单笔下单量 |
| `MinLimitSellOrderVolume` | 限价卖单最小单笔下单量 |
| `MaxFixedBuyOrderVol` | 盘后定价委托数量的上限（买） |
| `MinFixedBuyOrderVol` | 盘后定价委托数量的下限（买） |
| `MaxFixedSellOrderVol` | 盘后定价委托数量的上限（卖） |
| `MinFixedSellOrderVol` | 盘后定价委托数量的下限（卖） |
| `HSGTFlag` | 沪/深港通标的标识，0-非标的，1/3-标的，2/4-历史标的，5-沪港通也是深港通 |
| `BondParValue` | 债券面值 |
| `QualifiedType` | 投资者适当性管理分类 |
| `PriceTickType` | 价差类别（港股用），1-股票，3-债券，4-期权，5-交易所买卖基金 |
| `tradingStatus` | 交易状态 |
| `OptUnit` | 期权合约单位 |
| `MarginUnit` | 期权单位保证金 |
| `OptUndlCode` | 期权标的证券代码或可转债正股标的证券代码 |
| `OptUndlMarket` | 期权标的证券市场或可转债正股标的证券市场 |
| `OptLotSize` | 期权整手数 |
| `OptExercisePrice` | 期权行权价或可转债转股价 |
| `NeeqExeType` | 全国股转转让类型，1-协议，2-做市，3-集合竞价+连续竞价，4-集合竞价 |
| `OptExchFixedMargin` | 交易所期权合约保证金不变部分 |
| `OptExchMiniMargin` | 交易所期权合约最小保证金 |
| `Ccy` | 币种 |
| `IbSecType` | IB安全类型，期货或股票 |
| `OptUndlRiskFreeRate` | 期权标的无风险利率 |
| `OptUndlHistoryRate` | 期权标的历史波动率 |
| `EndDelivDate` | 期权行权终止日 |
| `RegisteredCapital` | 注册资本（单位:百万） |
| `MaxOrderPriceRange` | 最大有效申报范围 |
| `MinOrderPriceRange` | 最小有效申报范围 |
| `VoteRightRatio` | 同股同权比例 |
| `m_nMinRepurchaseDaysLimit` | 最小回购天数 |
| `m_nMaxRepurchaseDaysLimit` | 最大回购天数 |
| `DeliveryYear` | 交割年份 |
| `DeliveryMonth` | 交割月 |
| `ContractType` | 标识期权，1-过期，2-当月，3-下月，4-下季，5-隔季，6-隔下季 |
| `ProductTradeQuota` | 期货品种交易配额 |
| `ContractTradeQuota` | 期货合约交易配额 |
| `ProductOpenInterestQuota` | 期货品种持仓配额 |
| `ContractOpenInterestQuota` | 期货合约持仓配额 |
| `ChargeType` | 期货和期权手续费方式，0-未知，1-按元/手，2-按费率 |
| `ChargeOpen` | 开仓手续费率，-1表示没有 |
| `ChargeClose` | 平仓手续费率，-1表示没有 |
| `ChargeTodayOpen` | 开今仓（日内开仓）手续费率，-1表示没有 |
| `ChargeTodayClose` | 平今仓（日内平仓）手续费率，-1表示没有 |
| `OptionType` | 期权类型，-1为非期权，0为期权认购，1为期权认沽 |
| `OpenInterestMultiple` | 交割月持仓倍数 |

> 说明：原字段列表中 `ChargeClose` 出现了两次（重复），此处仅保留一次；同时补全 `ChargeTodayOpen`、`ChargeTodayClose`、`OptionType`、`OpenInterestMultiple` 等字段说明。

### `get_instrument_type(stock_code)`

返回单个品种的类型，常见返回值（因版本而异）：

- `'STOCK'` / `0`：A 股股票
- `'FUND'` / `1`：基金（包括 ETF）
- `'BOND'` / `2`：债券（包括可转债）
- `'INDEX'` / `3`：指数
- `'FUTURES'` / `4`：期货
- `'OPTION'` / `5`：期权

> 注意：不同 QMT/xtquant 版本返回的类型值可能不同，请以实际输出为准。

## 下一步

可以继续学习：

- `01_xtdata_basic/`：行情数据下载与复权
- `02_xtdata_sectors/`：板块与指数成分股
