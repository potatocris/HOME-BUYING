import streamlit as st
import defaults

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

# ── Build slider_values dict (keyed by defaults.py constant names) ────────────
# This dict is the interface to calculations (Story 2.3) and URL state (Story 2.7).
# Key names MUST match PARAM_MAP values in url_state.py exactly.
slider_values = {
    "HOME_PRICE":                home_price,
    "MORTGAGE_RATE":             mortgage_rate,
    "HOA_MONTHLY":               hoa_monthly,
    "HO6_INSURANCE_ANNUAL":      ho6_insurance_annual,
    "PROPERTY_TAX_RATE":         property_tax_rate,
    "MARKET_RENT":               market_rent,
    "APPRECIATION_RATE":         appreciation_rate,
    "INVESTMENT_RETURN_RATE":    investment_return_rate,
    "CLOSING_COST_PCT":          closing_cost_pct,
    "FURNITURE_BUDGET":          furniture_budget,
    "SPECIAL_ASSESSMENT_AMOUNT": special_assessment_amount,
    "SPECIAL_ASSESSMENT_MONTH":  special_assessment_month,
    "RENTAL_INCOME_MONTHLY":     rental_income_monthly,
    "VACANCY_RATE":              vacancy_rate,
    "PROPERTY_MGMT_FEE_PCT":     property_mgmt_fee_pct,
    "REALTOR_COMMISSION_PCT":    realtor_commission_pct,
}

# ── Main area: placeholder (Story 2.3 will replace this) ─────────────────────
st.title("Miami Home Buying Decision Tool")
st.info("Calculations and comparison display coming in Story 2.3.")
