import streamlit as st
import defaults
import calculations
import plotly.graph_objects as go
import pandas as pd
import url_state


def _headline_card(winner: str, difference: float, horizon_years: int, break_even_text: str) -> str:
    return f"""
<div aria-label="Financial comparison headline"
     style="background:#F5F7FA; padding:1.5rem 2rem; border-radius:8px; margin-bottom:1.5rem;">
  <p style="color:#1A1D2E; font-size:0.875rem; margin:0 0 0.25rem 0;">At current assumptions</p>
  <p style="color:#2B6CB0; font-size:2.5rem; font-weight:700; margin:0 0 0.25rem 0; line-height:1.1;">
    ${difference:,.0f}
  </p>
  <p style="color:#1A1D2E; font-size:1.1rem; font-weight:400; margin:0 0 0.5rem 0;">
    {winner} is better by ${difference:,.0f} over {horizon_years} year{"s" if horizon_years != 1 else ""}
  </p>
  <p style="color:#1A1D2E; font-size:0.875rem; margin:0; opacity:0.75;">{break_even_text}</p>
</div>
"""


def _fmt_dollar(v: float) -> str:
    if v < 0:
        return f"(${abs(v):,.0f})"
    return f"${v:,.0f}"


st.set_page_config(page_title="Miami Home Buying Decision Tool", layout="wide")

# ── Sidebar: all 18 input sliders ─────────────────────────────────────────────
_initial = url_state.decode_state(st.query_params.to_dict())
if _initial['HORIZON_YEARS'] not in [5, 10, 15, 20, 25, 30]:
    _initial['HORIZON_YEARS'] = defaults.HORIZON_YEARS

with st.sidebar:
    # ── Essential Inputs ──────────────────────────────────────────────────────
    st.subheader("Essential Inputs")
    st.caption("Miami defaults loaded")

    home_price = st.slider(
        "Home Price",
        min_value=100_000.0, max_value=1_000_000.0,
        value=_initial['HOME_PRICE'], step=5_000.0,
        format="$%.0f",
    )
    down_pct = st.slider(
        "Down Payment (%)",
        min_value=3.0, max_value=30.0,
        value=_initial['DOWN_PCT'], step=0.5,
        format="%.1f%%",
    )
    horizon_years = st.select_slider(
        "Comparison Horizon (years)",
        options=[5, 10, 15, 20, 25, 30],
        value=_initial['HORIZON_YEARS'],
    )
    mortgage_rate = st.slider(
        "Mortgage Rate (%)",
        min_value=3.0, max_value=12.0,
        value=_initial['MORTGAGE_RATE'], step=0.125,
        format="%.3f%%",
    )
    hoa_monthly = st.slider(
        "HOA (monthly)",
        min_value=0.0, max_value=2_500.0,
        value=_initial['HOA_MONTHLY'], step=25.0,
        format="$%.0f",
    )
    ho6_insurance_annual = st.slider(
        "HO-6 Insurance (annual)",
        min_value=500.0, max_value=6_000.0,
        value=_initial['HO6_INSURANCE_ANNUAL'], step=100.0,
        format="$%.0f",
    )
    property_tax_rate = st.slider(
        "Property Tax Rate (%)",
        min_value=0.5, max_value=3.0,
        value=_initial['PROPERTY_TAX_RATE'], step=0.05,
        format="%.2f%%",
    )
    market_rent = st.slider(
        "Market Rent (monthly)",
        min_value=500.0, max_value=6_000.0,
        value=_initial['MARKET_RENT'], step=50.0,
        format="$%.0f",
    )
    appreciation_rate = st.slider(
        "Home Appreciation (%/yr)",
        min_value=0.0, max_value=10.0,
        value=_initial['APPRECIATION_RATE'], step=0.25,
        format="%.2f%%",
    )
    investment_return_rate = st.slider(
        "Investment Return (%/yr)",
        min_value=0.0, max_value=15.0,
        value=_initial['INVESTMENT_RETURN_RATE'], step=0.25,
        format="%.2f%%",
    )
    closing_cost_pct = st.slider(
        "Closing Costs (%)",
        min_value=1.0, max_value=6.0,
        value=_initial['CLOSING_COST_PCT'], step=0.25,
        format="%.2f%%",
    )
    furniture_budget = st.slider(
        "Furniture & Improvements",
        min_value=0.0, max_value=50_000.0,
        value=_initial['FURNITURE_BUDGET'], step=500.0,
        format="$%.0f",
    )

    # ── Advanced Inputs ───────────────────────────────────────────────────────
    with st.expander("Advanced Inputs"):
        st.caption("Landlord scenario: used in the Rent Out exit path calculation")
        rental_income_monthly = st.slider(
            "Rental Income (monthly)",
            min_value=500.0, max_value=5_000.0,
            value=_initial['RENTAL_INCOME_MONTHLY'], step=50.0,
            format="$%.0f",
        )
        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            min_value=0.0, max_value=30.0,
            value=_initial['VACANCY_RATE'], step=1.0,
            format="%.1f%%",
        )
        property_mgmt_fee_pct = st.slider(
            "Property Mgmt Fee (%)",
            min_value=0.0, max_value=20.0,
            value=_initial['PROPERTY_MGMT_FEE_PCT'], step=1.0,
            format="%.1f%%",
        )

        st.caption("Realtor commission: applied to sale price in the Sell exit path")
        realtor_commission_pct = st.slider(
            "Realtor Commission (%)",
            min_value=0.0, max_value=8.0,
            value=_initial['REALTOR_COMMISSION_PCT'], step=0.25,
            format="%.2f%%",
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
    'APPRECIATION_RATE':         appreciation_rate,
    'INVESTMENT_RETURN_RATE':    investment_return_rate,
    'CLOSING_COST_PCT':          closing_cost_pct,
    'FURNITURE_BUDGET':          furniture_budget,
    'RENTAL_INCOME_MONTHLY':     rental_income_monthly,
    'VACANCY_RATE':              vacancy_rate,
    'PROPERTY_MGMT_FEE_PCT':     property_mgmt_fee_pct,
    'REALTOR_COMMISSION_PCT':    realtor_commission_pct,
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

except Exception:
    _calc_error = True

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

    st.markdown(_headline_card(winner, difference, horizon_years, break_even_text), unsafe_allow_html=True)

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
    ))
    fig.add_trace(go.Scatter(
        x=x_vals, y=buyer_series,
        name="Buy + Invest",
        mode="lines+markers",
        line=dict(color="#ED8936", width=2),
        marker=dict(size=5),
    ))

    if break_even_year is not None:
        fig.add_vline(
            x=break_even_year,
            line_dash="dash",
            line_color="#A0AEC0",
            annotation_text=f"Break-even: year {break_even_year}",
            annotation_position="top",
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
            "Rent + Invest": _fmt_dollar(r),
            "Buy + Invest": _fmt_dollar(b),
            "Difference": _fmt_dollar(diff),
            "Better": "Renting" if r >= b else "Buying",
        })

    st.subheader("Annual Wealth Breakdown")
    st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True)
