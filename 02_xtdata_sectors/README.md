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
