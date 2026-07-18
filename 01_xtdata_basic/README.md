# xtdata 行情数据示例

本目录包含 `xtquant.xtdata` 行情接口的入门示例，覆盖 A 股股票、可转债、ETF 三类资产的日 K 线、分钟 K 线、实时行情订阅，以及复权因子相关内容。

## 文件说明

| 文件 | 内容 |
|------|------|
| `01_historical_data.py` | 历史行情数据下载：日 K 线、分钟 K 线，股票 / 可转债 / ETF |
| `02_realtime_data.py` | 实时行情订阅：tick / 分钟线回调示例 |
| `03_dividend_factors.py` | 复权因子：get_divid_factors、复权价格计算、收益率对比 |
| `04_dividend_types.py` | 不同复权方式对比：none/front/back/front_ratio/back_ratio |
| `05_financial_data.py` | 财务数据：get_financial_data 资产负债表 / 利润表 / 现金流量表 |
| `06_calendar_data.py` | 交易日历：get_trading_dates |

## 运行前准备

1. **安装 xtquant**
   - 如果你使用的是 QMT 内置的 Python 环境，通常已经集成 `xtquant`。
   - 如果在外部 Python 环境使用，需先安装：
     ```bash
     pip install xtquant
     ```

2. **启动 QMT 终端并登录**
   - `xtdata` 需要连接 QMT/迅投终端才能获取数据。
   - 未登录时调用接口可能会返回空数据或报错。

3. **首次运行会下载数据到本地缓存**
   - 下载速度取决于网络和数据量，请耐心等待。
   - 下载完成后，再次读取会很快。

## 运行方式

```bash
python 01_xtdata_basic/01_historical_data.py
python 01_xtdata_basic/02_realtime_data.py
python 01_xtdata_basic/03_dividend_factors.py
python 01_xtdata_basic/04_dividend_types.py
python 01_xtdata_basic/05_financial_data.py
python 01_xtdata_basic/06_calendar_data.py
```

> 注意：运行 `03_dividend_factors.py` 前，请确认你的 xtquant 版本支持 `get_divid_factors` 接口。如果不支持，脚本会跳过手动计算部分，仅展示 `get_market_data` 自带的前复权/后复权结果。

## 代码规则说明

- 股票：`000001.SZ`（深圳）、`600000.SH`（上海）
- 可转债：`128136.SZ`（深圳）、`113XXX.SH`（上海）
- ETF：`510050.SH`（上海）、`159915.SZ`（深圳）

> 提示：示例中的可转债代码 `128136.SZ` 仅作格式参考，实际使用前请替换为你当前能交易的品种代码。

## 常用 `period` 参数

| period | 含义 |
|--------|------|
| `tick` | 逐笔 tick |
| `1m`   | 1 分钟 K 线 |
| `5m`   | 5 分钟 K 线 |
| `1d`   | 日 K 线 |

## 复权方式详解

### 等比前复权（front_ratio）

**公式**：`close_front_ratio = close * (cum_factor / latest_cum_factor)`

- `close`：不复权的原始收盘价
- `cum_factor`：从上市以来所有除权日的 `dr` 连乘累积因子
- `latest_cum_factor`：最新交易日的累积因子

**效果**：以最新价为基准，历史价格被压低，保持收益率一致。

**示例**：

| 交易日 | dr | cum_factor | 原始价格 | 等比前复权价格 |
|--------|-----|------------|----------|----------------|
| 上市首日 | - | 1.0 | 10.00 | 10.00 * 1.0 / 1.32 = **7.58** |
| 第 1 次除权后 | 1.1 | 1.1 | 9.50 | 9.50 * 1.1 / 1.32 = **7.92** |
| 第 2 次除权后 | 1.2 | 1.32 | 9.00 | 9.00 * 1.32 / 1.32 = **9.00** |
| 最新交易日 | - | 1.32 | 12.00 | 12.00 * 1.32 / 1.32 = **12.00** |

**用途**：技术分析、策略回测、当前视角下的价格走势分析。

### 等比后复权（back_ratio）

**公式**：`close_back_ratio = close * cum_factor`

- `close`：不复权的原始收盘价
- `cum_factor`：从上市以来所有除权日的 `dr` 连乘累积因子

**效果**：以历史发行价为基准，价格越来越高，反映"如果一直持有并分红再投资，现在的价值"。

**示例**：

| 交易日 | dr | cum_factor | 原始价格 | 等比后复权价格 |
|--------|-----|------------|----------|----------------|
| 上市首日 | - | 1.0 | 10.00 | 10.00 * 1.0 = **10.00** |
| 第 1 次除权后 | 1.1 | 1.1 | 9.50 | 9.50 * 1.1 = **10.45** |
| 第 2 次除权后 | 1.2 | 1.32 | 9.00 | 9.00 * 1.32 = **11.88** |

**用途**：计算长期真实收益率、评估分红再投资价值。

### 前复权 vs 后复权对比

| 复权方式 | 公式 | 基准 | 最新价格 | 历史价格 |
|---------|------|------|----------|----------|
| 等比前复权 | `close * cum_factor / latest_cum_factor` | 最新价 | 等于原始价 | 被压低 |
| 等比后复权 | `close * cum_factor` | 历史发行价 | 被放大 | 越来越高 |

### 前复权与后复权（加减法）

除了等比复权，QMT 还支持加减法复权（`front` / `back`），它用加减法调整价格，保持价格连续性。

#### 后复权单日调整公式（`calc_backward_price`）

```
后复权价格 = 前一日价格 * (1 + 送股率 + 转增股率 + 配股率)
             + 每股派息 - 配股率 * 配股价
```

**字段含义**：

| 字段 | 含义 |
|------|------|
| `stockGift` | 送股比例（利润送股）|
| `stockBonus` | 转增股比例（公积金转增）|
| `allotNum` | 配股比例 |
| `allotPrice` | 配股价格 |
| `interest` | 每股派息（现金分红）|

**示例**：

假设前一日价格 `v = 10.00` 元，除权日数据：
- `interest = 0.50`（每股派息 0.5 元）
- `stockGift = 0.1`（10 送 1）
- `stockBonus = 0.05`（10 转 0.5）
- `allotNum = 0.0`（无配股）
- `allotPrice = 0.0`

```
后复权价格 = 10.00 * (1 + 0.1 + 0.05 + 0.0) + 0.50 - 0.0 * 0.0
           = 10.00 * 1.15 + 0.50
           = 12.00
```

**含义**：除权前 1 股价值 10 元，除权后 1.15 股 + 0.5 元现金，总价值 12 元。

#### 前复权单日调整公式（`calc_forward_price`）

```
前复权价格 = (原始价格 - 每股派息 + 配股价 * 配股率)
             / (1 + 配股率 + 转增股率 + 送股率)
```

**示例**：

假设原始价格 `v = 10.00` 元，除权日数据同上：

```
前复权价格 = (10.00 - 0.50 + 0.0 * 0.0) / (1 + 0.0 + 0.05 + 0.1)
           = 9.50 / 1.15
           ≈ 8.26
```

**含义**：以最新价为基准，把历史价格"还原"到除权前的等价水平。除权后 10 元的股票，相当于除权前 8.26 元。

#### 前复权 vs 后复权（加减法）对比

| 复权方式 | 公式 | 基准 | 效果 |
|---------|------|------|------|
| 前复权 | `(v - interest + allotPrice*allotNum) / (1 + allotNum + stockBonus + stockGift)` | 最新价 | 历史价格被压低 |
| 后复权 | `v * (1 + stockGift + stockBonus + allotNum) + interest - allotNum*allotPrice` | 历史价 | 未来价格被放大 |

## 财务报表字段说明

`xtdata.get_financial_data(stock_list, table_list, start_time, end_time, report_type)` 支持的 `table_list` 取值如下：

| table_list 值 | 中文名称 | 说明 |
|---------------|----------|------|
| `Balance` | 资产负债表 | 反映企业特定日期财务状况 |
| `Income` | 利润表 | 反映企业一定期间经营成果 |
| `CashFlow` | 现金流量表 | 反映企业现金流入流出情况 |
| `Capital` | 股本表 | 股本结构信息 |
| `Holdernum` | 股东数 | 股东户数统计 |
| `Top10holder` | 十大股东 | 前十大股东明细 |
| `Top10flowholder` | 十大流通股东 | 前十大流通股东明细 |
| `Pershareindex` | 每股指标 | 每股财务指标及主要比率 |

> 说明：以下字段列表参考 `05_financial_data.py` 中 `FIELD_NAME_MAP` 的映射，不同 QMT 版本和不同行业（如银行、保险、券商）实际返回的字段会有差异，请以实际输出为准。每个报表通常还会包含两个通用字段：`m_anntime`（披露日期）和 `m_timetag`（截止日期）。

### 通用字段

| 字段名 | 说明 |
|--------|------|
| `m_anntime` | 披露日期 |
| `m_timetag` | 截止日期 |

### Balance（资产负债表）

| 字段名 | 说明 |
|--------|------|
| `cash_equivalents` | 货币资金 |
| `loans_to_oth_banks` | 拆出资金 |
| `tradable_fin_assets` | 交易性金融资产 |
| `derivative_fin_assets` | 衍生金融资产 |
| `bill_receivable` | 应收票据 |
| `account_receivable` | 应收账款 |
| `advance_payment` | 预付款项 |
| `int_rcv` | 应收利息 |
| `dividends_payable` | 应收股利 |
| `other_receivable` | 其他应收款 |
| `red_monetary_cap_for_sale` | 买入返售金融资产 |
| `agency_bus_assets` | 以公允价值计量且其变动计入当期损益的金融资产 |
| `inventories` | 存货 |
| `other_current_assets` | 其他流动资产 |
| `total_current_assets` | 流动资产合计 |
| `loans_and_adv_granted` | 发放贷款及垫款 |
| `fin_assets_avail_for_sale` | 可供出售金融资产 |
| `held_to_mty_invest` | 持有至到期投资 |
| `long_term_eqy_invest` | 长期股权投资 |
| `invest_real_estate` | 投资性房地产 |
| `accumulated_depreciation` | 累计折旧 |
| `fix_assets` | 固定资产 |
| `constru_in_process` | 在建工程 |
| `construction_materials` | 工程物资 |
| `long_term_receivables` | 长期应收款 |
| `intang_assets` | 无形资产 |
| `goodwill` | 商誉 |
| `long_deferred_expense` | 长期待摊费用 |
| `deferred_tax_assets` | 递延所得税资产 |
| `total_non_current_assets` | 非流动资产合计 |
| `tot_assets` | 资产总计 |
| `shortterm_loan` | 短期借款 |
| `borrow_central_bank` | 向中央银行借款 |
| `loans_oth_banks` | 拆入资金 |
| `tradable_fin_liab` | 交易性金融负债 |
| `derivative_fin_liab` | 衍生金融负债 |
| `notes_payable` | 应付票据 |
| `accounts_payable` | 应付账款 |
| `advance_peceipts` | 预收账款 |
| `fund_sales_fin_assets_rp` | 卖出回购金融资产款 |
| `empl_ben_payable` | 应付职工薪酬 |
| `taxes_surcharges_payable` | 应交税费 |
| `int_payable` | 应付利息 |
| `dividend_payable` | 应付股利 |
| `other_payable` | 其他应付款 |
| `non_current_liability_in_one_year` | 一年内到期的非流动负债 |
| `other_current_liability` | 其他流动负债 |
| `total_current_liability` | 流动负债合计 |
| `long_term_loans` | 长期借款 |
| `bonds_payable` | 应付债券 |
| `longterm_account_payable` | 长期应付款 |
| `grants_received` | 专项应付款 |
| `deferred_tax_liab` | 递延所得税负债 |
| `other_non_current_liabilities` | 其他非流动负债 |
| `non_current_liabilities` | 非流动负债合计 |
| `tot_liab` | 负债合计 |
| `cap_stk` | 实收资本(或股本) |
| `cap_rsrv` | 资本公积 |
| `specific_reserves` | 专项储备 |
| `surplus_rsrv` | 盈余公积 |
| `prov_nom_risks` | 一般风险准备 |
| `undistributed_profit` | 未分配利润 |
| `cnvd_diff_foreign_curr_stat` | 外币报表折算差额 |
| `tot_shrhldr_eqy_excl_min_int` | 归属于母公司股东权益合计 |
| `minority_int` | 少数股东权益 |
| `total_equity` | 所有者权益合计 |
| `tot_liab_shrhldr_eqy` | 负债和股东权益总计 |
| `less_tsy_stk` | 减:库存股 |
| `provisions` | 预计流动负债 |
| `cust_bank_dep` | 吸收存款及同业存放 |

### Income（利润表）

| 字段名 | 说明 |
|--------|------|
| `revenue_inc` | 营业收入 |
| `earned_premium` | 已赚保费 |
| `real_estate_sales_income` | 房地产销售收入 |
| `total_operating_cost` | 营业总成本 |
| `real_estate_sales_cost` | 房地产销售成本 |
| `research_expenses` | 研发费用 |
| `surrender_value` | 退保金 |
| `net_payments` | 赔付支出净额 |
| `net_withdrawal_ins_con_res` | 提取保险合同准备金净额 |
| `policy_dividend_expenses` | 保单红利支出 |
| `reinsurance_cost` | 分保费用 |
| `change_income_fair_value` | 公允价值变动收益 |
| `futures_loss` | 期货损益 |
| `trust_income` | 托管收益 |
| `subsidize_revenue` | 补贴收入 |
| `other_business_profits` | 其他业务利润 |
| `net_profit_excl_merged_int_inc` | 被合并方在合并前实现净利润 |
| `int_inc` | 利息收入 |
| `handling_chrg_comm_inc` | 手续费及佣金收入 |
| `less_handling_chrg_comm_exp` | 手续费及佣金支出 |
| `other_bus_cost` | 其他业务成本 |
| `plus_net_gain_fx_trans` | 汇兑收益 |
| `il_net_loss_disp_noncur_asset` | 非流动资产处置收益 |
| `inc_tax` | 所得税费用 |
| `unconfirmed_invest_loss` | 未确认投资损失 |
| `net_profit_excl_min_int_inc` | 归属于母公司所有者的净利润 |
| `less_int_exp` | 利息支出 |
| `other_bus_inc` | 其他业务收入 |
| `revenue` | 营业总收入 |
| `total_expense` | 营业成本 |
| `less_taxes_surcharges_ops` | 营业税金及附加 |
| `sale_expense` | 销售费用 |
| `less_gerl_admin_exp` | 管理费用 |
| `financial_expense` | 财务费用 |
| `less_impair_loss_assets` | 资产减值损失 |
| `plus_net_invest_inc` | 投资收益 |
| `incl_inc_invest_assoc_jv_entp` | 联营企业和合营企业的投资收益 |
| `oper_profit` | 营业利润 |
| `plus_non_oper_rev` | 营业外收入 |
| `less_non_oper_exp` | 营业外支出 |
| `tot_profit` | 利润总额 |
| `net_profit_incl_min_int_inc` | 净利润 |
| `net_profit_incl_min_int_inc_after` | 净利润(扣除非经常性损益后) |
| `minority_int_inc` | 少数股东损益 |
| `s_fa_eps_basic` | 基本每股收益 |
| `s_fa_eps_diluted` | 稀释每股收益 |
| `total_income` | 综合收益总额 |
| `total_income_minority` | 归属于少数股东的综合收益总额 |
| `other_compreh_inc` | 其他收益 |

### CashFlow（现金流量表）

| 字段名 | 说明 |
|--------|------|
| `cash_received_ori_ins_contract_pre` | 收到原保险合同保费取得的现金 |
| `net_cash_received_rei_ope` | 收到再保险业务现金净额 |
| `net_increase_insured_funds` | 保户储金及投资款净增加额 |
| `Net` | 处置交易性金融资产净增加额 |
| `cash_for_interest` | 收取利息、手续费及佣金的现金 |
| `net_increase_in_repurchase_funds` | 回购业务资金净增加额 |
| `cash_for_payment_original_insurance` | 支付原保险合同赔付款项的现金 |
| `cash_payment_policy_dividends` | 支付保单红利的现金 |
| `disposal_other_business_units` | 处置子公司及其他收到的现金 |
| `cash_received_from_pledges` | 减少质押和定期存款所收到的现金 |
| `cash_paid_for_investments` | 投资所支付的现金 |
| `net_increase_in_pledged_loans` | 质押贷款净增加额 |
| `cash_paid_by_subsidiaries` | 取得子公司及其他营业单位支付的现金净额 |
| `increase_in_cash_paid` | 增加质押和定期存款所支付的现金 |
| `cass_received_sub_abs` | 其中子公司吸收现金 |
| `cass_received_sub_investments` | 其中:子公司支付给少数股东的股利、利润 |
| `minority_shareholder_profit_loss` | 少数股东损益 |
| `unrecognized_investment_losses` | 未确认的投资损失 |
| `ncrease_deferred_income` | 递延收益增加(减:减少) |
| `projected_liability` | 预计负债 |
| `increase_operational_payables` | 经营性应付项目的增加 |
| `reduction_outstanding_amounts_less` | 已完工尚未结算款的减少(减:增加) |
| `reduction_outstanding_amounts_more` | 已结算尚未完工款的增加(减:减少) |
| `goods_sale_and_service_render_cash` | 销售商品、提供劳务收到的现金 |
| `net_incr_dep_cob` | 客户存款和同业存放款项净增加额 |
| `net_incr_loans_central_bank` | 向中央银行借款净增加额 |
| `net_incr_fund_borr_ofi` | 向其他金融机构拆入资金净增加额 |
| `tax_levy_refund` | 收到的税费返还 |
| `cash_paid_invest` | 投资支付的现金 |
| `other_cash_recp_ral_oper_act` | 收到的其他与经营活动有关的现金 |
| `stot_cash_inflows_oper_act` | 经营活动现金流入小计 |
| `goods_and_services_cash_paid` | 购买商品、接受劳务支付的现金 |
| `net_incr_clients_loan_adv` | 客户贷款及垫款净增加额 |
| `net_incr_dep_cbob` | 存放中央银行和同业款项净增加额 |
| `handling_chrg_paid` | 支付利息、手续费及佣金的现金 |
| `cash_pay_beh_empl` | 支付给职工以及为职工支付的现金 |
| `pay_all_typ_tax` | 支付的各项税费 |
| `other_cash_pay_ral_oper_act` | 支付其他与经营活动有关的现金 |
| `stot_cash_outflows_oper_act` | 经营活动现金流出小计 |
| `net_cash_flows_oper_act` | 经营活动产生的现金流量净额 |
| `cash_recp_disp_withdrwl_invest` | 收回投资所收到的现金 |
| `cash_recp_return_invest` | 取得投资收益所收到的现金 |
| `net_cash_recp_disp_fiolta` | 处置固定资产、无形资产和其他长期投资收到的现金 |
| `other_cash_recp_ral_inv_act` | 收到的其他与投资活动有关的现金 |
| `stot_cash_inflows_inv_act` | 投资活动现金流入小计 |
| `cash_pay_acq_const_fiolta` | 购建固定资产、无形资产和其他长期投资支付的现金 |
| `stot_cash_outflows_inv_act` | 投资活动现金流出小计 |
| `net_cash_flows_inv_act` | 投资活动产生的现金流量净额 |
| `cash_recp_cap_contrib` | 吸收投资收到的现金 |
| `cash_recp_borrow` | 取得借款收到的现金 |
| `proc_issue_bonds` | 发行债券收到的现金 |
| `other_cash_recp_ral_fnc_act` | 收到其他与筹资活动有关的现金 |
| `stot_cash_inflows_fnc_act` | 筹资活动现金流入小计 |
| `cash_prepay_amt_borr` | 偿还债务支付现金 |
| `cash_pay_dist_dpcp_int_exp` | 分配股利、利润或偿付利息支付的现金 |
| `other_cash_pay_ral_fnc_act` | 支付其他与筹资的现金 |
| `stot_cash_outflows_fnc_act` | 筹资活动现金流出小计 |
| `net_cash_flows_fnc_act` | 筹资活动产生的现金流量净额 |
| `eff_fx_flu_cash` | 汇率变动对现金的影响 |
| `net_incr_cash_cash_equ` | 现金及现金等价物净增加额 |
| `cash_cash_equ_beg_period` | 期初现金及现金等价物余额 |
| `cash_cash_equ_end_period` | 期末现金及现金等价物余额 |
| `net_profit` | 净利润 |
| `plus_prov_depr_assets` | 资产减值准备 |
| `depr_fa_coga_dpba` | 固定资产折旧、油气资产折耗、生产性物资折旧 |
| `amort_intang_assets` | 无形资产摊销 |
| `amort_lt_deferred_exp` | 长期待摊费用摊销 |
| `decr_deferred_exp` | 待摊费用的减少 |
| `incr_acc_exp` | 预提费用的增加 |
| `loss_disp_fiolta` | 处置固定资产、无形资产和其他长期资产的损失 |
| `loss_scr_fa` | 固定资产报废损失 |
| `loss_fv_chg` | 公允价值变动损失 |
| `fin_exp` | 财务费用 |
| `invest_loss` | 投资损失 |
| `decr_deferred_inc_tax_assets` | 递延所得税资产减少 |
| `incr_deferred_inc_tax_liab` | 递延所得税负债增加 |
| `decr_inventories` | 存货的减少 |
| `decr_oper_payable` | 经营性应收项目的减少 |
| `others` | 其他 |
| `im_net_cash_flows_oper_act` | 经营活动产生现金流量净额 |
| `conv_debt_into_cap` | 债务转为资本 |
| `conv_corp_bonds_due_within_1y` | 一年内到期的可转换公司债券 |
| `fa_fnc_leases` | 融资租入固定资产 |
| `end_bal_cash` | 现金的期末余额 |
| `less_beg_bal_cash` | 现金的期初余额 |
| `plus_end_bal_cash_equ` | 现金等价物的期末余额 |
| `less_beg_bal_cash_equ` | 现金等价物的期初余额 |
| `im_net_incr_cash_cash_equ` | 现金及现金等价物的净增加额 |

### Pershareindex（每股指标）

| 字段名 | 说明 |
|--------|------|
| `s_fa_ocfps` | 每股经营活动现金流量 |
| `s_fa_bps` | 每股净资产 |
| `s_fa_eps_basic` | 基本每股收益 |
| `s_fa_eps_diluted` | 稀释每股收益 |
| `s_fa_undistributedps` | 每股未分配利润 |
| `s_fa_surpluscapitalps` | 每股资本公积金 |
| `adjusted_earnings_per_share` | 扣非每股收益 |
| `du_return_on_equity` | 净资产收益率 |
| `sales_gross_profit` | 销售毛利率 |
| `inc_revenue_rate` | 主营收入同比增长 |
| `du_profit_rate` | 净利润同比增长 |
| `inc_net_profit_rate` | 归属于母公司所有者的净利润同比增长 |
| `adjusted_net_profit_rate` | 扣非净利润同比增长 |
| `inc_total_revenue_annual` | 营业总收入滚动环比增长 |
| `inc_net_profit_to_shareholders_annual` | 归属净利润滚动环比增长 |
| `adjusted_profit_to_profit_annual` | 扣非净利润滚动环比增长 |
| `equity_roe` | 加权净资产收益率 |
| `net_roe` | 摊薄净资产收益率 |
| `total_roe` | 摊薄总资产收益率 |
| `gross_profit` | 毛利率 |
| `net_profit` | 净利率 |
| `actual_tax_rate` | 实际税率 |
| `pre_pay_operate_income` | 预收款 / 营业收入 |
| `sales_cash_flow` | 销售现金流 / 营业收入 |
| `gear_ratio` | 资产负债比率 |
| `inventory_turnover` | 存货周转率 |

### Capital（股本表）

| 字段名 | 说明 |
|--------|------|
| `total_capital` | 总股本 |
| `circulating_capital` | 已上市流通A股 |
| `restrict_circulating_capital` | 限售流通股份 |

### Holdernum（股东数）

| 字段名 | 说明 |
|--------|------|
| `shareholder` | 股东总数 |
| `shareholderA` | A股东户数 |
| `shareholderB` | B股东户数 |
| `shareholderH` | H股东户数 |
| `shareholderFloat` | 已流通股东户数 |
| `shareholderOther` | 未流通股东户数 |

### Top10holder / Top10flowholder（十大股东 / 十大流通股东）

| 字段名 | 说明 |
|--------|------|
| `declareDate` | 公告日期 |
| `endDate` | 截止日期 |
| `name` | 股东名称 |
| `type` | 股东类型 |
| `quantity` | 持股数量 |
| `reason` | 变动原因 |
| `ratio` | 持股比例 |
| `nature` | 股份性质 |
| `rank` | 持股排名 |

## 除权除息字段说明

`xtdata.get_divid_factors(stock_code)` 返回个股的除权除息数据，结果为 `DataFrame`，index 为除权日，常见字段如下：

| 字段名 | 说明 |
|--------|------|
| `interest` | 每股股利（税前，元） |
| `stockBonus` | 每股红股（股） |
| `stockGift` | 每股转增股本（股） |
| `allotNum` | 每股配股数（股） |
| `allotPrice` | 配股价格（元） |
| `gugai` | 是否股改，对于股改，在算复权系数时，系统有特殊算法 |
| `dr` | 除权系数 |

> 说明：复权计算时使用 `dr` 作为累积因子；加减法复权公式（`calc_forward_price` / `calc_backward_price`）会用到 `interest`、`stockGift`、`stockBonus`、`allotNum`、`allotPrice` 这 5 个字段。

## 下一步

行情数据跑通后，可以继续学习 `xttrader` 交易接口：

- 查询资金、持仓
- 下单、撤单
- 订阅成交回报

参见后续示例目录 `03_xttrader_basic/`。
