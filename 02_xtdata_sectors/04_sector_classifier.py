# -*- coding: utf-8 -*-
"""
xtdata 板块分类整理工具

功能：
1. 调用 xtdata.get_sector_list() 获取全部板块
2. 按规则自动分类：全市场、申万行业、其他行业、概念、地域、指数、风格、主题、其他
3. 把分类结果保存到单独的 JSON/TXT/CSV 文件，方便查找和使用

运行前提：QMT/迅投终端已启动并登录。
"""

import os
import json
import csv
from collections import defaultdict
from xtquant import xtdata


def get_output_dir():
    """获取当前文件所在目录下的 outputs 目录。"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


# 常见地域关键词（省市自治区、直辖市）
REGION_KEYWORDS = [
    "北京", "上海", "天津", "重庆",
    "河北", "山西", "辽宁", "吉林", "黑龙江",
    "江苏", "浙江", "安徽", "福建", "江西", "山东",
    "河南", "湖北", "湖南", "广东", "海南",
    "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾",
    "内蒙古", "广西", "西藏", "宁夏", "新疆",
    "香港", "澳门",
]

# 风格关键词
STYLE_KEYWORDS = ["风格", "价值", "成长", "大盘", "小盘", "中盘", "蓝筹", "新兴", "龙头", "白马"]


def classify_sectors(sector_list):
    """
    对板块列表进行分类。

    返回 dict：{category: [sector_name, ...]}
    """
    categories = defaultdict(list)
    classified = set()

    for sector in sector_list:
        # 1. 全市场板块
        if any(kw in sector for kw in ["A股", "沪深", "上证", "深证", "全部", "市场", "所有"]):
            categories["全市场板块"].append(sector)
            classified.add(sector)
            continue

        # 2. 申万行业板块
        if "申万" in sector:
            categories["申万行业板块"].append(sector)
            classified.add(sector)
            continue

        # 3. 其他行业板块
        if "行业" in sector:
            categories["其他行业板块"].append(sector)
            classified.add(sector)
            continue

        # 4. 概念板块
        if "概念" in sector:
            categories["概念板块"].append(sector)
            classified.add(sector)
            continue

        # 5. 指数板块
        if "指数" in sector:
            categories["指数板块"].append(sector)
            classified.add(sector)
            continue

        # 6. 风格板块
        if any(kw in sector for kw in STYLE_KEYWORDS):
            categories["风格板块"].append(sector)
            classified.add(sector)
            continue

        # 7. 主题板块
        if "主题" in sector:
            categories["主题板块"].append(sector)
            classified.add(sector)
            continue

        # 8. 地域板块
        if any(kw in sector for kw in REGION_KEYWORDS) or ("板块" in sector and sector not in classified):
            categories["地域板块"].append(sector)
            classified.add(sector)
            continue

        # 9. 其他未分类
        categories["其他板块"].append(sector)

    return dict(categories)


def save_to_json(categories, total, filename=None):
    """保存分类结果到 JSON 文件。"""
    if filename is None:
        filename = os.path.join(get_output_dir(), "sector_classification.json")
    data = {
        "total": total,
        "categories": {k: len(v) for k, v in categories.items()},
        "data": categories,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[已保存] 分类结果 JSON：{filename}")


def save_to_txt(categories, filename=None):
    """保存分类结果到 TXT 文件，每个分类一个段落。"""
    if filename is None:
        filename = os.path.join(get_output_dir(), "sector_classification.txt")
    with open(filename, "w", encoding="utf-8") as f:
        for category, sectors in categories.items():
            f.write(f"\n{'=' * 60}\n")
            f.write(f"{category}（共 {len(sectors)} 个）\n")
            f.write(f"{'=' * 60}\n")
            for sector in sectors:
                f.write(sector + "\n")
    print(f"[已保存] 分类结果 TXT：{filename}")


def save_to_csv(categories, filename=None):
    """保存分类结果到 CSV 文件，每行一个板块及其分类。"""
    if filename is None:
        filename = os.path.join(get_output_dir(), "sector_classification.csv")
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "sector_name"])
        for category, sectors in categories.items():
            for sector in sectors:
                writer.writerow([category, sector])
    print(f"[已保存] 分类结果 CSV：{filename}")


def print_summary(categories, total):
    """打印分类统计摘要。"""
    print("\n" + "=" * 60)
    print("板块分类统计")
    print("=" * 60)
    print(f"总板块数：{total}")
    print()
    for category, sectors in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"  {category}: {len(sectors)} 个")
    print()


def main():
    print("=" * 60)
    print("xtdata 板块分类整理工具")
    print("=" * 60)

    # 1. 获取全部板块列表
    sector_list = xtdata.get_sector_list()
    total = len(sector_list)
    print(f"共获取到 {total} 个板块/分类")
    print(f"前 10 个：{sector_list[:10]}")
    print()

    # 2. 自动分类
    categories = classify_sectors(sector_list)

    # 3. 打印统计摘要
    print_summary(categories, total)

    # 4. 保存到文件
    save_to_json(categories, total)
    save_to_txt(categories)
    save_to_csv(categories)

    # 5. 打印部分示例
    print("=" * 60)
    print("各类别示例")
    print("=" * 60)
    for category, sectors in categories.items():
        print(f"\n{category}（共 {len(sectors)} 个），示例：")
        print(f"  {sectors[:10]}")

    print("\n提示：")
    print("  1. 分类规则基于关键词匹配，可能不完美，请根据实际结果调整。")
    print("  2. 输出文件 sector_classification.json/txt/csv 可直接用于查找板块名称。")
    print("  3. 如需更精确分类，可打开 JSON 文件查看全部板块并手工调整规则。")


if __name__ == "__main__":
    main()
