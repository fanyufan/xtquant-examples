# xtquant-examples

迅投 QMT `xtquant` 实战示例集：xtdata 行情数据下载与订阅、xttrader 模拟/实盘交易、资金流向监控等可直接运行的 Demo。

## 目录结构

```text
.
├── 01_xtdata_basic/          # 行情数据入门
│   ├── 01_historical_data.py  # 历史日 K / 分钟 K 数据
│   ├── 02_realtime_data.py    # 实时 tick / 分钟线订阅
│   ├── 03_dividend_factors.py # 复权因子与复权价格计算
│   └── README.md
├── 02_xtdata_sectors/        # 板块与指数成分股
│   ├── 01_sector_list_and_components.py  # 板块列表与成分股
│   ├── 02_index_components.py             # 指数成分股
│   └── README.md
├── LICENSE
└── README.md
```

## 快速开始

1. 安装 `xtquant`（QMT 内置环境通常已集成）：
   ```bash
   pip install xtquant
   ```
2. 启动 QMT/迅投终端并登录。
3. 进入对应目录运行示例：
   ```bash
   python 01_xtdata_basic/01_historical_data.py
   python 01_xtdata_basic/02_realtime_data.py
   python 01_xtdata_basic/03_dividend_factors.py
   python 02_xtdata_sectors/01_sector_list_and_components.py
   python 02_xtdata_sectors/02_index_components.py
   ```

## 计划中的示例

- `03_xttrader_basic/`：交易接口（查询、下单、撤单、成交回报）
- `04_strategies/`：完整策略闭环（行情 → 信号 → 交易）

欢迎按需补充或反馈。
