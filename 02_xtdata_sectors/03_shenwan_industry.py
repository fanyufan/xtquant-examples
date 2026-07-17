# -*- coding: utf-8 -*-
"""
xtdata 申万行业板块示例

覆盖内容：
- 申万一级行业、二级行业、三级行业的板块列表
- 根据关键词匹配申万行业板块
- 获取指定申万行业板块的成分股

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


def demo_shenwan_sector_list():
    """
    获取板块列表，并过滤出申万一级、二级、三级行业板块。
    同时保存到本地文件，方便后续查看。
    """
    print("=" * 60)
    print("示例 1：获取申万行业板块列表")
    print("=" * 60)

    sector_list = xtdata.get_sector_list()
    print(f"共获取到 {len(sector_list)} 个板块/分类")

    # 过滤申万行业板块
    shenwan_level1 = [s for s in sector_list if "申万" in s and "一级" in s]
    shenwan_level2 = [s for s in sector_list if "申万" in s and "二级" in s]
    shenwan_level3 = [s for s in sector_list if "申万" in s and "三级" in s]

    # 如果上面过滤为空，尝试其他常见命名方式
    if not shenwan_level1:
        shenwan_level1 = [s for s in sector_list if "申万" in s and ("1级" in s or "L1" in s or "一级行业" in s)]
    if not shenwan_level2:
        shenwan_level2 = [s for s in sector_list if "申万" in s and ("2级" in s or "L2" in s or "二级行业" in s)]
    if not shenwan_level3:
        shenwan_level3 = [s for s in sector_list if "申万" in s and ("3级" in s or "L3" in s or "三级行业" in s)]

    print(f"申万一级行业：{len(shenwan_level1)} 个")
    print(f"申万二级行业：{len(shenwan_level2)} 个")
    print(f"申万三级行业：{len(shenwan_level3)} 个")
    print()

    print(f"申万一级行业示例：{shenwan_level1[:10]}")
    print(f"申万二级行业示例：{shenwan_level2[:10]}")
    print(f"申万三级行业示例：{shenwan_level3[:10]}")
    print()

    # 保存到文件
    shenwan_data = {
        "total": len(sector_list),
        "shenwan_level1": shenwan_level1,
        "shenwan_level2": shenwan_level2,
        "shenwan_level3": shenwan_level3,
    }

    json_file = os.path.join(get_output_dir(), "shenwan_sectors.json")
    txt_file = os.path.join(get_output_dir(), "shenwan_sectors.txt")

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(shenwan_data, f, ensure_ascii=False, indent=2)
    print(f"[已保存] 申万行业分类 JSON：{json_file}")

    with open(txt_file, "w", encoding="utf-8") as f:
        for sector in shenwan_level1 + shenwan_level2 + shenwan_level3:
            f.write(sector + "\n")
    print(f"[已保存] 申万行业列表 TXT：{txt_file}")
    print()

    return shenwan_level1, shenwan_level2, shenwan_level3


def find_sectors_by_keyword(sector_list, keyword):
    """
    根据关键词从板块列表中模糊匹配。
    返回所有名称中包含 keyword 的板块列表。
    """
    return [s for s in sector_list if keyword in s]


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


def demo_sector_components_by_keyword(sector_list, keyword, max_display=20):
    """
    对匹配某个关键词的所有板块，循环打印其成分股。
    """
    matched_sectors = find_sectors_by_keyword(sector_list, keyword)

    print("=" * 60)
    print(f"关键词 '{keyword}' 匹配到 {len(matched_sectors)} 个板块：")
    print("=" * 60)
    if not matched_sectors:
        print(f"未找到包含 '{keyword}' 的板块，请检查 shenwan_sectors.txt 中的真实名称。")
        print()
        return

    print(f"{matched_sectors}")
    print()

    for sector_name in matched_sectors:
        demo_sector_components(sector_name, max_display=max_display)


def main():
    # 1. 获取申万行业板块列表
    level1, level2, level3 = demo_shenwan_sector_list()

    # 2. 展示几个具体申万行业板块的成分股
    #    如果运行时提示不存在，请先从上面打印的列表里找一个可用的名称
    if level1:
        demo_sector_components(level1[0], max_display=20)
    if level2:
        demo_sector_components(level2[0], max_display=20)
    if level3:
        demo_sector_components(level3[0], max_display=20)

    # 3. 根据关键词自动匹配申万行业板块，并循环打印每个匹配板块的成分股
    keywords = ["半导体", "银行", "医药"]
    all_shenwan = level1 + level2 + level3
    for keyword in keywords:
        demo_sector_components_by_keyword(all_shenwan, keyword, max_display=20)

    print("提示：")
    print("  1. 如果某个板块返回空列表，请检查该板块名称在 get_sector_list() 中是否存在。")
    print("  2. 不同 QMT 版本对申万行业的命名可能不同（如 '申万一级'、'申万一级行业'、'电子(申万一级)' 等）。")
    print("  3. 示例中的关键词（半导体/银行/医药）可能匹配到多个级别，请从输出中挑选需要的板块。")


if __name__ == "__main__":
    main()
