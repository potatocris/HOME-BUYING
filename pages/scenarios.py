import streamlit as st
import defaults
import calculations
import formatting

st.set_page_config(page_title="Scenario Comparison", layout="wide")

# ── Sidebar: all 16 input sliders ─────────────────────────────────────────────
with st.sidebar:
    # ── Essential Inputs ──────────────────────────────────────────────────────
    st.subheader("Essential Inputs")
    st.caption("Miami defaults loaded")

    home_price = st.slider(
        "Home Price",
        min_value=100_000.0, max_value=1_000_000.0,
        value=defaults.HOME_PRICE, step=5_000.0,
        format="$%.0f",
    )
    mortgage_rate = st.slider(
        "Mortgage Rate (%)",
        min_value=3.0, max_value=12.0,
        value=defaults.MORTGAGE_RATE, step=0.125,
        format="%.3f%%",
    )
    hoa_monthly = st.slider(
        "HOA (monthly)",
        min_value=0.0, max_value=2_500.0,
        value=defaults.HOA_MONTHLY, step=25.0,
        format="$%.0f",
    )
    ho6_insurance_annual = st.slider(
        "HO-6 Insurance (annual)",
        min_value=500.0, max_value=6_000.0,
        value=defaults.HO6_INSURANCE_ANNUAL, step=100.0,
        format="$%.0f",
    )
    property_tax_rate = st.slider(
        "Property Tax Rate (%)",
        min_value=0.5, max_value=3.0,
        value=defaults.PROPERTY_TAX_RATE, step=0.05,
        format="%.2f%%",
    )
    market_rent = st.slider(
        "Market Rent (monthly)",
        min_value=500.0, max_value=6_000.0,
        value=defaults.MARKET_RENT, step=50.0,
        format="$%.0f",
    )
    rent_growth_rate = st.slider(
        "Rent Increase (%/yr)",
        min_value=0.0, max_value=10.0,
        value=defaults.RENT_GROWTH_RATE, step=0.25,
        format="%.2f%%",
    )
    monthly_budget = st.slider(
        "Monthly Budget",
        min_value=1_000.0, max_value=10_000.0,
        value=defaults.MONTHLY_BUDGET, step=100.0,
        format="$%.0f",
    )
    st.caption("Income grows at rent + 0.25%/yr")
    appreciation_rate = st.slider(
        "Home Appreciation (%/yr)",
        min_value=0.0, max_value=10.0,
        value=defaults.APPRECIATION_RATE, step=0.25,
        format="%.2f%%",
    )
    investment_return_rate = st.slider(
        "Investment Return (%/yr)",
        min_value=0.0, max_value=15.0,
        value=defaults.INVESTMENT_RETURN_RATE, step=0.25,
        format="%.2f%%",
    )
    closing_cost_pct = st.slider(
        "Closing Costs (%)",
        min_value=1.0, max_value=6.0,
        value=defaults.CLOSING_COST_PCT, step=0.25,
        format="%.2f%%",
    )
    furniture_budget = st.slider(
        "Furniture & Improvements",
        min_value=0.0, max_value=50_000.0,
        value=defaults.FURNITURE_BUDGET, step=500.0,
        format="$%.0f",
    )

    # ── Advanced Inputs ───────────────────────────────────────────────────────
    with st.expander("Advanced Inputs"):
        st.caption("Landlord scenario: used in the Rent Out exit path calculation")
        rental_income_monthly = st.slider(
            "Rental Income (monthly)",
            min_value=500.0, max_value=5_000.0,
            value=defaults.RENTAL_INCOME_MONTHLY, step=50.0,
            format="$%.0f",
        )
        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            min_value=0.0, max_value=30.0,
            value=defaults.VACANCY_RATE, step=1.0,
            format="%.1f%%",
        )
        property_mgmt_fee_pct = st.slider(
            "Property Mgmt Fee (%)",
            min_value=0.0, max_value=20.0,
            value=defaults.PROPERTY_MGMT_FEE_PCT, step=1.0,
            format="%.1f%%",
        )

        st.caption("Realtor commission: applied to sale price in the Sell exit path")
        realtor_commission_pct = st.slider(
            "Realtor Commission (%)",
            min_value=0.0, max_value=8.0,
            value=defaults.REALTOR_COMMISSION_PCT, step=0.25,
            format="%.2f%%",
        )

# ── Run calculations for all 4 down payment scenarios ─────────────────────────
DOWN_PAYMENT_SCENARIOS = [5, 10, 15, 20]
scenarios = []

for down_pct in DOWN_PAYMENT_SCENARIOS:
    schedule = calculations.calculate_amortization_schedule(
        home_price, down_pct, mortgage_rate
    )
    upfront_cash = calculations.calculate_upfront_cash(
        home_price, down_pct, closing_cost_pct, furniture_budget
    )

    rec0         = schedule[0]
    p_and_i_m1   = rec0["interest"] + rec0["principal"]
    pmi_m1       = rec0["pmi"]
    hoa_m1       = hoa_monthly
    tax_m1       = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, 1)
    insurance_m1 = ho6_insurance_annual / 12
    total_m1     = p_and_i_m1 + pmi_m1 + hoa_m1 + tax_m1 + insurance_m1

    monthly_cost_m1 = {
        "p_and_i":      p_and_i_m1,
        "pmi":          pmi_m1,
        "hoa":          hoa_m1,
        "property_tax": tax_m1,
        "insurance":    insurance_m1,
        "total":        total_m1,
    }

    # Budget-based renter portfolio (Story 4.1): invest max(0, budget − rent) each
    # month, seeded with upfront cash. Budget grows at rent-growth + 0.25 pct-pts;
    # rent escalates annually. (Page 2 has no per-month buyer cost trajectory, so the
    # cost-growth input lives only on the main page.)
    income_growth        = rent_growth_rate + calculations.INCOME_RENT_PREMIUM
    renter_contrib_list  = []
    for m_idx in range(len(schedule)):
        m        = m_idx + 1
        rent_m   = calculations.escalated_rent(market_rent, rent_growth_rate, m)
        budget_m = calculations.annual_escalate(monthly_budget, income_growth, m)
        renter_contrib_list.append(max(0.0, budget_m - rent_m))
    monthly_contribution = renter_contrib_list[0]  # month-1 figure (card display)
    portfolio_values     = calculations.calculate_renter_investment_portfolio(
        upfront_cash, renter_contrib_list, investment_return_rate
    )

    remaining_balance = schedule[-1]["balance"]
    appreciated_value = home_price * (1 + appreciation_rate / 100) ** 5

    carrying_costs_m1 = p_and_i_m1 + hoa_m1 + tax_m1 + insurance_m1

    exit_sell = calculations.calculate_exit_sell(
        home_price, appreciation_rate, remaining_balance, realtor_commission_pct
    )
    exit_rent_out = calculations.calculate_exit_rent_out(
        monthly_rental_income=rental_income_monthly,
        vacancy_rate_pct=vacancy_rate,
        mgmt_fee_pct=property_mgmt_fee_pct,
        monthly_carrying_costs=carrying_costs_m1,
        appreciated_value=appreciated_value,
        remaining_balance=remaining_balance,
    )
    exit_continue_renting = calculations.calculate_exit_continue_renting(portfolio_values)

    break_even_month = None
    for m_idx, rec in enumerate(schedule):
        m               = m_idx + 1
        home_value_at_m = home_price * (1 + appreciation_rate / 100) ** (m / 12)
        home_equity     = home_value_at_m - rec["balance"]
        if home_equity >= portfolio_values[m_idx]:
            break_even_month = m
            break

    scenarios.append({
        "down_pct":              down_pct,
        "upfront_cash":          upfront_cash,
        "schedule":              schedule,
        "monthly_cost_m1":       monthly_cost_m1,
        "monthly_contribution":  monthly_contribution,
        "portfolio_values":      portfolio_values,
        "exit_sell":             exit_sell,
        "exit_rent_out":         exit_rent_out,
        "exit_continue_renting": exit_continue_renting,
        "break_even_month":      break_even_month,
    })

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Scenario Comparison — 4 Down Payment Options")

cols = st.columns(4)
for col, sc in zip(cols, scenarios):
    mc = sc["monthly_cost_m1"]
    recurring_total = mc["p_and_i"] + mc["pmi"] + mc["hoa"] + mc["property_tax"] + mc["insurance"]

    card_html = f"""
<div aria-label="{formatting.fmt_pct_compact(sc['down_pct'])} down payment scenario"
     style="background:#F5F7FA;border:1px solid #D1D9E6;border-radius:8px;padding:16px;color:#1A1A1A">
  <div style="font-weight:600;font-size:1.05rem;color:#1A1A1A">{formatting.fmt_pct_compact(sc['down_pct'])} Down</div>
  <div style="font-size:0.82rem;color:#555;margin-bottom:10px">Upfront: {formatting.fmt_dollar(sc['upfront_cash'])}</div>
  <div style="font-size:1.4rem;font-weight:700;margin-bottom:10px;color:#1A1A1A">{formatting.fmt_dollar(recurring_total)}<span style="font-size:0.82rem;font-weight:400">&thinsp;/mo</span></div>
  <table style="width:100%;font-size:0.82rem;border-collapse:collapse;color:#1A1A1A">
    <tr><td>P&amp;I</td><td style="text-align:right">{formatting.fmt_dollar(mc['p_and_i'])}</td></tr>
    <tr><td>PMI</td><td style="text-align:right">{formatting.fmt_dollar(mc['pmi'])}</td></tr>
    <tr><td>HOA</td><td style="text-align:right">{formatting.fmt_dollar(mc['hoa'])}</td></tr>
    <tr><td>Property Tax</td><td style="text-align:right">{formatting.fmt_dollar(mc['property_tax'])}</td></tr>
    <tr><td>Insurance</td><td style="text-align:right">{formatting.fmt_dollar(mc['insurance'])}</td></tr>
    <tr style="border-top:1px solid #D1D9E6;font-weight:600">
      <td>Total</td><td style="text-align:right">{formatting.fmt_dollar(recurring_total)}</td>
    </tr>
  </table>
</div>
"""
    col.markdown(card_html, unsafe_allow_html=True)
