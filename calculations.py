"""
Financial calculation engine for the Miami Home Buying Decision Tool.

Pure Python only — no Streamlit imports. This module is independently
unit-testable against a reference spreadsheet.
"""

PMI_ANNUAL_RATE = 0.008  # 0.8% of original loan amount per year


def calculate_amortization_schedule(price, down_pct, annual_rate):
    """Returns list of 60 monthly records: month, principal, interest, balance, pmi."""
    loan = price * (1 - down_pct / 100)
    r = annual_rate / 100 / 12
    n = 360  # 30-year mortgage

    if r == 0:
        monthly_payment = loan / n
    else:
        monthly_payment = loan * r * (1 + r) ** n / ((1 + r) ** n - 1)

    pmi_threshold = 0.78 * price
    pmi_monthly = loan * PMI_ANNUAL_RATE / 12
    pmi_cancelled = False

    balance = loan
    schedule = []

    for month in range(1, 61):
        interest = balance * r
        principal = monthly_payment - interest
        balance -= principal

        if pmi_cancelled or balance <= pmi_threshold:
            pmi_cancelled = True
            pmi = 0.0
        else:
            pmi = pmi_monthly

        schedule.append({
            "month": month,
            "principal": principal,
            "interest": interest,
            "balance": balance,
            "pmi": pmi,
        })

    return schedule


HOMESTEAD_EXEMPTION = 50_000  # Florida statutory exemption (dollars, year 2+)


def calculate_monthly_property_tax(price, tax_rate_pct, month):
    """Returns monthly property tax in dollars for the given month (1-60)."""
    assessed = price if month <= 12 else price - HOMESTEAD_EXEMPTION
    return assessed * (tax_rate_pct / 100) / 12


def calculate_upfront_cash(price, down_pct, closing_pct, furniture):
    """Returns total upfront cash: down payment + closing costs + furniture."""
    down_payment = price * (down_pct / 100)
    closing_costs = price * (closing_pct / 100)
    return down_payment + closing_costs + furniture


def calculate_investment_portfolio(initial_capital, monthly_contribution, annual_rate, months=60):
    """Returns list of `months` monthly portfolio values with monthly compounding (NFR8)."""
    monthly_rate = annual_rate / 100 / 12
    portfolio = []
    balance = initial_capital
    for _ in range(months):
        balance = (balance + monthly_contribution) * (1 + monthly_rate)
        portfolio.append(balance)
    return portfolio


def get_special_assessment_for_month(amount, assessment_month, current_month):
    """Returns special assessment cash outflow for current_month, else 0.0 (FR18)."""
    if amount > 0 and current_month == assessment_month:
        return float(amount)
    return 0.0


FL_DOC_STAMP_RATE = 0.007  # Florida documentary stamp tax (0.70% of sale price)


def calculate_exit_sell(price, appreciation_rate, remaining_balance, realtor_commission_pct):
    """Returns net proceeds from selling at year 5 (FR19)."""
    appreciated_value = price * (1 + appreciation_rate / 100) ** 5
    realtor_fee = appreciated_value * (realtor_commission_pct / 100)
    doc_stamp = appreciated_value * FL_DOC_STAMP_RATE
    return appreciated_value - realtor_fee - doc_stamp - remaining_balance


def calculate_exit_rent_out(monthly_rental_income, vacancy_rate_pct, mgmt_fee_pct,
                             monthly_carrying_costs, appreciated_value, remaining_balance):
    """Returns 60-month net landlord cash flow + home equity at month 60 (FR20)."""
    effective_income = monthly_rental_income * (1 - vacancy_rate_pct / 100)
    net_monthly_income = effective_income * (1 - mgmt_fee_pct / 100)
    monthly_net_cashflow = net_monthly_income - monthly_carrying_costs
    cumulative_cashflow = monthly_net_cashflow * 60
    home_equity = appreciated_value - remaining_balance
    return cumulative_cashflow + home_equity


def calculate_exit_continue_renting(portfolio_values):
    """Returns renter's portfolio value at month 60 (FR21)."""
    return portfolio_values[-1]
