# xtquant-examples

迅投 QMT `xtquant` 实战示例集：xtdata 行情数据下载与订阅、xttrader 模拟/实盘交易、资金流向监控等可直接运行的 Demo。

## 目录结构

```text
.
├── 01_xtdata_basic/          # 行情数据入门
│   ├── 01_historical_data.py  # 历史日 K / 分钟 K 数据
│   ├── 02_realtime_data.py    # 实时 tick / 分钟线订阅
│   ├── 03_dividend_factors.py # 复权因子与复权价格计算
│   ├── 04_dividend_types.py   # 不同复权方式对比
│   └── README.md
├── 02_xtdata_sectors/        # 板块与指数成分股
│   ├── 01_sector_list_and_components.py  # 板块列表与成分股
│   ├── 02_index_components.py             # 指数成分股
│   ├── 03_shenwan_industry.py             # 申万行业板块
│   ├── 04_sector_classifier.py            # 板块自动分类整理
│   └── README.md
├── 03_xtdata_instruments/    # 品种信息查询
│   ├── 01_instrument_detail.py  # 品种详情查询
│   ├── 02_instrument_type.py    # 品种类型查询
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
   python 01_xtdata_basic/04_dividend_types.py
   python 02_xtdata_sectors/01_sector_list_and_components.py
   python 02_xtdata_sectors/02_index_components.py
   python 02_xtdata_sectors/03_shenwan_industry.py
   python 02_xtdata_sectors/04_sector_classifier.py
   python 03_xtdata_instruments/01_instrument_detail.py
   python 03_xtdata_instruments/02_instrument_type.py
   ```

## 计划中的示例

- `03_xttrader_basic/`：交易接口（查询、下单、撤单、成交回报）
- `04_strategies/`：完整策略闭环（行情 → 信号 → 交易）

欢迎按需补充或反馈。
