import pytest
from calculations import (
    calculate_amortization_schedule,
    calculate_monthly_property_tax,
    calculate_upfront_cash,
    calculate_investment_portfolio,
    get_special_assessment_for_month,
    calculate_exit_sell,
    calculate_exit_rent_out,
    calculate_exit_continue_renting,
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


def test_pmi_applies_initially_at_20pct_down():
    # 20% down: initial balance $240K > $234K threshold → PMI applies month 1
    record = calculate_amortization_schedule(300_000, 20, 6.5)[0]
    assert record["pmi"] > 0


def test_pmi_cancelled_by_month_60_at_20pct_down():
    # 20% down: PMI should cancel around month 27
    record = calculate_amortization_schedule(300_000, 20, 6.5)[-1]
    assert record["pmi"] == 0.0


def test_pmi_cancels_around_month_27_at_20pct_down():
    schedule = calculate_amortization_schedule(300_000, 20, 6.5)
    cancel_month = next(r["month"] for r in schedule if r["pmi"] == 0.0)
    # Tolerance: allow month 24–32 (formula precision variation)
    assert 24 <= cancel_month <= 32


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


# ── get_special_assessment_for_month (Story 1.5) ─────────────────────────────

def test_special_assessment_returns_amount_on_correct_month():
    result = get_special_assessment_for_month(5_000, 12, 12)
    assert result == 5_000.0


def test_special_assessment_returns_zero_before_month():
    result = get_special_assessment_for_month(5_000, 12, 11)
    assert result == 0.0


def test_special_assessment_returns_zero_after_month():
    result = get_special_assessment_for_month(5_000, 12, 13)
    assert result == 0.0


def test_special_assessment_zero_amount_always_zero():
    assert get_special_assessment_for_month(0, 12, 12) == 0.0
    assert get_special_assessment_for_month(0, 1, 1) == 0.0


def test_special_assessment_first_month():
    result = get_special_assessment_for_month(10_000, 1, 1)
    assert result == 10_000.0


def test_special_assessment_last_month():
    result = get_special_assessment_for_month(7_500, 60, 60)
    assert result == 7_500.0


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
