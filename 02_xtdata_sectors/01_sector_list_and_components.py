# -*- coding: utf-8 -*-
"""
xtdata 板块列表与成分股示例

覆盖接口：
- get_sector_list：获取所有板块分类
- get_stock_list_in_sector：获取指定板块的成分股

运行前提：
1. QMT/迅投终端已启动并登录。
2. 首次查询板块数据时，可能需要先下载板块数据到本地缓存。
3. 不同 QMT 版本返回的板块名称可能略有差异，如果返回空，
   可以先 print 出 get_sector_list() 的全部结果，再挑选可用名称。
"""

import os
import json
from xtquant import xtdata


def get_output_dir():
    """获取当前文件所在目录下的 outputs 目录。"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def demo_sector_list():
    """获取板块列表并打印分类，同时保存到本地文件。"""
    print("=" * 60)
    print("示例 1：获取板块列表")
    print("=" * 60)

    sector_list = xtdata.get_sector_list()
    print(f"共获取到 {len(sector_list)} 个板块/分类")
    print(f"前 30 个：{sector_list[:30]}")
    print()

    # 简单分类展示：通常包含全市场、行业、概念、地域等
    market_sectors = [s for s in sector_list if "A股" in s or "沪深" in s or "上证" in s or "深证" in s]
    industry_sectors = [s for s in sector_list if "行业" in s and "A股" not in s]
    concept_sectors = [s for s in sector_list if "概念" in s]
    region_sectors = [s for s in sector_list if "板块" in s and s not in industry_sectors and s not in concept_sectors]

    print(f"全市场类板块：{market_sectors[:10]}")
    print(f"行业类板块：{industry_sectors[:10]}")
    print(f"概念类板块：{concept_sectors[:10]}")
    print(f"地域类板块：{region_sectors[:10]}")
    print()

    # 保存到文件，方便后续查看和替换示例中的板块名称
    sector_data = {
        "total": len(sector_list),
        "all_sectors": sector_list,
        "market_sectors": market_sectors,
        "industry_sectors": industry_sectors,
        "concept_sectors": concept_sectors,
        "region_sectors": region_sectors,
    }

    json_file = os.path.join(get_output_dir(), "sectors.json")
    txt_file = os.path.join(get_output_dir(), "sectors.txt")

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sector_data, f, ensure_ascii=False, indent=2)
    print(f"[已保存] 板块分类 JSON：{json_file}")

    with open(txt_file, "w", encoding="utf-8") as f:
        for sector in sector_list:
            f.write(sector + "\n")
    print(f"[已保存] 板块列表 TXT：{txt_file}")
    print()

    return sector_list


def find_sectors_by_keyword(sector_list, keyword):
    """
    根据关键词从板块列表中模糊匹配。
    返回所有名称中包含 keyword 的板块列表。
    """
    return [s for s in sector_list if keyword in s]


def demo_sector_components_by_keyword(sector_list, keyword, max_display=20):
    """
    对匹配某个关键词的所有板块，循环打印其成分股。
    """
    matched_sectors = find_sectors_by_keyword(sector_list, keyword)

    print("=" * 60)
    print(f"关键词 '{keyword}' 匹配到 {len(matched_sectors)} 个板块：")
    print("=" * 60)
    if not matched_sectors:
        print(f"未找到包含 '{keyword}' 的板块，请检查 sectors.txt 中的真实名称。")
        print()
        return

    print(f"{matched_sectors}")
    print()

    for sector_name in matched_sectors:
        demo_sector_components(sector_name, max_display=max_display)


def demo_sector_components(sector_name, max_display=20):
    """获取指定板块的成分股。"""
    print("=" * 60)
    print(f"示例 2：获取板块 '{sector_name}' 的成分股")
    print("=" * 60)

    # 先下载板块数据（部分 QMT 版本需要显式下载）
    try:
        xtdata.download_sector_data()
    except Exception as e:
        print(f"download_sector_data 调用提示：{e}")

    stocks = xtdata.get_stock_list_in_sector(sector_name)
    print(f"板块 '{sector_name}' 共有 {len(stocks)} 只成分股")
    print(f"前 {max_display} 只：{stocks[:max_display]}")
    print()


def main():
    # 1. 先看所有板块有哪些，并返回板块列表
    sector_list = demo_sector_list()

    # 2. 全市场板块：沪深A股
    #    如果运行时提示不存在，请先从上面打印的列表里找一个可用的全市场名称
    demo_sector_components("沪深A股", max_display=20)

    # 3. 根据关键词自动匹配行业/概念板块，并循环打印每个匹配板块的成分股
    keywords = ["半导体", "新能源"]
    for keyword in keywords:
        demo_sector_components_by_keyword(sector_list, keyword, max_display=20)

    print("提示：如果某个板块返回空列表，请检查该板块名称在 get_sector_list() 中是否存在，")
    print("      或尝试 QMT 终端中手动刷新一次板块数据。")


if __name__ == "__main__":
    main()
