# xtdata 行情数据示例

本目录包含 `xtquant.xtdata` 行情接口的入门示例，覆盖 A 股股票、可转债、ETF 三类资产的日 K 线、分钟 K 线、实时行情订阅，以及复权因子相关内容。

## 文件说明

| 文件 | 内容 |
|------|------|
| `01_historical_data.py` | 历史行情数据下载：日 K 线、分钟 K 线，股票 / 可转债 / ETF |
| `02_realtime_data.py` | 实时行情订阅：tick / 分钟线回调示例 |
| `03_dividend_factors.py` | 复权因子：get_divid_factors、复权价格计算、收益率对比 |

## 运行前准备

1. **安装 xtquant**
   - 如果你使用的是 QMT 内置的 Python 环境，通常已经集成 `xtquant`。
   - 如果在外部 Python 环境使用，需先安装：
     ```bash
     pip install xtquant
     ```

2. **启动 QMT 终端并登录**
   - `xtdata` 需要连接 QMT/迅投终端才能获取数据。
   - 未登录时调用接口可能会返回空数据或报错。

3. **首次运行会下载数据到本地缓存**
   - 下载速度取决于网络和数据量，请耐心等待。
   - 下载完成后，再次读取会很快。

## 运行方式

```bash
python 01_xtdata_basic/01_historical_data.py
python 01_xtdata_basic/02_realtime_data.py
python 01_xtdata_basic/03_dividend_factors.py
```

> 注意：运行 `03_dividend_factors.py` 前，请确认你的 xtquant 版本支持 `get_divid_factors` 接口。如果不支持，脚本会跳过手动计算部分，仅展示 `get_market_data` 自带的前复权/后复权结果。

## 代码规则说明

- 股票：`000001.SZ`（深圳）、`600000.SH`（上海）
- 可转债：`128136.SZ`（深圳）、`113XXX.SH`（上海）
- ETF：`510050.SH`（上海）、`159915.SZ`（深圳）

> 提示：示例中的可转债代码 `128136.SZ` 仅作格式参考，实际使用前请替换为你当前能交易的品种代码。

## 常用 `period` 参数

| period | 含义 |
|--------|------|
| `tick` | 逐笔 tick |
| `1m`   | 1 分钟 K 线 |
| `5m`   | 5 分钟 K 线 |
| `1d`   | 日 K 线 |

## 下一步

行情数据跑通后，可以继续学习 `xttrader` 交易接口：

- 查询资金、持仓
- 下单、撤单
- 订阅成交回报

参见后续示例目录 `03_xttrader_basic/`。
