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
