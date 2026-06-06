import pytest
from calculations import (
    calculate_amortization_schedule,
    calculate_monthly_property_tax,
    calculate_upfront_cash,
    calculate_investment_portfolio,
    calculate_exit_sell,
    calculate_exit_rent_out,
    calculate_exit_continue_renting,
    calculate_buyer_investment_portfolio,
    get_annual_snapshots,
    get_annual_averages,
    escalated_rent,
    annual_escalate,
    calculate_renter_investment_portfolio,
)


# ── Structure ────────────────────────────────────────────────────────────────

def test_returns_60_months():
    assert len(calculate_amortization_schedule(300_000, 5, 6.5)) == 60


def test_record_has_required_keys():
    record = calculate_amortization_schedule(300_000, 5, 6.5)[0]
    assert set(record.keys()) >= {"month", "principal", "interest", "balance", "pmi"}


def test_month_numbers_sequential():
    schedule = calculate_amortization_schedule(300_000, 5, 6.5)
    for i, record in enumerate(schedule):
        assert record["month"] == i + 1


def test_balance_strictly_decreasing():
    schedule = calculate_amortization_schedule(300_000, 10, 6.5)
    for i in range(1, len(schedule)):
        assert schedule[i]["balance"] < schedule[i - 1]["balance"]


# ── Financial Accuracy (NFR5: within $1/month of reference) ─────────────────

def test_month1_interest_5pct_down():
    # $285,000 loan * (6.5%/12) = $1,543.75
    record = calculate_amortization_schedule(300_000, 5, 6.5)[0]
    assert abs(record["interest"] - 1543.75) < 1.00


def test_month1_balance_5pct_down():
    # Reference: ~$284,742
    record = calculate_amortization_schedule(300_000, 5, 6.5)[0]
    assert abs(record["balance"] - 284_742) < 1.00


def test_month1_interest_20pct_down():
    # $240,000 loan * (6.5%/12) = $1,300.00
    record = calculate_amortization_schedule(300_000, 20, 6.5)[0]
    assert abs(record["interest"] - 1300.00) < 1.00


def test_principal_plus_interest_equals_payment():
    # P + I must equal the fixed monthly payment every month
    schedule = calculate_amortization_schedule(300_000, 10, 6.5)
    payment = schedule[0]["principal"] + schedule[0]["interest"]
    for record in schedule:
        assert abs((record["principal"] + record["interest"]) - payment) < 0.02


# ── PMI Logic (NFR6) ─────────────────────────────────────────────────────────

def test_pmi_applies_all_60_months_at_5pct_down():
    # 5% down: initial balance $285K, never reaches $234K (78% of $300K) in 5 years
    schedule = calculate_amortization_schedule(300_000, 5, 6.5)
    assert all(record["pmi"] > 0 for record in schedule)


def test_no_pmi_at_20pct_down_from_day_one():
    # HPA: 20% down = 80% LTV at origination → PMI never required
    record = calculate_amortization_schedule(300_000, 20, 6.5)[0]
    assert record["pmi"] == 0.0


def test_no_pmi_all_60_months_at_20pct_down():
    # 20% down: PMI is 0 for every month in the 5-year window
    schedule = calculate_amortization_schedule(300_000, 20, 6.5)
    assert all(record["pmi"] == 0.0 for record in schedule)


def test_pmi_applies_at_15pct_down():
    # 15% down = 85% LTV at origination > 80% threshold → PMI applies month 1
    record = calculate_amortization_schedule(300_000, 15, 6.5)[0]
    assert record["pmi"] > 0


def test_pmi_stays_cancelled_once_triggered():
    # Once PMI hits 0, it must remain 0 for all subsequent months
    schedule = calculate_amortization_schedule(300_000, 20, 6.5)
    pmi_values = [r["pmi"] for r in schedule]
    first_zero = next((i for i, v in enumerate(pmi_values) if v == 0), None)
    if first_zero is not None:
        assert all(v == 0 for v in pmi_values[first_zero:])


def test_no_pmi_at_20pct_down_after_loan_paid_past_threshold():
    # Sanity: final balance for 20% down must be well below 234K
    final = calculate_amortization_schedule(300_000, 20, 6.5)[-1]
    assert final["balance"] < 234_000


# ── calculate_monthly_property_tax (Story 1.4) ───────────────────────────────

def test_property_tax_month1_no_exemption():
    # $300K * 1.3% / 12 = $325.00
    result = calculate_monthly_property_tax(300_000, 1.3, 1)
    assert abs(result - 325.00) < 0.01


def test_property_tax_month12_no_exemption():
    # Month 12 is still year 1 — no exemption
    result = calculate_monthly_property_tax(300_000, 1.3, 12)
    assert abs(result - 325.00) < 0.01


def test_property_tax_month13_with_exemption():
    # ($300K - $50K) * 1.3% / 12 = $250K * 0.013 / 12 = $270.83
    result = calculate_monthly_property_tax(300_000, 1.3, 13)
    assert abs(result - 270.83) < 0.01


def test_property_tax_month60_with_exemption():
    # Month 60 still uses homestead
    result = calculate_monthly_property_tax(300_000, 1.3, 60)
    assert abs(result - 270.83) < 0.01


def test_property_tax_exemption_boundary():
    # Month 12 (no exemption) must be greater than month 13 (exemption)
    tax_year1 = calculate_monthly_property_tax(300_000, 1.3, 12)
    tax_year2 = calculate_monthly_property_tax(300_000, 1.3, 13)
    assert tax_year1 > tax_year2


def test_property_tax_zero_rate():
    # Edge case: zero tax rate → $0
    assert calculate_monthly_property_tax(300_000, 0, 1) == 0.0
    assert calculate_monthly_property_tax(300_000, 0, 13) == 0.0


# ── calculate_upfront_cash (Story 1.4) ───────────────────────────────────────

def test_upfront_cash_5pct_down():
    # 5% down: $15K + closing $10.5K + furniture $15K = $40,500
    result = calculate_upfront_cash(300_000, 5, 3.5, 15_000)
    assert abs(result - 40_500) < 0.01


def test_upfront_cash_10pct_down():
    # 10% down: $30K + $10.5K + $15K = $55,500
    result = calculate_upfront_cash(300_000, 10, 3.5, 15_000)
    assert abs(result - 55_500) < 0.01


def test_upfront_cash_20pct_down():
    # 20% down: $60K + $10.5K + $15K = $85,500
    result = calculate_upfront_cash(300_000, 20, 3.5, 15_000)
    assert abs(result - 85_500) < 0.01


def test_upfront_cash_components():
    # Verify formula: down + closing + furniture, all independent
    result = calculate_upfront_cash(400_000, 10, 2.0, 20_000)
    expected = 40_000 + 8_000 + 20_000  # = $68,000
    assert abs(result - expected) < 0.01


def test_upfront_cash_zero_furniture():
    result = calculate_upfront_cash(300_000, 20, 3.5, 0)
    assert abs(result - 70_500) < 0.01  # $60K down + $10.5K closing


# ── calculate_investment_portfolio (Story 1.5) ────────────────────────────────

def test_portfolio_returns_correct_length():
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    assert len(result) == 60


def test_portfolio_month1_formula():
    # (initial + contribution) * (1 + monthly_rate)
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    expected = (10_000 + 500) * (1 + 7 / 100 / 12)
    assert abs(result[0] - expected) < 0.01


def test_portfolio_month2_compounds_month1():
    # Month 2 must compound month 1 value, not initial_capital
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    expected_m2 = (result[0] + 500) * (1 + 7 / 100 / 12)
    assert abs(result[1] - expected_m2) < 0.01


def test_portfolio_zero_rate_flat_accumulation():
    # No growth: each month just adds contribution
    result = calculate_investment_portfolio(0, 1_000, 0, 60)
    assert abs(result[0] - 1_000) < 0.01
    assert abs(result[59] - 60_000) < 0.01


def test_portfolio_zero_contribution_compounds_only():
    # Only initial capital, no monthly savings: $10K at 12% annual → month 1 = $10,100
    result = calculate_investment_portfolio(10_000, 0, 12, 60)
    assert abs(result[0] - 10_100) < 0.01


def test_portfolio_grows_over_time():
    result = calculate_investment_portfolio(10_000, 500, 7, 60)
    assert result[59] > result[0]


def test_portfolio_monthly_not_annual_compounding():
    # At 12% annual, monthly compounding gives more than simple annual 12% growth
    result_monthly = calculate_investment_portfolio(10_000, 0, 12, 12)
    annual_simple = 10_000 * 1.12
    assert result_monthly[11] > annual_simple


def test_portfolio_custom_months_length():
    result = calculate_investment_portfolio(5_000, 200, 5, 12)
    assert len(result) == 12


# ── calculate_exit_sell (Story 1.6) ──────────────────────────────────────────

def test_exit_sell_zero_appreciation_zero_balance():
    # $300K, 0% appreciation, 3% realtor, $0 balance
    # realtor = 300_000 * 0.03 = 9,000; doc_stamp = 300_000 * 0.007 = 2,100
    # net = 300_000 - 9_000 - 2_100 - 0 = 288,900
    result = calculate_exit_sell(300_000, 0, 0, 3)
    assert abs(result - 288_900) < 1.00


def test_exit_sell_appreciation_increases_value():
    no_appreciation = calculate_exit_sell(300_000, 0, 0, 3)
    with_appreciation = calculate_exit_sell(300_000, 3, 0, 3)
    assert with_appreciation > no_appreciation


def test_exit_sell_reference_values():
    # $300K, 3% appreciation, 3% commission, $0 remaining balance
    # appreciated = 300_000 * (1.03)^5 = ~$347,782
    # realtor = 347_782 * 0.03 = ~$10,433; doc_stamp = 347_782 * 0.007 = ~$2,435
    # net = 347_782 - 10_433 - 2_435 - 0 = ~$334,914
    result = calculate_exit_sell(300_000, 3, 0, 3)
    assert abs(result - 334_914) < 1.00


def test_exit_sell_deducts_remaining_balance():
    low_balance = calculate_exit_sell(300_000, 3, 100_000, 3)
    high_balance = calculate_exit_sell(300_000, 3, 200_000, 3)
    assert low_balance > high_balance
    assert abs(low_balance - high_balance - 100_000) < 0.01


def test_exit_sell_can_be_negative():
    # Deeply underwater: balance exceeds appreciated value minus fees
    result = calculate_exit_sell(300_000, 0, 400_000, 3)
    assert result < 0


def test_exit_sell_doc_stamp_on_appreciated_value():
    # Zero fees except doc stamp: result = price - (price * 0.007)
    result = calculate_exit_sell(200_000, 0, 0, 0)
    expected = 200_000 - (200_000 * 0.007)
    assert abs(result - expected) < 0.01


# ── calculate_exit_rent_out (Story 1.6) ──────────────────────────────────────

def test_exit_rent_out_positive_cashflow():
    # income=2000, vac=5%, mgmt=10%, carrying=1000, appreciated=350000, balance=270000
    # effective=1900, net_income=1710, monthly_net=710, cumulative=42600
    # equity=80000, total=122600
    result = calculate_exit_rent_out(2_000, 5, 10, 1_000, 350_000, 270_000)
    assert abs(result - 122_600) < 1.00


def test_exit_rent_out_negative_cashflow_offset_by_equity():
    # income=2000, vac=0, mgmt=0, carrying=2500 → monthly_net=-500 → cumulative=-30000
    # equity=80000, total=50000
    result = calculate_exit_rent_out(2_000, 0, 0, 2_500, 350_000, 270_000)
    assert abs(result - 50_000) < 1.00


def test_exit_rent_out_zero_vacancy_zero_mgmt():
    # income=1000, no deductions, carrying=0, appreciated=200000, balance=150000
    # cumulative=60000, equity=50000, total=110000
    result = calculate_exit_rent_out(1_000, 0, 0, 0, 200_000, 150_000)
    assert abs(result - 110_000) < 1.00


def test_exit_rent_out_equity_only():
    # Zero income, zero costs → result equals equity alone
    result = calculate_exit_rent_out(0, 0, 0, 0, 300_000, 200_000)
    assert abs(result - 100_000) < 0.01


def test_exit_rent_out_vacancy_reduces_result():
    low_vacancy = calculate_exit_rent_out(2_000, 5, 0, 1_000, 300_000, 200_000)
    high_vacancy = calculate_exit_rent_out(2_000, 20, 0, 1_000, 300_000, 200_000)
    assert low_vacancy > high_vacancy


# ── calculate_exit_continue_renting (Story 1.6) ──────────────────────────────

def test_exit_continue_renting_returns_last_value():
    portfolio = [100 * i for i in range(1, 61)]  # [100, 200, ..., 6000]
    result = calculate_exit_continue_renting(portfolio)
    assert result == 6_000


def test_exit_continue_renting_integrates_with_portfolio():
    # Zero-rate portfolio: month 60 = initial + 60*contribution
    portfolio = calculate_investment_portfolio(0, 1_000, 0, 60)
    result = calculate_exit_continue_renting(portfolio)
    assert abs(result - 60_000) < 0.01


def test_exit_continue_renting_with_growth():
    portfolio = calculate_investment_portfolio(15_000, 0, 7, 60)
    result = calculate_exit_continue_renting(portfolio)
    assert result > 15_000


def test_exit_continue_renting_empty_portfolio_returns_zero():
    # Guard: empty list (e.g., months=0) returns 0.0 instead of IndexError
    assert calculate_exit_continue_renting([]) == 0.0


# ── Net-worth reconciliation (Story 1.6 AC5) ─────────────────────────────────

def test_exit_rent_out_reconciles_cashflow_plus_equity_ac5():
    # AC5: cumulative monthly cashflows + terminal equity = function return
    income, vac, mgmt, carrying, appreciated, balance = 2_000, 5, 10, 1_000, 350_000, 270_000
    result = calculate_exit_rent_out(income, vac, mgmt, carrying, appreciated, balance)
    effective_income = income * (1 - vac / 100)           # 1_900
    net_monthly = effective_income * (1 - mgmt / 100) - carrying  # 710
    expected = net_monthly * 60 + (appreciated - balance)  # 42_600 + 80_000
    assert abs(result - expected) < 0.01


# ── calculate_amortization_schedule months param (Story 1.8) ─────────────────

def test_amortization_default_still_60_months():
    # No-arg call: backward compatible default returns exactly 60 records
    result = calculate_amortization_schedule(300_000, 5, 6.5)
    assert len(result) == 60


def test_amortization_custom_months_120():
    # 10-year horizon: 120 months of data
    result = calculate_amortization_schedule(300_000, 10, 6.5, months=120)
    assert len(result) == 120


def test_amortization_custom_months_360():
    # Full 30-year schedule
    result = calculate_amortization_schedule(300_000, 20, 6.5, months=360)
    assert len(result) == 360


def test_amortization_custom_months_sequential():
    # Month numbers must run 1 .. N regardless of N
    result = calculate_amortization_schedule(300_000, 10, 6.5, months=120)
    for i, record in enumerate(result):
        assert record["month"] == i + 1


def test_amortization_360_months_balance_near_zero():
    # After 360 payments the loan should be essentially paid off
    result = calculate_amortization_schedule(300_000, 20, 6.5, months=360)
    final_balance = result[-1]["balance"]
    assert abs(final_balance) < 1.00  # within $1 of $0


def test_amortization_120_months_balance_less_than_60_months():
    # At month 120 more principal has been paid than at month 60
    balance_60 = calculate_amortization_schedule(300_000, 5, 6.5, months=60)[-1]["balance"]
    balance_120 = calculate_amortization_schedule(300_000, 5, 6.5, months=120)[-1]["balance"]
    assert balance_120 < balance_60


# ── calculate_buyer_investment_portfolio (Story 1.8) ─────────────────────────

def test_buyer_portfolio_returns_correct_length():
    surpluses = [100.0] * 60
    result = calculate_buyer_investment_portfolio(surpluses, 7.0)
    assert len(result) == 60


def test_buyer_portfolio_variable_length():
    surpluses = [200.0] * 120
    result = calculate_buyer_investment_portfolio(surpluses, 5.0)
    assert len(result) == 120


def test_buyer_portfolio_all_zero_surplus_zero_rate():
    # No surplus, no return → all zeros
    result = calculate_buyer_investment_portfolio([0.0] * 60, 0.0)
    assert all(v == 0.0 for v in result)


def test_buyer_portfolio_all_zero_surplus_with_rate():
    # Starting balance is $0; with no contributions nothing grows
    result = calculate_buyer_investment_portfolio([0.0] * 60, 7.0)
    assert all(abs(v) < 0.01 for v in result)


def test_buyer_portfolio_zero_rate_flat_accumulation():
    # At 0% return: each month simply adds the surplus
    surpluses = [1_000.0] * 60
    result = calculate_buyer_investment_portfolio(surpluses, 0.0)
    assert abs(result[0] - 1_000.0) < 0.01
    assert abs(result[59] - 60_000.0) < 0.01


def test_buyer_portfolio_matches_investment_portfolio_constant_surplus():
    # Constant surplus with compounding must match calculate_investment_portfolio(0, surplus, rate, months)
    surplus = 500.0
    rate = 7.0
    months = 60
    surpluses = [surplus] * months
    buyer_result = calculate_buyer_investment_portfolio(surpluses, rate)
    reference = calculate_investment_portfolio(0, surplus, rate, months)
    for i in range(months):
        assert abs(buyer_result[i] - reference[i]) < 0.01


def test_buyer_portfolio_month1_formula():
    # Month 1: (0 + surplus) * (1 + monthly_rate)
    surplus = 300.0
    annual_rate = 6.0
    monthly_rate = 6.0 / 100 / 12
    result = calculate_buyer_investment_portfolio([surplus], annual_rate)
    expected = (0 + surplus) * (1 + monthly_rate)
    assert abs(result[0] - expected) < 0.01


def test_buyer_portfolio_month2_compounds_month1():
    # Month 2 must compound month 1 balance
    surplus = 300.0
    annual_rate = 6.0
    monthly_rate = 6.0 / 100 / 12
    result = calculate_buyer_investment_portfolio([surplus, surplus], annual_rate)
    month1 = (0 + surplus) * (1 + monthly_rate)
    month2 = (month1 + surplus) * (1 + monthly_rate)
    assert abs(result[1] - month2) < 0.01


def test_buyer_portfolio_variable_surpluses():
    # Mix of zero and non-zero surpluses
    surpluses = [0.0, 200.0, 0.0, 300.0]
    rate = 12.0
    result = calculate_buyer_investment_portfolio(surpluses, rate)
    # m1: (0 + 0) * 1.01 = 0
    assert abs(result[0] - 0.0) < 0.01
    # m2: (0 + 200) * 1.01 = 202
    assert abs(result[1] - 202.0) < 0.01
    # m3: (202 + 0) * 1.01 = 204.02
    assert abs(result[2] - 204.02) < 0.01
    # m4: (204.02 + 300) * 1.01 = 504.02 * 1.01 ≈ 509.0602
    assert abs(result[3] - 509.0602) < 0.01


def test_buyer_portfolio_grows_with_positive_surpluses():
    surpluses = [500.0] * 60
    result = calculate_buyer_investment_portfolio(surpluses, 7.0)
    assert result[-1] > result[0]


# ── get_annual_snapshots (Story 1.8) ─────────────────────────────────────────

def test_annual_snapshots_60_months_returns_5_values():
    values = list(range(1, 61))
    result = get_annual_snapshots(values)
    assert len(result) == 5


def test_annual_snapshots_120_months_returns_10_values():
    values = list(range(1, 121))
    result = get_annual_snapshots(values)
    assert len(result) == 10


def test_annual_snapshots_360_months_returns_30_values():
    values = list(range(1, 361))
    result = get_annual_snapshots(values)
    assert len(result) == 30


def test_annual_snapshots_correct_indices():
    # Values [1, 2, ..., 60]: month 12 → value 12, month 24 → value 24, etc.
    values = list(range(1, 61))
    result = get_annual_snapshots(values)
    assert result[0] == 12   # month 12
    assert result[1] == 24   # month 24
    assert result[2] == 36   # month 36
    assert result[3] == 48   # month 48
    assert result[4] == 60   # month 60


def test_annual_snapshots_reflects_portfolio_year_ends():
    # Integration: get year-end values from a real portfolio
    portfolio = calculate_investment_portfolio(0, 1_000, 0, 60)  # zero-rate → $1K, $2K, ..., $60K
    snapshots = get_annual_snapshots(portfolio)
    assert len(snapshots) == 5
    assert abs(snapshots[0] - 12_000.0) < 0.01  # year 1 end
    assert abs(snapshots[4] - 60_000.0) < 0.01  # year 5 end


def test_annual_snapshots_partial_year_ignored():
    # 65 months: 5 complete years, 5 leftover months → still 5 snapshots
    values = list(range(1, 66))
    result = get_annual_snapshots(values)
    assert len(result) == 5


# ── get_annual_averages (monthly invested amount) ────────────────────────────

def test_annual_averages_60_months_returns_5_values():
    result = get_annual_averages(list(range(1, 61)))
    assert len(result) == 5


def test_annual_averages_correct_means():
    # Values [1..60]: year 1 = mean(1..12) = 6.5, year 2 = mean(13..24) = 18.5, ...
    result = get_annual_averages(list(range(1, 61)))
    assert result[0] == 6.5
    assert result[1] == 18.5
    assert result[4] == 54.5


def test_annual_averages_constant_contribution():
    # Constant $500/mo → every year's average is exactly $500
    result = get_annual_averages([500.0] * 36)
    assert result == [500.0, 500.0, 500.0]


def test_annual_averages_partial_year_ignored():
    # 65 months: 5 complete years, 5 leftover months → still 5 averages
    result = get_annual_averages(list(range(1, 66)))
    assert len(result) == 5


# ── escalated_rent ───────────────────────────────────────────────────────────

def test_escalated_rent_year_one_is_flat():
    # Months 1-12 (year 1) all equal the base rent — no increase yet
    for m in range(1, 13):
        assert escalated_rent(2_000.0, 3.0, m) == 2_000.0


def test_escalated_rent_year_two_step():
    # Month 13 starts year 2 → one annual increase applied
    assert abs(escalated_rent(2_000.0, 3.0, 13) - 2_060.0) < 0.001
    assert abs(escalated_rent(2_000.0, 3.0, 24) - 2_060.0) < 0.001  # still year 2


def test_escalated_rent_zero_growth_never_changes():
    assert escalated_rent(2_000.0, 0.0, 1) == 2_000.0
    assert escalated_rent(2_000.0, 0.0, 120) == 2_000.0


def test_escalated_rent_compounds_annually():
    # Year 3 (month 25) → base * 1.03^2
    assert abs(escalated_rent(2_000.0, 3.0, 25) - 2_000.0 * 1.03 ** 2) < 0.001


# ── annual_escalate (Story 4.1) ──────────────────────────────────────────────

def test_annual_escalate_year_one_is_flat():
    # Months 1-12 (year 1) all equal the base — no increase yet
    for m in range(1, 13):
        assert annual_escalate(3_500.0, 2.0, m) == 3_500.0


def test_annual_escalate_year_two_step():
    # Month 13 begins year 2 → one annual increase applied
    assert abs(annual_escalate(3_500.0, 2.0, 13) - 3_570.0) < 0.001
    assert abs(annual_escalate(3_500.0, 2.0, 24) - 3_570.0) < 0.001  # still year 2


def test_annual_escalate_zero_growth_never_changes():
    assert annual_escalate(3_500.0, 0.0, 1) == 3_500.0
    assert annual_escalate(3_500.0, 0.0, 240) == 3_500.0


def test_annual_escalate_compounds_annually():
    # Year 3 (month 25) → base * 1.0325^2
    assert abs(annual_escalate(3_500.0, 3.25, 25) - 3_500.0 * 1.0325 ** 2) < 0.001


def test_escalated_rent_matches_annual_escalate():
    # escalated_rent delegates to annual_escalate — identical results
    for m in (1, 12, 13, 25, 60):
        assert escalated_rent(2_000.0, 3.0, m) == annual_escalate(2_000.0, 3.0, m)


# ── property tax assessed-value growth + SOH cap (Story 4.1) ─────────────────

def test_property_tax_growth_default_arg_is_flat():
    # Back-compat: omitting assessment_growth_pct reproduces the old flat behavior
    flat = calculate_monthly_property_tax(300_000, 1.3, 13)
    grown_zero = calculate_monthly_property_tax(300_000, 1.3, 13, 0.0)
    assert flat == grown_zero


def test_property_tax_assessed_value_grows():
    # Year 2 (month 13): assessed value = (price grown 1 yr) − homestead, then × rate/12
    grown = 300_000 * 1.03
    expected = (grown - 50_000) * (1.3 / 100) / 12
    result = calculate_monthly_property_tax(300_000, 1.3, 13, 3.0)
    assert abs(result - expected) < 0.001


def test_property_tax_growth_capped_at_soh_3pct():
    # A cost-growth slider above 3% must still cap assessed-value growth at 3% (Save Our Homes)
    at_cap = calculate_monthly_property_tax(300_000, 1.3, 13, 3.0)
    above_cap = calculate_monthly_property_tax(300_000, 1.3, 13, 6.0)
    assert above_cap == at_cap


def test_property_tax_growth_year1_unaffected_no_exemption():
    # Year 1 (month 1): no growth applied yet (year 1 = base), no homestead exemption
    expected = 300_000 * (1.3 / 100) / 12
    assert abs(calculate_monthly_property_tax(300_000, 1.3, 1, 3.0) - expected) < 0.001


# ── calculate_renter_investment_portfolio (Story 4.1) ────────────────────────

def test_renter_portfolio_returns_correct_length():
    result = calculate_renter_investment_portfolio(10_000, [500.0] * 60, 7.0)
    assert len(result) == 60


def test_renter_portfolio_month1_formula():
    # month1 = (initial + contribution) * (1 + monthly_rate)
    result = calculate_renter_investment_portfolio(10_000, [500.0], 7.0)
    expected = (10_000 + 500.0) * (1 + 7.0 / 100 / 12)
    assert abs(result[0] - expected) < 0.001


def test_renter_portfolio_matches_investment_portfolio_constant_contribution():
    # Constant contribution must match the legacy fixed-contribution function
    months = 60
    ref = calculate_investment_portfolio(10_000, 500.0, 7.0, months)
    new = calculate_renter_investment_portfolio(10_000, [500.0] * months, 7.0)
    for a, b in zip(ref, new):
        assert abs(a - b) < 0.0001


def test_renter_portfolio_floor_zero_contribution_compounds_only():
    # A $0 contribution month (the floor) still compounds the existing balance
    result = calculate_renter_investment_portfolio(10_000, [0.0, 0.0], 12.0)
    r = 12.0 / 100 / 12
    assert abs(result[0] - 10_000 * (1 + r)) < 0.001
    assert abs(result[1] - 10_000 * (1 + r) ** 2) < 0.001
