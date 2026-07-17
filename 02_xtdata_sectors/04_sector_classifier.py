# -*- coding: utf-8 -*-
"""
xtdata 板块分类整理工具

功能：
1. 调用 xtdata.get_sector_list() 获取全部板块
2. 按规则自动分类：全市场、ETF、期货、申万一级/二级/三级行业、指数申万交叉（中证1000/中证500/沪深300/港股 × 申万行业）、可转债申万交叉（转债 × 申万行业）、G 一/二/三/四级行业板块、证监会行业一/二/三/四级、同花顺行业/概念、通达信概念/风格、其他行业、概念、地域（一/二级）、指数、风格、主题、其他
3. 把分类结果保存到单独的 JSON/TXT/CSV 文件，方便查找和使用

申万行业识别规则（当前 QMT 版本）：
- SW1 开头：申万一级行业
- SW2 开头：申万二级行业
- SW3 开头：申万三级行业
- 包含 SW港股通：申万一级行业（港股）

同花顺板块识别规则：
- TGN 开头：同花顺概念板块
- THY 开头：同花顺行业板块

通达信板块识别规则：
- TDGN 开头：通达信概念板块
- TFG 开头：通达信风格板块

指数申万交叉板块识别规则：
- 1000SW1 / 1000SW2：中证1000 × 申万一级 / 二级行业
- 500SW1 / 500SW2：中证500 × 申万一级 / 二级行业
- 300SW1 / 300SW2：沪深300 × 申万一级 / 二级行业
- HKSW1 / HKSW2 / HKSW3：港股 × 申万一级 / 二级 / 三级行业

可转债申万交叉板块识别规则：
- 转债SW1：可转债 × 申万一级行业
- 转债SW2：可转债 × 申万二级行业
- 转债SW3：可转债 × 申万三级行业

GICS 行业识别规则：
- GICS1 开头：G 一级行业板块
- GICS2 开头：G 二级行业板块
- GICS3 开头：G 三级行业板块
- GICS4 开头：G 四级行业板块

证监会行业识别规则：
- CSRC1 开头：证监会行业板块一级
- CSRC2 开头：证监会行业板块二级
- CSRC3 开头：证监会行业板块三级
- CSRC4 开头：证监会行业板块四级

概念板块识别规则：
- 名称包含"概念"或 GN 开头：归入概念板块

地域板块识别规则：
- DY1 开头：一级地域板块
- DY2 开头：二级地域板块

ETF 板块识别规则：
- 名称包含 ETF：归入 ETF 板块

期货板块识别规则：
- 名称包含"期货"：归入期货板块

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

        # 2. ETF 板块
        if "ETF" in sector:
            categories["ETF 板块"].append(sector)
            classified.add(sector)
            continue

        # 3. 期货板块
        if "期货" in sector:
            categories["期货板块"].append(sector)
            classified.add(sector)
            continue

        # 4. 申万行业板块（按 SW1/SW2/SW3 前缀细分）
        if "SW港股通" in sector:
            categories["申万一级行业板块（港股）"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("SW1"):
            categories["申万一级行业板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("SW2"):
            categories["申万二级行业板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("SW3"):
            categories["申万三级行业板块"].append(sector)
            classified.add(sector)
            continue
        # 兼容旧命名：包含"申万"但不以 SW 开头
        if "申万" in sector:
            categories["申万行业板块（其他命名）"].append(sector)
            classified.add(sector)
            continue

        # 5. 指数申万交叉板块（按具体指数和申万级别细分）
        if sector.startswith("1000SW1"):
            categories["中证1000 × 申万一级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("1000SW2"):
            categories["中证1000 × 申万二级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("500SW1"):
            categories["中证500 × 申万一级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("500SW2"):
            categories["中证500 × 申万二级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("300SW1"):
            categories["沪深300 × 申万一级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("300SW2"):
            categories["沪深300 × 申万二级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("HKSW1"):
            categories["港股 × 申万一级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("HKSW2"):
            categories["港股 × 申万二级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("HKSW3"):
            categories["港股 × 申万三级行业"].append(sector)
            classified.add(sector)
            continue

        # 6. 可转债申万交叉板块（按转债SW1/SW2/SW3 前缀细分）
        if sector.startswith("转债SW1"):
            categories["可转债 × 申万一级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("转债SW2"):
            categories["可转债 × 申万二级行业"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("转债SW3"):
            categories["可转债 × 申万三级行业"].append(sector)
            classified.add(sector)
            continue

        # 7. GICS 行业板块（按 GICS1/GICS2/GICS3/GICS4 前缀细分）
        if sector.startswith("GICS1"):
            categories["G 一级行业板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("GICS2"):
            categories["G 二级行业板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("GICS3"):
            categories["G 三级行业板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("GICS4"):
            categories["G 四级行业板块"].append(sector)
            classified.add(sector)
            continue

        # 8. 证监会行业板块（按 CSRC1/CSRC2/CSRC3/CSRC4 前缀细分）
        if sector.startswith("CSRC1"):
            categories["证监会行业板块一级"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("CSRC2"):
            categories["证监会行业板块二级"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("CSRC3"):
            categories["证监会行业板块三级"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("CSRC4"):
            categories["证监会行业板块四级"].append(sector)
            classified.add(sector)
            continue

        # 9. 同花顺板块（按 TGN/THY 前缀细分）
        if sector.startswith("TGN"):
            categories["同花顺概念板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("THY"):
            categories["同花顺行业板块"].append(sector)
            classified.add(sector)
            continue

        # 10. 地域板块（按 DY1/DY2 前缀细分）
        if sector.startswith("DY1"):
            categories["一级地域板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("DY2"):
            categories["二级地域板块"].append(sector)
            classified.add(sector)
            continue

        # 11. 通达信板块（按 TDGN/TFG 前缀细分）
        if sector.startswith("TDGN"):
            categories["通达信概念板块"].append(sector)
            classified.add(sector)
            continue
        if sector.startswith("TFG"):
            categories["通达信风格板块"].append(sector)
            classified.add(sector)
            continue

        # 12. 概念板块（包含 GN 前缀的板块，GN 通常代表"概念"）
        if "概念" in sector or sector.startswith("GN"):
            categories["概念板块"].append(sector)
            classified.add(sector)
            continue

        # 13. 其他行业板块
        if "行业" in sector:
            categories["其他行业板块"].append(sector)
            classified.add(sector)
            continue

        # 14. 指数板块
        if "指数" in sector:
            categories["指数板块"].append(sector)
            classified.add(sector)
            continue

        # 15. 风格板块
        if any(kw in sector for kw in STYLE_KEYWORDS):
            categories["风格板块"].append(sector)
            classified.add(sector)
            continue

        # 16. 主题板块
        if "主题" in sector:
            categories["主题板块"].append(sector)
            classified.add(sector)
            continue

        # 17. 地域板块（按关键词匹配）
        if any(kw in sector for kw in REGION_KEYWORDS) or ("板块" in sector and sector not in classified):
            categories["地域板块"].append(sector)
            classified.add(sector)
            continue

        # 18. 其他未分类
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
    print("  1. 名称包含 ETF 的板块归入 ETF 板块。")
    print("  2. 名称包含\"期货\"的板块归入期货板块。")
    print("  3. 申万行业按 SW1/SW2/SW3 前缀区分一/二/三级行业，SW港股通 为申万一级行业（港股）。")
    print("  4. 指数申万交叉板块按 1000SW1/1000SW2（中证1000）、500SW1/500SW2（中证500）、300SW1/300SW2（沪深300）、HKSW1/HKSW2/HKSW3（港股）细分。")
    print("  5. 可转债申万交叉板块按转债SW1/SW2/SW3 前缀区分一/二/三级行业。")
    print("  6. GICS 行业板块按 GICS1/GICS2/GICS3/GICS4 前缀区分一/二/三/四级。")
    print("  7. 证监会行业板块按 CSRC1/CSRC2/CSRC3/CSRC4 前缀区分一/二/三/四级。")
    print("  8. 同花顺板块按 TGN（概念）/THY（行业）前缀区分。")
    print("  9. 地域板块按 DY1（一级）/DY2（二级）前缀区分。")
    print("  10. 通达信概念板块按 TDGN 前缀区分，通达信风格板块按 TFG 前缀区分。")
    print("  11. 名称包含\"概念\"或 GN 开头的板块归入概念板块。")
    print("  12. 分类规则基于关键词匹配，可能不完美，请根据实际结果调整。")
    print("  13. 输出文件 sector_classification.json/txt/csv 可直接用于查找板块名称。")
    print("  14. 如需更精确分类，可打开 JSON 文件查看全部板块并手工调整规则。")


if __name__ == "__main__":
    main()
