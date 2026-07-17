# -*- coding: utf-8 -*-
"""
xtdata 财务数据示例

覆盖内容：
- 使用 get_financial_data 获取个股财务数据
- 支持同时查询多只股票、多张报表
- 常见的财务报表类型：资产负债表、利润表、现金流量表、财务指标
- 将财务数据保存到本地 CSV，方便查看

接口说明：
- xtdata.get_financial_data(stock_list, table_list, start_time, end_time, report_type='report_time')
- 返回：dict {stock_code: {table_name: DataFrame}}

常用 table_list：
- "Balance"          资产负债表
- "Income"           利润表
- "CashFlow"         现金流量表
- "Capital"          股本表
- "Holdernum"        股东数
- "Top10holder"      十大股东
- "Top10flowholder"  十大流通股东
- "Pershareindex"    每股指标

report_type 说明：
- "report_time"    按报告期（截止日期，默认值）
- "announce_time"  按披露日期

运行前提：QMT/迅投终端已启动并登录。
"""

import os
import pandas as pd
from xtquant import xtdata


# 财务字段中文映射（可根据需要扩展）
# 来源：xtquant 官方文档 / QMT 财务数据字段说明
FIELD_NAME_MAP = {
    # 通用字段
    "m_anntime": "披露日期",
    "m_timetag": "截止日期",

    # 资产负债表（Balance）常见字段
    "cash_equivalents": "货币资金",
    "loans_to_oth_banks": "拆出资金",
    "tradable_fin_assets": "交易性金融资产",
    "derivative_fin_assets": "衍生金融资产",
    "bill_receivable": "应收票据",
    "account_receivable": "应收账款",
    "advance_payment": "预付款项",
    "int_rcv": "应收利息",
    "dividends_payable": "应收股利",
    "other_receivable": "其他应收款",
    "red_monetary_cap_for_sale": "买入返售金融资产",
    "agency_bus_assets": "以公允价值计量且其变动计入当期损益的金融资产",
    "inventories": "存货",
    "other_current_assets": "其他流动资产",
    "total_current_assets": "流动资产合计",
    "loans_and_adv_granted": "发放贷款及垫款",
    "fin_assets_avail_for_sale": "可供出售金融资产",
    "held_to_mty_invest": "持有至到期投资",
    "long_term_eqy_invest": "长期股权投资",
    "invest_real_estate": "投资性房地产",
    "accumulated_depreciation": "累计折旧",
    "fix_assets": "固定资产",
    "constru_in_process": "在建工程",
    "construction_materials": "工程物资",
    "long_term_receivables": "长期应收款",
    "intang_assets": "无形资产",
    "goodwill": "商誉",
    "long_deferred_expense": "长期待摊费用",
    "deferred_tax_assets": "递延所得税资产",
    "total_non_current_assets": "非流动资产合计",
    "tot_assets": "资产总计",
    "shortterm_loan": "短期借款",
    "borrow_central_bank": "向中央银行借款",
    "loans_oth_banks": "拆入资金",
    "tradable_fin_liab": "交易性金融负债",
    "derivative_fin_liab": "衍生金融负债",
    "notes_payable": "应付票据",
    "accounts_payable": "应付账款",
    "advance_peceipts": "预收账款",
    "fund_sales_fin_assets_rp": "卖出回购金融资产款",
    "empl_ben_payable": "应付职工薪酬",
    "taxes_surcharges_payable": "应交税费",
    "int_payable": "应付利息",
    "dividend_payable": "应付股利",
    "other_payable": "其他应付款",
    "non_current_liability_in_one_year": "一年内到期的非流动负债",
    "other_current_liability": "其他流动负债",
    "total_current_liability": "流动负债合计",
    "long_term_loans": "长期借款",
    "bonds_payable": "应付债券",
    "longterm_account_payable": "长期应付款",
    "grants_received": "专项应付款",
    "deferred_tax_liab": "递延所得税负债",
    "other_non_current_liabilities": "其他非流动负债",
    "non_current_liabilities": "非流动负债合计",
    "tot_liab": "负债合计",
    "cap_stk": "实收资本(或股本)",
    "cap_rsrv": "资本公积",
    "specific_reserves": "专项储备",
    "surplus_rsrv": "盈余公积",
    "prov_nom_risks": "一般风险准备",
    "undistributed_profit": "未分配利润",
    "cnvd_diff_foreign_curr_stat": "外币报表折算差额",
    "tot_shrhldr_eqy_excl_min_int": "归属于母公司股东权益合计",
    "minority_int": "少数股东权益",
    "total_equity": "所有者权益合计",
    "tot_liab_shrhldr_eqy": "负债和股东权益总计",
    "less_tsy_stk": "减:库存股",
    "provisions": "预计流动负债",
    "cust_bank_dep": "吸收存款及同业存放",

    # 利润表（Income）常见字段
    "revenue_inc": "营业收入",
    "earned_premium": "已赚保费",
    "real_estate_sales_income": "房地产销售收入",
    "total_operating_cost": "营业总成本",
    "real_estate_sales_cost": "房地产销售成本",
    "research_expenses": "研发费用",
    "surrender_value": "退保金",
    "net_payments": "赔付支出净额",
    "net_withdrawal_ins_con_res": "提取保险合同准备金净额",
    "policy_dividend_expenses": "保单红利支出",
    "reinsurance_cost": "分保费用",
    "change_income_fair_value": "公允价值变动收益",
    "futures_loss": "期货损益",
    "trust_income": "托管收益",
    "subsidize_revenue": "补贴收入",
    "other_business_profits": "其他业务利润",
    "net_profit_excl_merged_int_inc": "被合并方在合并前实现净利润",
    "int_inc": "利息收入",
    "handling_chrg_comm_inc": "手续费及佣金收入",
    "less_handling_chrg_comm_exp": "手续费及佣金支出",
    "other_bus_cost": "其他业务成本",
    "plus_net_gain_fx_trans": "汇兑收益",
    "il_net_loss_disp_noncur_asset": "非流动资产处置收益",
    "inc_tax": "所得税费用",
    "unconfirmed_invest_loss": "未确认投资损失",
    "net_profit_excl_min_int_inc": "归属于母公司所有者的净利润",
    "less_int_exp": "利息支出",
    "other_bus_inc": "其他业务收入",
    "revenue": "营业总收入",
    "total_expense": "营业成本",
    "less_taxes_surcharges_ops": "营业税金及附加",
    "sale_expense": "销售费用",
    "less_gerl_admin_exp": "管理费用",
    "financial_expense": "财务费用",
    "less_impair_loss_assets": "资产减值损失",
    "plus_net_invest_inc": "投资收益",
    "incl_inc_invest_assoc_jv_entp": "联营企业和合营企业的投资收益",
    "oper_profit": "营业利润",
    "plus_non_oper_rev": "营业外收入",
    "less_non_oper_exp": "营业外支出",
    "tot_profit": "利润总额",
    "net_profit_incl_min_int_inc": "净利润",
    "net_profit_incl_min_int_inc_after": "净利润(扣除非经常性损益后)",
    "minority_int_inc": "少数股东损益",
    "s_fa_eps_basic": "基本每股收益",
    "s_fa_eps_diluted": "稀释每股收益",
    "total_income": "综合收益总额",
    "total_income_minority": "归属于少数股东的综合收益总额",
    "other_compreh_inc": "其他收益",

    # 现金流量表（CashFlow）常见字段
    "cash_received_ori_ins_contract_pre": "收到原保险合同保费取得的现金",
    "net_cash_received_rei_ope": "收到再保险业务现金净额",
    "net_increase_insured_funds": "保户储金及投资款净增加额",
    "Net": "处置交易性金融资产净增加额",
    "cash_for_interest": "收取利息、手续费及佣金的现金",
    "net_increase_in_repurchase_funds": "回购业务资金净增加额",
    "cash_for_payment_original_insurance": "支付原保险合同赔付款项的现金",
    "cash_payment_policy_dividends": "支付保单红利的现金",
    "disposal_other_business_units": "处置子公司及其他收到的现金",
    "cash_received_from_pledges": "减少质押和定期存款所收到的现金",
    "cash_paid_for_investments": "投资所支付的现金",
    "net_increase_in_pledged_loans": "质押贷款净增加额",
    "cash_paid_by_subsidiaries": "取得子公司及其他营业单位支付的现金净额",
    "increase_in_cash_paid": "增加质押和定期存款所支付的现金",
    "cass_received_sub_abs": "其中子公司吸收现金",
    "cass_received_sub_investments": "其中:子公司支付给少数股东的股利、利润",
    "minority_shareholder_profit_loss": "少数股东损益",
    "unrecognized_investment_losses": "未确认的投资损失",
    "ncrease_deferred_income": "递延收益增加(减:减少)",
    "projected_liability": "预计负债",
    "increase_operational_payables": "经营性应付项目的增加",
    "reduction_outstanding_amounts_less": "已完工尚未结算款的减少(减:增加)",
    "reduction_outstanding_amounts_more": "已结算尚未完工款的增加(减:减少)",
    "goods_sale_and_service_render_cash": "销售商品、提供劳务收到的现金",
    "net_incr_dep_cob": "客户存款和同业存放款项净增加额",
    "net_incr_loans_central_bank": "向中央银行借款净增加额",
    "net_incr_fund_borr_ofi": "向其他金融机构拆入资金净增加额",
    "tax_levy_refund": "收到的税费返还",
    "cash_paid_invest": "投资支付的现金",
    "other_cash_recp_ral_oper_act": "收到的其他与经营活动有关的现金",
    "stot_cash_inflows_oper_act": "经营活动现金流入小计",
    "goods_and_services_cash_paid": "购买商品、接受劳务支付的现金",
    "net_incr_clients_loan_adv": "客户贷款及垫款净增加额",
    "net_incr_dep_cbob": "存放中央银行和同业款项净增加额",
    "handling_chrg_paid": "支付利息、手续费及佣金的现金",
    "cash_pay_beh_empl": "支付给职工以及为职工支付的现金",
    "pay_all_typ_tax": "支付的各项税费",
    "other_cash_pay_ral_oper_act": "支付其他与经营活动有关的现金",
    "stot_cash_outflows_oper_act": "经营活动现金流出小计",
    "net_cash_flows_oper_act": "经营活动产生的现金流量净额",
    "cash_recp_disp_withdrwl_invest": "收回投资所收到的现金",
    "cash_recp_return_invest": "取得投资收益所收到的现金",
    "net_cash_recp_disp_fiolta": "处置固定资产、无形资产和其他长期投资收到的现金",
    "other_cash_recp_ral_inv_act": "收到的其他与投资活动有关的现金",
    "stot_cash_inflows_inv_act": "投资活动现金流入小计",
    "cash_pay_acq_const_fiolta": "购建固定资产、无形资产和其他长期投资支付的现金",
    "stot_cash_outflows_inv_act": "投资活动现金流出小计",
    "net_cash_flows_inv_act": "投资活动产生的现金流量净额",
    "cash_recp_cap_contrib": "吸收投资收到的现金",
    "cash_recp_borrow": "取得借款收到的现金",
    "proc_issue_bonds": "发行债券收到的现金",
    "other_cash_recp_ral_fnc_act": "收到其他与筹资活动有关的现金",
    "stot_cash_inflows_fnc_act": "筹资活动现金流入小计",
    "cash_prepay_amt_borr": "偿还债务支付现金",
    "cash_pay_dist_dpcp_int_exp": "分配股利、利润或偿付利息支付的现金",
    "other_cash_pay_ral_fnc_act": "支付其他与筹资的现金",
    "stot_cash_outflows_fnc_act": "筹资活动现金流出小计",
    "net_cash_flows_fnc_act": "筹资活动产生的现金流量净额",
    "eff_fx_flu_cash": "汇率变动对现金的影响",
    "net_incr_cash_cash_equ": "现金及现金等价物净增加额",
    "cash_cash_equ_beg_period": "期初现金及现金等价物余额",
    "cash_cash_equ_end_period": "期末现金及现金等价物余额",
    "net_profit": "净利润",
    "plus_prov_depr_assets": "资产减值准备",
    "depr_fa_coga_dpba": "固定资产折旧、油气资产折耗、生产性物资折旧",
    "amort_intang_assets": "无形资产摊销",
    "amort_lt_deferred_exp": "长期待摊费用摊销",
    "decr_deferred_exp": "待摊费用的减少",
    "incr_acc_exp": "预提费用的增加",
    "loss_disp_fiolta": "处置固定资产、无形资产和其他长期资产的损失",
    "loss_scr_fa": "固定资产报废损失",
    "loss_fv_chg": "公允价值变动损失",
    "fin_exp": "财务费用",
    "invest_loss": "投资损失",
    "decr_deferred_inc_tax_assets": "递延所得税资产减少",
    "incr_deferred_inc_tax_liab": "递延所得税负债增加",
    "decr_inventories": "存货的减少",
    "decr_oper_payable": "经营性应收项目的减少",
    "others": "其他",
    "im_net_cash_flows_oper_act": "经营活动产生现金流量净额",
    "conv_debt_into_cap": "债务转为资本",
    "conv_corp_bonds_due_within_1y": "一年内到期的可转换公司债券",
    "fa_fnc_leases": "融资租入固定资产",
    "end_bal_cash": "现金的期末余额",
    "less_beg_bal_cash": "现金的期初余额",
    "plus_end_bal_cash_equ": "现金等价物的期末余额",
    "less_beg_bal_cash_equ": "现金等价物的期初余额",
    "im_net_incr_cash_cash_equ": "现金及现金等价物的净增加额",

    # 主要指标（PershareIndex）常见字段
    "s_fa_ocfps": "每股经营活动现金流量",
    "s_fa_bps": "每股净资产",
    "s_fa_eps_basic": "基本每股收益",
    "s_fa_eps_diluted": "稀释每股收益",
    "s_fa_undistributedps": "每股未分配利润",
    "s_fa_surpluscapitalps": "每股资本公积金",
    "adjusted_earnings_per_share": "扣非每股收益",
    "du_return_on_equity": "净资产收益率",
    "sales_gross_profit": "销售毛利率",
    "inc_revenue_rate": "主营收入同比增长",
    "du_profit_rate": "净利润同比增长",
    "inc_net_profit_rate": "归属于母公司所有者的净利润同比增长",
    "adjusted_net_profit_rate": "扣非净利润同比增长",
    "inc_total_revenue_annual": "营业总收入滚动环比增长",
    "inc_net_profit_to_shareholders_annual": "归属净利润滚动环比增长",
    "adjusted_profit_to_profit_annual": "扣非净利润滚动环比增长",
    "equity_roe": "加权净资产收益率",
    "net_roe": "摊薄净资产收益率",
    "total_roe": "摊薄总资产收益率",
    "gross_profit": "毛利率",
    "net_profit": "净利率",
    "actual_tax_rate": "实际税率",
    "pre_pay_operate_income": "预收款 / 营业收入",
    "sales_cash_flow": "销售现金流 / 营业收入",
    "gear_ratio": "资产负债比率",
    "inventory_turnover": "存货周转率",

    # 股本表（CapitalStructure）常见字段
    "total_capital": "总股本",
    "circulating_capital": "已上市流通A股",
    "restrict_circulating_capital": "限售流通股份",

    # 十大股东 / 十大流通股东（Top10holder / Top10flowholder）常见字段
    "declareDate": "公告日期",
    "endDate": "截止日期",
    "name": "股东名称",
    "type": "股东类型",
    "quantity": "持股数量",
    "reason": "变动原因",
    "ratio": "持股比例",
    "nature": "股份性质",
    "rank": "持股排名",

    # 股东数（Holdernum）常见字段
    "shareholder": "股东总数",
    "shareholderA": "A股东户数",
    "shareholderB": "B股东户数",
    "shareholderH": "H股东户数",
    "shareholderFloat": "已流通股东户数",
    "shareholderOther": "未流通股东户数",
}


def get_output_dir():
    """获取当前文件所在目录下的 outputs 目录。"""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_financial_data_demo(stock_list, table_list, start_time, end_time, report_type="report_time"):
    """
    获取指定股票的财务数据。

    参数：
        stock_list: 股票代码列表，如 ["000001.SZ", "600000.SH"]
        table_list: 财务报表类型列表，如 ["balance_sheet", "income_statement"]
        start_time: 开始时间，如 "20230101"
        end_time: 结束时间，如 "20231231"
        report_type: 报告期类型，默认 "report_time"

    返回值：
        dict: {stock_code: {table_name: DataFrame}}
    """
    print("=" * 60)
    print("示例：获取财务数据")
    print(f"股票列表：{stock_list}")
    print(f"报表列表：{table_list}")
    print(f"时间范围：{start_time} ~ {end_time}")
    print(f"报告期类型：{report_type}")
    print("=" * 60)

    # 先下载财务数据到本地缓存（部分 QMT 版本需要）
    if hasattr(xtdata, "download_financial_data2"):
        try:
            print("  正在下载财务数据到本地缓存...")
            xtdata.download_financial_data2(stock_list, table_list, start_time, end_time)
            print("  下载完成。")
        except Exception as e:
            print(f"  download_financial_data2 调用提示：{e}")
    else:
        print("  当前 QMT 版本没有 download_financial_data2，跳过下载步骤。")
    print()

    try:
        data = xtdata.get_financial_data(stock_list, table_list, start_time, end_time, report_type)
    except Exception as e:
        print(f"  get_financial_data 调用失败：{e}")
        print("  提示：请确认当前 QMT 版本支持该接口，以及参数是否正确。")
        return {}

    if not data:
        print("  未获取到数据，请检查股票代码、报表类型和时间范围。")
        return {}

    print(f"  获取到数据：{len(data)} 只股票")
    for stock_code, tables in data.items():
        print(f"    {stock_code}: {list(tables.keys())}")
    print()

    return data


def format_dataframe_for_display(df, max_rows=5, max_col_width=20):
    """
    将 DataFrame 格式化为终端友好的字符串。

    - 限制显示行数
    - 限制每列宽度，避免终端换行
    - 显示所有列，但用省略号截断过宽内容
    """
    with pd.option_context(
        "display.max_rows", max_rows,
        "display.max_columns", None,
        "display.width", 120,
        "display.max_colwidth", max_col_width,
        "display.float_format", "{:.2f}".format,
    ):
        return df.head(max_rows).to_string()


def display_latest_report(stock_code, table_name, df):
    """
    展示最新一期的财务数据摘要。

    参数：
        stock_code: 股票代码
        table_name: 报表名称
        df: 财务数据 DataFrame
    """
    if df.empty:
        return

    # 通常第一列或最后一列为报告期，这里取最后一行作为最新报告期
    latest = df.iloc[-1].copy()
    report_date = latest.get("m_timetag", latest.get("report_time", latest.get("公告日", "未知")))

    # 报表中文名
    table_name_cn = {
        "Balance": "资产负债表",
        "Income": "利润表",
        "CashFlow": "现金流量表",
        "Capital": "股本表",
        "CapitalStructure": "股本结构",
        "Holdernum": "股东数",
        "Top10holder": "十大股东",
        "Top10flowholder": "十大流通股东",
        "Pershareindex": "每股指标",
    }.get(table_name, table_name)

    print(f"  📊 {stock_code} - {table_name_cn}（最新报告期：{report_date}）")
    print(f"     报告期数量：{len(df)}，字段数量：{len(df.columns)}")
    print()

    # 展示最新一期的关键字段（最多 10 个），优先显示有中文映射的字段
    display_cols = list(df.columns)[:10]
    print("     最新一期关键字段：")
    for col in display_cols:
        value = latest[col]
        cn_name = FIELD_NAME_MAP.get(col, col)
        # 数值型格式化为 2 位小数，其他原样输出
        if isinstance(value, (int, float)):
            value_str = f"{value:,.2f}"
        else:
            value_str = str(value)
        print(f"       {col:30s} | {cn_name:30s} : {value_str}")
    print()

    if len(df.columns) > 10:
        print(f"     ... 还有 {len(df.columns) - 10} 个字段，详见 CSV 文件")
        print()


def analyze_and_save(data, stock_list, table_list):
    """
    解析返回的财务数据并保存到 CSV。

    参数：
        data: get_financial_data 返回的 dict
        stock_list: 股票代码列表
        table_list: 报表类型列表
    """
    if not data:
        return

    saved_files = []

    for stock_code in stock_list:
        if stock_code not in data:
            print(f"⚠️  未获取到 {stock_code} 的数据，跳过。")
            continue

        print("=" * 60)
        print(f"股票：{stock_code}")
        print("=" * 60)

        for table_name in table_list:
            if table_name not in data[stock_code]:
                print(f"⚠️  未获取到 {stock_code} 的 {table_name} 数据，跳过。")
                continue

            df = data[stock_code][table_name]

            # 1. 展示最新一期摘要
            display_latest_report(stock_code, table_name, df)

            # 2. 展示前 5 行（截断显示）
            print("  前 5 行预览：")
            print(format_dataframe_for_display(df, max_rows=5))
            print()

            # 3. 保存到 CSV
            filename = os.path.join(
                get_output_dir(),
                f"financial_{table_name}_{stock_code.replace('.', '_')}.csv"
            )
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            saved_files.append(filename)

    print("=" * 60)
    print("已保存的 CSV 文件")
    print("=" * 60)
    for f in saved_files:
        print(f"  {f}")
    print()


def main():
    # 示例股票：平安银行、浦发银行
    stock_list = ["000001.SZ", "600000.SH"]

    # 财务报表类型
    table_list = [
        "Balance",           # 资产负债表
        "Income",            # 利润表
        "CashFlow",          # 现金流量表
        "Pershareindex",     # 每股指标
        "CapitalStructure",  # 股本结构
    ]

    # 时间范围：最近一年
    start_time = "20230101"
    end_time = "20231231"

    print("=" * 60)
    print("xtdata 财务数据示例")
    print("=" * 60)
    print()

    # 1. 获取财务数据
    data = get_financial_data_demo(stock_list, table_list, start_time, end_time)

    # 2. 解析并保存
    analyze_and_save(data, stock_list, table_list)

    print("提示：")
    print("  1. get_financial_data 返回结构为 {stock: {table: DataFrame}}。")
    print("  2. 不同 QMT 版本支持的 table_list 和 report_type 可能有差异。")
    print("  3. 如果返回空，请确认股票代码、报表类型和时间范围是否正确。")
    print("  4. 部分 QMT 版本需要先调用 download_financial_data2 下载财务数据到本地缓存。")


if __name__ == "__main__":
    main()
