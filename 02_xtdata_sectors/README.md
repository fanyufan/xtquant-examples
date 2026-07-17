# xtdata 板块与指数成分股示例

本目录展示 `xtquant.xtdata` 中板块分类和指数成分股相关的接口。

## 文件说明

| 文件 | 内容 |
|------|------|
| `01_sector_list_and_components.py` | `get_sector_list` 板块列表 + `get_stock_list_in_sector` 板块成分股 |
| `02_index_components.py` | `get_index_stock_list` 指数成分股 + 成分股行情快照 |
| `03_shenwan_industry.py` | 申万一级/二级/三级行业板块列表与成分股 |
| `04_sector_classifier.py` | 自动分类整理 7104 个板块到 JSON/TXT/CSV |

## 运行前准备

1. QMT/迅投终端已启动并登录。
2. 已安装 `xtquant` 包。
3. 首次运行可能需要先下载板块/指数数据到本地缓存，请保持网络畅通。

## 运行方式

```bash
python 02_xtdata_sectors/01_sector_list_and_components.py
python 02_xtdata_sectors/02_index_components.py
python 02_xtdata_sectors/03_shenwan_industry.py
python 02_xtdata_sectors/04_sector_classifier.py
```

## 常见板块名称说明

不同 QMT 版本返回的板块名称可能不同，常见类别包括：

- 全市场板块：`沪深A股`、`上证A股`、`深证A股` 等
- 行业板块：`半导体`、`银行`、`医药生物`、`电力设备` 等
- 概念板块：`新能源`、`人工智能`、`央企改革` 等
- 地域板块：`北京板块`、`上海板块`、`广东板块` 等

如果示例中的某个板块名称不存在，请先运行 `01_sector_list_and_components.py`，
从 `get_sector_list()` 的打印结果中挑选可用的名称替换。

## 板块自动分类规则说明

`04_sector_classifier.py` 会调用 `xtdata.get_sector_list()` 获取全部板块，并按以下规则自动归类，
结果保存到 `outputs/sector_classification.json`、`outputs/sector_classification.txt` 和 `outputs/sector_classification.csv`。

### 按前缀识别的分类体系

| 前缀 | 分类名称 | 说明 |
|------|---------|------|
| `SW1` / `SW2` / `SW3` | 申万一级 / 二级 / 三级行业板块 | 申万行业分类 |
| `SW港股通` | 申万一级行业板块（港股） | 港股通申万一级行业 |
| `1000SW` / `500SW` / `300SW` / `HKSW` | 指数申万交叉板块 | 中证1000/中证500/沪深300/港股 × 申万行业交叉分类 |
| `GICS1` / `GICS2` / `GICS3` / `GICS4` | G 一级 / 二级 / 三级 / 四级行业板块 | GICS 全球行业分类 |
| `CSRC1` / `CSRC2` / `CSRC3` / `CSRC4` | 证监会行业板块一级 / 二级 / 三级 / 四级 | 中国证监会行业分类 |
| `TGN` / `THY` | 同花顺概念板块 / 同花顺行业板块 | 同花顺概念与行业 |
| `TDGN` / `TFG` | 通达信概念板块 / 通达信风格板块 | 通达信概念与风格 |

### 其他分类

除上述前缀体系外，还会按关键词归类为：

- 全市场板块
- 其他行业板块
- 概念板块
- 指数板块
- 风格板块
- 主题板块
- 地域板块
- 其他未分类板块

> 注意：分类规则基于关键词/前缀匹配，不同 QMT 版本返回的板块名称可能略有差异，
> 实际归类结果请以运行 `04_sector_classifier.py` 后的输出为准。如需调整规则，
> 可直接修改 `04_sector_classifier.py` 中的 `classify_sectors()` 函数。

## 常见指数代码

| 指数名称 | 代码 |
|---------|------|
| 沪深300 | `000300.SH` |
| 中证500 | `000905.SH` |
| 上证50 | `000016.SH` |
| 创业板指 | `399006.SZ` |
| 创业板50 | `399673.SZ` |
| 科创50 | `000688.SH` |

> 提示：不同 QMT 版本对指数代码的格式要求可能不同，如返回空可尝试不带后缀的写法（如 `000300`）。

## 常用接口速查

```python
# 获取板块列表
sectors = xtdata.get_sector_list()

# 获取板块成分股
stocks = xtdata.get_stock_list_in_sector("沪深A股")

# 获取指数成分股
stocks = xtdata.get_index_stock_list("000300.SH")

# 下载板块数据（部分版本需要）
xtdata.download_sector_data()
```
