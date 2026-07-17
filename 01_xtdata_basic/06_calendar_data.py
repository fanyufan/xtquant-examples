# -*- coding: utf-8 -*-
"""
xtdata 交易日历示例

覆盖内容：
- 使用 get_trading_dates() 获取指定市场的交易日列表
- 常见应用场景：判断某日是否交易日、获取区间交易日、获取未来 N 个交易日

接口说明：
- xtdata.get_trading_dates(market, start_time='', end_time='', count=-1)
  参数：
    market     - 市场代码，如 "SH"（上海）、"SZ"（深圳）、"BJ"（北京）
    start_time - 起始时间，8 位字符串
    end_time   - 结束时间，8 位字符串
    count      - 返回数据个数，-1 表示返回全部
  返回：list[str]，完整交易日列表

运行前提：QMT/迅投终端已启动并登录。
"""

import os
from datetime import datetime, timedelta
from xtquant import xtdata


def get_output_dir():
    """获取当前文件所在目录下的 outputs 目录。"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def demo_get_trading_dates(market="SH", start_time="", end_time="", count=-1):
    """示例 1：获取指定市场的交易日列表。"""
    print("=" * 60)
    print(f"示例 1：获取 '{market}' 市场交易日列表")
    print("=" * 60)

    try:
        trading_days = xtdata.get_trading_dates(market, start_time, end_time, count)
    except Exception as e:
        print(f"  get_trading_dates({market}, {start_time}, {end_time}, {count}) 调用失败：{e}")
        print()
        print("  可能原因：")
        print("    1. 当前 QMT 客户端版本过低，不支持 get_trading_dates 接口。")
        print("    2. 当前账号权限不足，需要更新客户端或升级投研版。")
        print("    3. 该接口在你使用的 xtquant / QMT 版本中尚未实现（function not realize）。")
        print()
        return []

    # 统一转换为字符串，避免后续比较时出现 str vs int 类型错误
    trading_days = [str(d) for d in trading_days]

    print(f"  共获取到 {len(trading_days)} 个交易日")
    if trading_days:
        print(f"  起始日期：{trading_days[0]}")
        print(f"  结束日期：{trading_days[-1]}")
        print(f"  前 5 个交易日：{trading_days[:5]}")
        print(f"  后 5 个交易日：{trading_days[-5:]}")
    print()
    return trading_days


def _to_str(value):
    """将日期值统一转换为 8 位字符串，兼容 int / str 输入。"""
    return str(value).strip()


def is_trading_day(date_str, trading_days):
    """判断指定日期是否为交易日。"""
    return _to_str(date_str) in trading_days


def get_trading_days_between(start_date, end_date, trading_days):
    """获取指定日期区间内的所有交易日。"""
    start = _to_str(start_date)
    end = _to_str(end_date)
    return [d for d in trading_days if start <= d <= end]


def get_next_n_trading_days(base_date, n, trading_days):
    """获取 base_date 之后的第 n 个交易日（包含跨越节假日）。"""
    base = _to_str(base_date)
    future_days = [d for d in trading_days if d > base]
    if len(future_days) < n:
        return None
    return future_days[n - 1]


def get_prev_n_trading_days(base_date, n, trading_days):
    """获取 base_date 之前的第 n 个交易日。"""
    base = _to_str(base_date)
    past_days = [d for d in trading_days if d < base]
    if len(past_days) < n:
        return None
    return past_days[-n]


def demo_common_usages(trading_days_sh):
    """示例 3：常见应用场景。"""
    print("=" * 60)
    print("示例 3：交易日历常见应用")
    print("=" * 60)

    # 场景 1：判断今天是否交易日
    today = datetime.now().strftime("%Y%m%d")
    print(f"  今天：{today}")
    print(f"  今天是否交易日：{is_trading_day(today, trading_days_sh)}")
    print()

    # 场景 2：获取近 30 天的交易日
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    recent_trading_days = get_trading_days_between(thirty_days_ago, today, trading_days_sh)
    print(f"  最近 30 天内交易日数量：{len(recent_trading_days)}")
    print(f"  最近 5 个交易日：{recent_trading_days[-5:]}")
    print()

    # 场景 3：获取未来第 5 个交易日
    next_5th = get_next_n_trading_days(today, 5, trading_days_sh)
    print(f"  从今天起第 5 个交易日：{next_5th}")

    # 场景 4：获取过去第 3 个交易日
    prev_3rd = get_prev_n_trading_days(today, 3, trading_days_sh)
    print(f"  今天往前第 3 个交易日：{prev_3rd}")
    print()


def save_trading_days(trading_days_sh):
    """将交易日历保存到本地文本文件。"""
    output_dir = get_output_dir()

    trading_file = os.path.join(output_dir, "trading_calendar_SH.txt")
    with open(trading_file, "w", encoding="utf-8") as f:
        f.write("\n".join(trading_days_sh))
    print(f"[已保存] 上海市场交易日历：{trading_file}")
    print()


def main():
    # 1. 获取上海市场交易日列表（近三年）
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y%m%d")
    trading_days_sh = demo_get_trading_dates("SH", start_date, end_date)

    # 2. 常见应用场景
    if trading_days_sh:
        demo_common_usages(trading_days_sh)

    # 3. 保存结果
    if trading_days_sh:
        save_trading_days(trading_days_sh)

    print("提示：")
    print("  1. get_trading_dates() 可获取指定区间或指定数量的交易日列表。")
    print("  2. 不同市场（SH/SZ/BJ）的交易日历基本一致，但可能存在细微差异。")
    print("  3. 若 get_trading_dates 报 'function not realize'，说明当前 QMT 客户端/账号不支持该接口，")
    print("     可尝试更新客户端版本或联系券商开通投研版权限。")


if __name__ == "__main__":
    main()
