import streamlit as st
import defaults
import calculations

st.set_page_config(page_title="Miami Home Buying Decision Tool", layout="wide")

# ── Sidebar: all 16 input sliders ─────────────────────────────────────────────
# Story 2.7 will add url_state.decode_state() here to restore slider values from
# URL params. For now, value= points directly to defaults.py constants.
# Pattern: when Story 2.7 wires URL state, replace each value=defaults.CONST_NAME
# with value=_initial["CONST_NAME"] where _initial = url_state.decode_state(st.query_params.to_dict()).

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
    down_pct = st.slider(
        "Down Payment (%)",
        min_value=3.0, max_value=30.0,
        value=defaults.DOWN_PCT, step=0.5,
        format="%.1f%%",
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
        st.caption("Special assessment: a one-time lump-sum cost (e.g. post-Surfside reserves)")
        special_assessment_amount = st.slider(
            "Special Assessment ($)",
            min_value=0.0, max_value=100_000.0,
            value=defaults.SPECIAL_ASSESSMENT_AMOUNT, step=500.0,
            format="$%.0f",
        )
        special_assessment_month = st.slider(
            "Assessment Month (1–60)",
            min_value=1, max_value=60,
            value=defaults.SPECIAL_ASSESSMENT_MONTH, step=1,
        )

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

# ── Rent vs Buy Two-Path Calculation ──────────────────────────────────────────
# Story 2.6 replaces the next line with the timeline slider widget.
horizon_years = defaults.HORIZON_YEARS
total_months  = horizon_years * 12

schedule     = calculations.calculate_amortization_schedule(
    home_price, down_pct, mortgage_rate, months=total_months
)
upfront_cash = calculations.calculate_upfront_cash(
    home_price, down_pct, closing_cost_pct, furniture_budget
)
monthly_rate = investment_return_rate / 100 / 12

# Pass 1: renter portfolio (variable contributions) + buyer surplus list
renter_balance     = upfront_cash
renter_monthly     = []
buyer_surplus_list = []

for month_idx, rec in enumerate(schedule):
    m        = month_idx + 1
    p_and_i  = rec["interest"] + rec["principal"]
    pmi_m    = rec["pmi"]
    tax_m    = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, m)
    ins_m    = ho6_insurance_annual / 12
    buying_cost_m = p_and_i + pmi_m + hoa_monthly + tax_m + ins_m

    renter_contribution = max(0.0, buying_cost_m - market_rent)
    renter_balance      = (renter_balance + renter_contribution) * (1 + monthly_rate)
    renter_monthly.append(renter_balance)

    buyer_surplus_list.append(max(0.0, market_rent - buying_cost_m))

# Buyer side portfolio: $0 start, grows from monthly surpluses
buyer_portfolio = calculations.calculate_buyer_investment_portfolio(
    buyer_surplus_list, investment_return_rate
)

# Pass 2: buyer total wealth = home equity + side portfolio
buyer_monthly = []
for month_idx, rec in enumerate(schedule):
    m                   = month_idx + 1
    appreciated_value_m = home_price * (1 + appreciation_rate / 100) ** (m / 12)
    home_equity_m       = appreciated_value_m - rec["balance"]
    buyer_monthly.append(home_equity_m + buyer_portfolio[month_idx])

# Annual snapshots for chart (Story 2.7) and table (Story 2.8)
renter_annual = calculations.get_annual_snapshots(renter_monthly)
buyer_annual  = calculations.get_annual_snapshots(buyer_monthly)

# ── Main area ─────────────────────────────────────────────────────────────────
# Story 2.6 replaces this placeholder with the headline + timeline slider.
# Story 2.7 adds the Plotly chart. Story 2.8 adds the annual table.
st.title("Miami Home Buying Decision Tool")
st.info(
    f"Calculations ready — {horizon_years}-year horizon, {down_pct:.1f}% down. "
    f"Year {horizon_years}: Renting → ${renter_annual[-1]:,.0f} | "
    f"Buying → ${buyer_annual[-1]:,.0f}. "
    f"Chart and headline coming in Stories 2.6–2.7."
)
