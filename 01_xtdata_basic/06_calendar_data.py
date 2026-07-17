# -*- coding: utf-8 -*-
"""
xtdata 交易日历示例

覆盖内容：
- 使用 get_trading_dates() 获取指定市场的交易日列表
- 常见应用场景：判断某日是否交易日、获取区间交易日、获取未来/过去 N 个交易日
- 同时对比多个市场（SH / SZ / BJ）的交易日历

接口说明：
- xtdata.get_trading_dates(market, start_time='', end_time='', count=-1)
  参数：
    market     - 市场代码，如 "SH"（上海）、"SZ"（深圳）、"BJ"（北京）
    start_time - 起始时间，8 位字符串
    end_time   - 结束时间，8 位字符串
    count      - 返回数据个数，-1 表示返回全部；正数表示从 start_time 起取 count 个
  返回：list[str]，完整交易日列表（统一为 8 位 YYYYMMDD 字符串，便于比较与格式化）

运行前提：QMT/迅投终端已启动并登录。
"""

import os
from datetime import datetime, timedelta
from xtquant import xtdata


# ==================== 基础配置 ====================
# 示例市场：上海、深圳、北京
MARKETS = ["SH", "SZ", "BJ"]

# 默认查询时间范围：近三年
END_DATE = datetime.now().strftime("%Y%m%d")
START_DATE = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y%m%d")


def get_output_dir():
    """获取当前文件所在目录下的 outputs 目录。"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def _to_str(value):
    """将日期值统一转换为字符串，兼容 int / str 输入。"""
    return str(value).strip()


def normalize_date(value):
    """
    将各种日期格式统一转换为 8 位日期字符串（YYYYMMDD）。

    支持的输入格式：
    - 8 位日期字符串 / 整数："20230718" / 20230718
    - 13 位毫秒时间戳字符串 / 整数："1689609600000" / 1689609600000
    """
    s = _to_str(value)
    if not s:
        return s

    # 13 位毫秒时间戳 -> 北京时间日期字符串
    if len(s) == 13 and s.isdigit():
        from datetime import timezone
        ts_ms = int(s)
        # 毫秒时间戳默认是 UTC，转换到北京时间
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).astimezone()
        return dt.strftime("%Y%m%d")

    # 已经是 8 位 YYYYMMDD 格式
    if len(s) == 8 and s.isdigit():
        return s

    # 其他格式尝试按原样返回
    return s


def format_date(date_value):
    """
    将日期值格式化为 YYYY-MM-DD，便于阅读。

    支持 8 位日期字符串、13 位毫秒时间戳等。
    """
    s = normalize_date(date_value)
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return s


def get_trading_dates(market="SH", start_time="", end_time="", count=-1):
    """
    获取指定市场的交易日列表。

    参数：
        market: 市场代码，如 "SH"
        start_time: 起始时间，8 位字符串
        end_time: 结束时间，8 位字符串
        count: 返回数量，-1 表示全部

    返回：
        list[str]: 交易日列表（已统一转换为字符串）
    """
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

    # 统一转换为 8 位日期字符串，避免后续比较时出现 str vs int 类型错误
    # 同时把毫秒时间戳（如 1689609600000）转换成 YYYYMMDD，便于后续格式化输出
    return [normalize_date(d) for d in trading_days]


def demo_get_trading_dates(market="SH", start_time="", end_time="", count=-1):
    """示例 1：获取指定市场的交易日列表。"""
    print("=" * 60)
    print(f"示例 1：获取 '{market}' 市场交易日列表")
    print("=" * 60)
    print(f"  参数：start_time={start_time}, end_time={end_time}, count={count}")

    trading_days = get_trading_dates(market, start_time, end_time, count)
    if not trading_days:
        return []

    print(f"  共获取到 {len(trading_days)} 个交易日")
    print(f"  起始日期：{format_date(trading_days[0])}")
    print(f"  结束日期：{format_date(trading_days[-1])}")
    print(f"  前 5 个交易日：{[format_date(d) for d in trading_days[:5]]}")
    print(f"  后 5 个交易日：{[format_date(d) for d in trading_days[-5:]]}")
    print()
    return trading_days


def is_trading_day(date_str, trading_days):
    """判断指定日期是否为交易日。"""
    return _to_str(date_str) in trading_days


def get_trading_days_between(start_date, end_date, trading_days):
    """获取指定日期区间内的所有交易日。"""
    start = _to_str(start_date)
    end = _to_str(end_date)
    return [d for d in trading_days if start <= d <= end]


def get_trading_day_count(start_date, end_date, trading_days):
    """获取指定日期区间内的交易日数量。"""
    return len(get_trading_days_between(start_date, end_date, trading_days))


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


def demo_common_usages(trading_days, market="SH"):
    """示例 2：交易日历常见应用。"""
    print("=" * 60)
    print(f"示例 2：'{market}' 市场交易日历常见应用")
    print("=" * 60)

    if not trading_days:
        print("  没有可用的交易日数据，跳过应用场景演示。")
        print()
        return

    today = datetime.now().strftime("%Y%m%d")

    # 场景 1：判断今天是否交易日
    print(f"  今天：{format_date(today)}")
    print(f"  今天是否交易日：{is_trading_day(today, trading_days)}")
    print()

    # 场景 2：获取近 30 天的交易日
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    recent_trading_days = get_trading_days_between(thirty_days_ago, today, trading_days)
    print(f"  最近 30 天内交易日数量：{len(recent_trading_days)}")
    print(f"  最近 5 个交易日：{[format_date(d) for d in recent_trading_days[-5:]]}")
    print()

    # 场景 3：获取未来第 5 个交易日
    next_5th = get_next_n_trading_days(today, 5, trading_days)
    print(f"  从今天起第 5 个交易日：{format_date(next_5th) if next_5th else 'N/A'}")

    # 场景 4：获取过去第 3 个交易日
    prev_3rd = get_prev_n_trading_days(today, 3, trading_days)
    print(f"  今天往前第 3 个交易日：{format_date(prev_3rd) if prev_3rd else 'N/A'}")
    print()

    # 场景 5：区间交易日数量统计
    start_of_year = f"{datetime.now().year}0101"
    count_ytd = get_trading_day_count(start_of_year, today, trading_days)
    print(f"  今年以来（{format_date(start_of_year)} ~ {format_date(today)}）交易日数量：{count_ytd}")
    print()


def demo_count_parameter():
    """示例 3：使用 count 参数获取固定数量的交易日。"""
    print("=" * 60)
    print("示例 3：使用 count 参数获取未来 10 个交易日")
    print("=" * 60)

    today = datetime.now().strftime("%Y%m%d")
    trading_days = get_trading_dates("SH", today, count=10)
    if trading_days:
        print(f"  从 {format_date(today)} 起未来 10 个交易日：")
        for i, d in enumerate(trading_days, 1):
            print(f"    T+{i:2d}: {format_date(d)}")
    print()


def compare_market_calendars(markets, start_time, end_time):
    """示例 4：对比多个市场的交易日历差异。"""
    print("=" * 60)
    print(f"示例 4：对比市场 {markets} 的交易日历")
    print("=" * 60)

    calendars = {}
    for market in markets:
        days = get_trading_dates(market, start_time, end_time)
        calendars[market] = set(days)
        print(f"  {market}: {len(days)} 个交易日")

    if len(calendars) < 2:
        print()
        return

    # 找出差异日期
    all_days = set()
    for days in calendars.values():
        all_days |= days

    diff_dates = sorted([d for d in all_days if not all(d in c for c in calendars.values())])
    if diff_dates:
        print(f"  存在差异的日期（共 {len(diff_dates)} 个）：")
        for d in diff_dates:
            status = {m: ("交易日" if d in cal else "非交易日") for m, cal in calendars.items()}
            print(f"    {format_date(d)}: {status}")
    else:
        print("  各市场交易日历完全一致。")
    print()


def save_trading_days(trading_days, market="SH"):
    """将交易日历保存到本地文本文件。"""
    if not trading_days:
        return

    output_dir = get_output_dir()
    trading_file = os.path.join(output_dir, f"trading_calendar_{market}.txt")
    with open(trading_file, "w", encoding="utf-8") as f:
        f.write("\n".join(format_date(d) for d in trading_days))
    print(f"[已保存] {market} 市场交易日历：{trading_file}")
    print()


def main():
    print("=" * 60)
    print("xtdata 交易日历示例")
    print("=" * 60)
    print()

    # 1. 获取上海市场交易日列表（近三年）
    trading_days_sh = demo_get_trading_dates("SH", START_DATE, END_DATE)

    # 2. 常见应用场景
    if trading_days_sh:
        demo_common_usages(trading_days_sh, market="SH")

    # 3. 使用 count 参数获取未来 10 个交易日
    demo_count_parameter()

    # 4. 对比多个市场日历（最近一年）
    start_of_year = f"{datetime.now().year}0101"
    compare_market_calendars(MARKETS, start_of_year, END_DATE)

    # 5. 保存上海市场结果
    if trading_days_sh:
        save_trading_days(trading_days_sh, market="SH")

    print("提示：")
    print("  1. get_trading_dates() 可获取指定区间或指定数量的交易日列表。")
    print("  2. 不同市场（SH/SZ/BJ）的交易日历基本一致，但可能存在细微差异。")
    print("  3. 若 get_trading_dates 报 'function not realize'，说明当前 QMT 客户端/账号不支持该接口，")
    print("     可尝试更新客户端版本或联系券商开通投研版权限。")


if __name__ == "__main__":
    main()
