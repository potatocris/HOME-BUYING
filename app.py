import streamlit as st
import defaults
import calculations
import formatting
import plotly.graph_objects as go
import pandas as pd
import url_state


def _headline_card(winner: str, difference: float, horizon_years: int, down_pct: float, break_even_text: str) -> str:
    # Accent #2B6CB0 is winner-independent (UX-DR11): only the text changes
    # between renting-wins and buying-wins, never the color.
    return f"""
<div aria-label="Financial comparison headline"
     style="background:#F5F7FA; padding:1.5rem; border-radius:8px; height:100%; color:#1A1D2E;">
  <p style="color:#1A1D2E; font-size:1.05rem; font-weight:600; margin:0 0 0.5rem 0;">Outcome</p>
  <p style="color:#2B6CB0; font-size:2.5rem; font-weight:700; margin:0 0 0.25rem 0; line-height:1.1;">
    {formatting.fmt_dollar(difference)}
  </p>
  <p style="color:#1A1D2E; font-size:1.1rem; font-weight:400; margin:0 0 0.5rem 0;">
    {winner} is better by {formatting.fmt_dollar(difference)} over {horizon_years} year{"s" if horizon_years != 1 else ""}
  </p>
  <p style="color:#1A1D2E; font-size:0.875rem; margin:0; opacity:0.75;">At {formatting.fmt_pct_compact(down_pct)} down · {break_even_text}</p>
</div>
"""


def _renting_card(starting_rent: float, total_rent: float, growth_pct: float,
                  monthly_invested: float, horizon_years: int) -> str:
    yrs = f"{horizon_years} year{'s' if horizon_years != 1 else ''}"
    return f"""
<div aria-label="Renting summary"
     style="background:#F5F7FA; padding:1.5rem; border-radius:8px; height:100%; color:#1A1D2E;">
  <p style="color:#2B6CB0; font-size:1.05rem; font-weight:600; margin:0 0 0.5rem 0;">Renting</p>
  <p style="color:#1A1D2E; font-size:1.4rem; font-weight:700; margin:0;">{formatting.fmt_dollar(starting_rent)}<span style="font-size:0.82rem; font-weight:400">&thinsp;/mo</span></p>
  <p style="color:#1A1D2E; font-size:0.82rem; margin:0 0 1rem 0; opacity:0.75;">Starting rent · grows {formatting.fmt_pct_compact(growth_pct)}/yr</p>
  <p style="color:#1A1D2E; font-size:0.82rem; margin:0;">Invested monthly (start)</p>
  <p style="color:#1A1D2E; font-size:1.1rem; font-weight:600; margin:0 0 1rem 0;">{formatting.fmt_dollar(monthly_invested)}<span style="font-size:0.82rem; font-weight:400">&thinsp;/mo</span></p>
  <p style="color:#1A1D2E; font-size:0.82rem; margin:0;">Total rent over {yrs}</p>
  <p style="color:#1A1D2E; font-size:1.1rem; font-weight:600; margin:0;">{formatting.fmt_dollar(total_rent)}</p>
</div>
"""


def _buying_card(monthly_total: float, principal: float, interest: float,
                 tax: float, other: float, total_paid: float,
                 monthly_invested: float, horizon_years: int) -> str:
    # "Other costs" bundles HOA + HO-6 insurance + PMI (month-1 snapshot, Zillow-style).
    yrs = f"{horizon_years} year{'s' if horizon_years != 1 else ''}"
    return f"""
<div aria-label="Buying summary"
     style="background:#F5F7FA; padding:1.5rem; border-radius:8px; height:100%; color:#1A1D2E;">
  <p style="color:#6B46C1; font-size:1.05rem; font-weight:600; margin:0 0 0.5rem 0;">Buying</p>
  <p style="color:#1A1D2E; font-size:1.4rem; font-weight:700; margin:0 0 0.5rem 0;">{formatting.fmt_dollar(monthly_total)}<span style="font-size:0.82rem; font-weight:400">&thinsp;/mo</span></p>
  <table style="width:100%; font-size:0.82rem; border-collapse:collapse; color:#1A1D2E;">
    <tr><td>Principal</td><td style="text-align:right">{formatting.fmt_dollar(principal)}</td></tr>
    <tr><td>Interest</td><td style="text-align:right">{formatting.fmt_dollar(interest)}</td></tr>
    <tr><td>Property Tax</td><td style="text-align:right">{formatting.fmt_dollar(tax)}</td></tr>
    <tr><td>Other costs</td><td style="text-align:right">{formatting.fmt_dollar(other)}</td></tr>
  </table>
  <p style="color:#1A1D2E; font-size:0.82rem; margin:1rem 0 0 0;">Invested monthly (start)</p>
  <p style="color:#1A1D2E; font-size:1.1rem; font-weight:600; margin:0;">{formatting.fmt_dollar(monthly_invested)}<span style="font-size:0.82rem; font-weight:400">&thinsp;/mo</span></p>
  <p style="color:#1A1D2E; font-size:0.82rem; margin:1rem 0 0 0;">Total paid over {yrs}</p>
  <p style="color:#1A1D2E; font-size:1.1rem; font-weight:600; margin:0;">{formatting.fmt_dollar(total_paid)}</p>
</div>
"""


# Outcome-neutral by design (UX-DR11): blue (Renting) and purple (Buying) are
# neutral cross-references to the chart line colors — NOT good/bad signals.
# Do not collapse to one color or switch to red/green.
_BETTER_COLORS = {
    "Renting": "color: #2B6CB0; font-weight: 600",
    "Buying":  "color: #6B46C1; font-weight: 600",
}


def _disclaimer_banner(last_updated: str) -> str:
    return f"""
<div aria-label="Disclaimer and defaults information"
     style="background:#EBF4FF; padding:0.5rem 1rem; border-radius:4px; margin-bottom:1rem;
            display:flex; justify-content:space-between; align-items:center;">
  <span style="color:#2B6CB0; font-size:0.75rem;">
    Financial calculator only. No lender affiliation. Not financial advice.
  </span>
  <span style="color:#2B6CB0; font-size:0.75rem;">
    Defaults last updated: {last_updated}
  </span>
</div>
"""


st.set_page_config(page_title="Miami Home Buying Decision Tool", layout="wide")

# ── Sidebar: all 18 input sliders ─────────────────────────────────────────────
_initial = url_state.decode_state(st.query_params.to_dict())
if _initial['HORIZON_YEARS'] not in [5, 10, 15, 20, 25, 30]:
    _initial['HORIZON_YEARS'] = defaults.HORIZON_YEARS
_has_url_params = bool(st.query_params.to_dict())

with st.sidebar:
    # Color-code slider labels by group: Rental=blue (#2B6CB0), Buy=purple (#6B46C1) —
    # matching the chart/table palette. Streamlit 1.39+ adds a `st-key-<key>` class to
    # each keyed widget's container div; we target those prefixes. Scoped to the sidebar
    # so coloring can't leak into the main area. Key prefixes are the CSS contract.
    st.markdown(
        """<style>
/* Slider labels — neutral grey (rent/buy colour-coding removed). Targets every
   sidebar slider key prefix so all labels match. */
section[data-testid="stSidebar"] div[class*="st-key-rent_"] label,
section[data-testid="stSidebar"] div[class*="st-key-buy_"]  label,
section[data-testid="stSidebar"] div[class*="st-key-nx_"]   label { color:#4A5568 !important; }
/* Slider control (track fill line + thumb + value bubble) inherits the theme's blue
   primaryColor. The fill is a dynamic react-range gradient set inline as a
   linear-gradient, so we can't set a solid color without losing the fill split.
   grayscale(1) desaturates the blue to neutral grey while preserving the
   filled/unfilled gradient split. We target the element carrying the inline gradient
   (the track line); the thumb + value bubble are its descendants, so one filter
   covers them all. Applied to every sidebar slider so all controls match. */
section[data-testid="stSidebar"] [style*="linear-gradient"] { filter:grayscale(1); }
</style>""",
        unsafe_allow_html=True,
    )

    # ── Comparison Settings (shared — neutral, default color) ─────────────────
    st.markdown('<p style="color:#4A5568;font-weight:700;font-size:1.05rem;margin:0 0 0.25rem 0;">Comparison Settings</p>', unsafe_allow_html=True)
    if not _has_url_params:
        st.caption("Miami defaults loaded")

    horizon_years = st.select_slider(
        "Comparison Horizon (years)",
        options=[5, 10, 15, 20, 25, 30],
        value=_initial['HORIZON_YEARS'],
        key="nx_horizon",
    )
    investment_return_rate = st.slider(
        "Investment Return (%/yr)",
        min_value=0.0, max_value=15.0,
        value=_initial['INVESTMENT_RETURN_RATE'], step=0.25,
        format="%.2f%%",
        key="nx_invest",
    )
    _lo, _hi = st.columns(2)
    _lo.caption("0.00%")
    _hi.markdown('<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">15.00%</p>', unsafe_allow_html=True)

    monthly_budget = st.slider(
        "Monthly Budget",
        min_value=1_000.0, max_value=10_000.0,
        value=_initial['MONTHLY_BUDGET'], step=100.0,
        format="$%.0f",
        key="nx_budget",
    )
    st.caption("Income grows at rent + 0.25%/yr")

    # ── Rental (neutral grey #4A5568) ─────────────────────────────────────────
    st.markdown('<p style="color:#4A5568;font-weight:700;font-size:1.05rem;margin:1.25rem 0 0.25rem 0;">Rental</p>', unsafe_allow_html=True)
    market_rent = st.slider(
        "Market Rent (monthly)",
        min_value=500.0, max_value=6_000.0,
        value=_initial['MARKET_RENT'], step=50.0,
        format="$%.0f",
        key="rent_market",
    )
    rent_growth_rate = st.slider(
        "Rent Increase (%/yr)",
        min_value=0.0, max_value=10.0,
        value=_initial['RENT_GROWTH_RATE'], step=0.25,
        format="%.2f%%",
        key="rent_growth",
    )

    # ── Buy (neutral grey #4A5568) ────────────────────────────────────────────
    st.markdown('<p style="color:#4A5568;font-weight:700;font-size:1.05rem;margin:1.25rem 0 0.25rem 0;">Buy</p>', unsafe_allow_html=True)
    home_price = st.slider(
        "Home Price",
        min_value=100_000.0, max_value=1_000_000.0,
        value=_initial['HOME_PRICE'], step=5_000.0,
        format="$%.0f",
        key="buy_home_price",
    )
    down_pct = st.slider(
        "Down Payment (%)",
        min_value=3.0, max_value=30.0,
        value=_initial['DOWN_PCT'], step=0.5,
        format="%.1f%%",
        key="buy_down_pct",
    )
    mortgage_rate = st.slider(
        "Mortgage Rate (%)",
        min_value=3.0, max_value=12.0,
        value=_initial['MORTGAGE_RATE'], step=0.125,
        format="%.3f%%",
        key="buy_mortgage",
    )
    _lo, _hi = st.columns(2)
    _lo.caption("3.00%")
    _hi.markdown('<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">12.00%</p>', unsafe_allow_html=True)
    hoa_monthly = st.slider(
        "HOA (monthly)",
        min_value=0.0, max_value=2_500.0,
        value=_initial['HOA_MONTHLY'], step=25.0,
        format="$%.0f",
        key="buy_hoa",
    )
    ho6_insurance_annual = st.slider(
        "HO-6 Insurance (annual)",
        min_value=500.0, max_value=6_000.0,
        value=_initial['HO6_INSURANCE_ANNUAL'], step=100.0,
        format="$%.0f",
        key="buy_ho6",
    )
    property_tax_rate = st.slider(
        "Property Tax Rate (%)",
        min_value=0.5, max_value=3.0,
        value=_initial['PROPERTY_TAX_RATE'], step=0.05,
        format="%.2f%%",
        key="buy_proptax",
    )
    _lo, _hi = st.columns(2)
    _lo.caption("0.50%")
    _hi.markdown('<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">3.00%</p>', unsafe_allow_html=True)
    cost_growth_rate = st.slider(
        "Annual Cost Growth (%/yr)",
        min_value=0.0, max_value=8.0,
        value=_initial['COST_GROWTH_RATE'], step=0.25,
        format="%.2f%%",
        key="buy_cost_growth",
    )
    _lo, _hi = st.columns(2)
    _lo.caption("0.00%")
    _hi.markdown('<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">8.00%</p>', unsafe_allow_html=True)
    st.caption("Grows HOA, insurance & property-tax value (tax capped at 3%/yr)")
    appreciation_rate = st.slider(
        "Home Appreciation (%/yr)",
        min_value=0.0, max_value=10.0,
        value=_initial['APPRECIATION_RATE'], step=0.25,
        format="%.2f%%",
        key="buy_appreciation",
    )
    _lo, _hi = st.columns(2)
    _lo.caption("0.00%")
    _hi.markdown('<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">10.00%</p>', unsafe_allow_html=True)
    closing_cost_pct = st.slider(
        "Closing Costs (%)",
        min_value=1.0, max_value=6.0,
        value=_initial['CLOSING_COST_PCT'], step=0.25,
        format="%.2f%%",
        key="buy_closing",
    )
    _lo, _hi = st.columns(2)
    _lo.caption("1.00%")
    _hi.markdown('<p style="text-align:right;font-size:0.75rem;color:#718096;margin:0;padding:0">6.00%</p>', unsafe_allow_html=True)
    furniture_budget = st.slider(
        "Furniture & Improvements",
        min_value=0.0, max_value=50_000.0,
        value=_initial['FURNITURE_BUDGET'], step=500.0,
        format="$%.0f",
        key="buy_furniture",
    )

    # ── Advanced Inputs (landlord scenario — part of Buy) ─────────────────────
    with st.expander("Advanced Inputs"):
        st.caption("Landlord scenario: used in the Rent Out exit path calculation")
        rental_income_monthly = st.slider(
            "Rental Income (monthly)",
            min_value=500.0, max_value=5_000.0,
            value=_initial['RENTAL_INCOME_MONTHLY'], step=50.0,
            format="$%.0f",
            key="buy_rental_income",
        )
        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            min_value=0.0, max_value=30.0,
            value=_initial['VACANCY_RATE'], step=1.0,
            format="%.1f%%",
            key="buy_vacancy",
        )
        property_mgmt_fee_pct = st.slider(
            "Property Mgmt Fee (%)",
            min_value=0.0, max_value=20.0,
            value=_initial['PROPERTY_MGMT_FEE_PCT'], step=1.0,
            format="%.1f%%",
            key="buy_mgmt",
        )

        st.caption("Realtor commission: applied to sale price in the Sell exit path")
        realtor_commission_pct = st.slider(
            "Realtor Commission (%)",
            min_value=0.0, max_value=8.0,
            value=_initial['REALTOR_COMMISSION_PCT'], step=0.25,
            format="%.2f%%",
            key="buy_realtor",
        )

# ── Write current slider state to URL ─────────────────────────────────────────
st.query_params.update(url_state.encode_state({
    'HOME_PRICE':                home_price,
    'DOWN_PCT':                  down_pct,
    'HORIZON_YEARS':             horizon_years,
    'MORTGAGE_RATE':             mortgage_rate,
    'HOA_MONTHLY':               hoa_monthly,
    'HO6_INSURANCE_ANNUAL':      ho6_insurance_annual,
    'PROPERTY_TAX_RATE':         property_tax_rate,
    'MARKET_RENT':               market_rent,
    'RENT_GROWTH_RATE':          rent_growth_rate,
    'APPRECIATION_RATE':         appreciation_rate,
    'INVESTMENT_RETURN_RATE':    investment_return_rate,
    'CLOSING_COST_PCT':          closing_cost_pct,
    'FURNITURE_BUDGET':          furniture_budget,
    'RENTAL_INCOME_MONTHLY':     rental_income_monthly,
    'VACANCY_RATE':              vacancy_rate,
    'PROPERTY_MGMT_FEE_PCT':     property_mgmt_fee_pct,
    'REALTOR_COMMISSION_PCT':    realtor_commission_pct,
    'MONTHLY_BUDGET':            monthly_budget,
    'COST_GROWTH_RATE':          cost_growth_rate,
}))

# ── Rent vs Buy Two-Path Calculation ──────────────────────────────────────────
_calc_error = False
try:
    total_months  = horizon_years * 12

    schedule     = calculations.calculate_amortization_schedule(
        home_price, down_pct, mortgage_rate, months=total_months
    )
    upfront_cash = calculations.calculate_upfront_cash(
        home_price, down_pct, closing_cost_pct, furniture_budget
    )
    monthly_rate = investment_return_rate / 100 / 12

    # Budget-based model (Story 4.1): both sides invest what's left of a shared
    # monthly budget after housing. Income grows at rent-growth + 0.25 pct-pts.
    income_growth = rent_growth_rate + calculations.INCOME_RENT_PREMIUM

    # Pass 1: renter portfolio (budget − rent) + buyer contribution list (budget − buying)
    renter_balance      = upfront_cash
    renter_monthly      = []
    renter_contrib_list = []  # per-month amount the renter invests: max(0, budget - rent)
    buyer_surplus_list  = []  # per-month amount the buyer invests: max(0, budget - buying)
    total_rent_paid    = 0.0  # summary column: actual escalating rent paid over period
    total_buying_paid  = 0.0  # summary column: actual monthly buying costs over period

    for month_idx, rec in enumerate(schedule):
        m        = month_idx + 1
        p_and_i  = rec["interest"] + rec["principal"]
        pmi_m    = rec["pmi"]
        hoa_m    = calculations.annual_escalate(hoa_monthly, cost_growth_rate, m)
        ins_m    = calculations.annual_escalate(ho6_insurance_annual / 12, cost_growth_rate, m)
        tax_m    = calculations.calculate_monthly_property_tax(
            home_price, property_tax_rate, m, cost_growth_rate
        )
        buying_cost_m = p_and_i + pmi_m + hoa_m + tax_m + ins_m

        rent_m   = calculations.escalated_rent(market_rent, rent_growth_rate, m)
        budget_m = calculations.annual_escalate(monthly_budget, income_growth, m)
        total_rent_paid   += rent_m
        total_buying_paid += buying_cost_m

        renter_contribution = max(0.0, budget_m - rent_m)
        renter_balance      = (renter_balance + renter_contribution) * (1 + monthly_rate)
        renter_monthly.append(renter_balance)
        renter_contrib_list.append(renter_contribution)

        buyer_surplus_list.append(max(0.0, budget_m - buying_cost_m))

    # Buyer side portfolio: $0 start, grows from monthly budget surpluses
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

    # Monthly invested amount: per-year averages (table) + month-1 figure (cards)
    renter_invest_annual = calculations.get_annual_averages(renter_contrib_list)
    buyer_invest_annual  = calculations.get_annual_averages(buyer_surplus_list)
    renter_invest_m1     = renter_contrib_list[0]
    buyer_invest_m1      = buyer_surplus_list[0]

except Exception:
    _calc_error = True

st.markdown(_disclaimer_banner(defaults.DEFAULTS_LAST_UPDATED), unsafe_allow_html=True)
st.title("Miami Home Buying Decision Tool")

if _calc_error:
    st.error("Unable to calculate — please check your inputs.")
else:
    # ── Break-even detection ───────────────────────────────────────────────────
    break_even_year = None
    if len(renter_annual) >= 2:
        prev_renting_ahead = renter_annual[0] >= buyer_annual[0]
        for i in range(1, len(renter_annual)):
            curr_renting_ahead = renter_annual[i] >= buyer_annual[i]
            if curr_renting_ahead != prev_renting_ahead:
                break_even_year = i + 1  # 1-indexed: renter_annual[0] = year 1
                break
            prev_renting_ahead = curr_renting_ahead

    if break_even_year is not None:
        break_even_text = f"Break-even at year {break_even_year}"
    else:
        break_even_text = f"No break-even within {horizon_years} year{'s' if horizon_years != 1 else ''}"

    # ── Main area ─────────────────────────────────────────────────────────────
    final_renter = renter_annual[-1]
    final_buyer  = buyer_annual[-1]
    if final_renter >= final_buyer:
        winner     = "Renting"
        difference = final_renter - final_buyer
    else:
        winner     = "Buying"
        difference = final_buyer - final_renter

    # ── Three-column summary (Renting · Buying · Headline) ─────────────────────
    rec0         = schedule[0]
    principal_m1 = rec0["principal"]
    interest_m1  = rec0["interest"]
    tax_m1       = calculations.calculate_monthly_property_tax(home_price, property_tax_rate, 1)
    ins_m1       = ho6_insurance_annual / 12
    other_m1     = hoa_monthly + ins_m1 + rec0["pmi"]
    buying_total_m1 = principal_m1 + interest_m1 + tax_m1 + other_m1

    col1, col2, col3 = st.columns(3)
    col1.markdown(
        _renting_card(market_rent, total_rent_paid, rent_growth_rate,
                      renter_invest_m1, horizon_years),
        unsafe_allow_html=True,
    )
    col2.markdown(
        _buying_card(buying_total_m1, principal_m1, interest_m1, tax_m1, other_m1,
                     total_buying_paid, buyer_invest_m1, horizon_years),
        unsafe_allow_html=True,
    )
    col3.markdown(
        _headline_card(winner, difference, horizon_years, down_pct, break_even_text),
        unsafe_allow_html=True,
    )

    # ── Wealth over time chart ─────────────────────────────────────────────────
    x_vals        = list(range(horizon_years + 1))
    renter_series = [upfront_cash] + renter_annual
    buyer_series  = [0.0] + buyer_annual

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=renter_series,
        name="Rent + Invest",
        mode="lines+markers",
        line=dict(color="#2B6CB0", width=2),
        marker=dict(size=5),
        hovertemplate="%{y:$,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x_vals, y=buyer_series,
        name="Buy + Invest",
        mode="lines+markers",
        line=dict(color="#6B46C1", width=2),
        marker=dict(size=5),
        hovertemplate="%{y:$,.0f}<extra></extra>",
    ))

    if break_even_year is not None:
        fig.add_vline(
            x=break_even_year,
            line_dash="dash",
            line_color="#A0AEC0",
            annotation_text=f"Break-even: year {break_even_year}",
            annotation_position="top",
            annotation_font=dict(color="#1A1D2E", size=12),
        )

    fig.update_layout(
        template="simple_white",
        title=dict(text="Total Wealth Over Time", font=dict(color="#1A1D2E", size=16)),
        xaxis=dict(
            title=dict(text="Year", font=dict(color="#1A1D2E")),
            tickfont=dict(color="#1A1D2E"),
            tickmode="linear", dtick=5, tick0=0,
            gridcolor="#E2E8F0", showgrid=True,
        ),
        yaxis=dict(
            title=dict(text="Total Net Wealth", font=dict(color="#1A1D2E")),
            tickfont=dict(color="#1A1D2E"),
            tickprefix="$", tickformat=",",
            gridcolor="#E2E8F0", showgrid=True,
        ),
        legend=dict(
            font=dict(color="#1A1D2E"),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=0, r=0, t=60, b=0),
        hovermode="x unified",
        font=dict(color="#1A1D2E"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Annual wealth breakdown table ─────────────────────────────────────────
    table_rows = []
    for i, (r, b) in enumerate(zip(renter_annual, buyer_annual)):
        diff = r - b
        table_rows.append({
            "Year": i + 1,
            "Rent + Invest": formatting.fmt_dollar(r),
            "Buy + Invest": formatting.fmt_dollar(b),
            "Difference": formatting.fmt_dollar(diff),
            "Rent: Invested/mo": formatting.fmt_dollar(renter_invest_annual[i]),
            "Buy: Invested/mo": formatting.fmt_dollar(buyer_invest_annual[i]),
            "Better": "Renting" if r >= b else "Buying",
        })

    st.subheader("Annual Wealth Breakdown")
    df = pd.DataFrame(table_rows)
    styled = df.style.map(lambda v: _BETTER_COLORS.get(v, ""), subset=["Better"])
    st.dataframe(
        styled,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Year": st.column_config.NumberColumn("Year", format="%d", width="small"),
        },
    )
