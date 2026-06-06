"""
Miami-specific default input values and last-reviewed date.

Isolated from calculation logic so defaults can be updated independently.
All percentage values stored as human-readable floats (6.5 = 6.5%, not 0.065)
so they feed directly into Streamlit sliders without conversion.
"""

# -- Property ------------------------------------------------------------------
HOME_PRICE = 350_000.0        # Miami condo target price (dollars)
APPRECIATION_RATE = 3.0       # Conservative Miami appreciation (% per year)
PROPERTY_TAX_RATE = 1.3       # Miami-Dade effective rate (% of value)
HOA_MONTHLY = 500.0           # Average HOA fee ($/month)
HO6_INSURANCE_ANNUAL = 1_200.0  # Florida HO-6 condo unit policy ($/year)

# -- Mortgage ------------------------------------------------------------------
MORTGAGE_RATE = 6.5           # 30-year fixed (% per year)
CLOSING_COST_PCT = 3.5        # FL avg: title, recording, lender fees (% of price)

# -- Renting / Opportunity Cost ------------------------------------------------
MARKET_RENT = 3_000.0         # risonrable Miami unit monthly rent ($/month)
RENT_GROWTH_RATE = 3.0        # Assumed annual rent increase (% per year)
INVESTMENT_RETURN_RATE = 7.0  # Long-run stock market return assumption (% per year)

# -- Income / Budget (shared across rent & buy) --------------------------------
MONTHLY_BUDGET = 3_500.0      # Monthly income allocated to housing + investing ($/month)
# Income grows annually at RENT_GROWTH_RATE + 0.25 (derived in app.py; no separate slider)

# -- Cost Escalation -----------------------------------------------------------
COST_GROWTH_RATE = 3.0        # Annual growth for HOA, HO-6 insurance, and tax assessed value (%/yr)

# -- Upfront Costs -------------------------------------------------------------
FURNITURE_BUDGET = 15_000.0   # Furniture and improvements estimate (dollars)

# -- Scenario Inputs -----------------------------------------------------------
DOWN_PCT = 20.0           # Default down payment % for rent-vs-buy main page (conventional, no PMI)
HORIZON_YEARS = 30        # Default comparison horizon (years); Story 2.6 uses as timeline slider default

# -- Landlord Scenario ---------------------------------------------------------
RENTAL_INCOME_MONTHLY = 2_000.0  # Expected gross rent if unit rented out ($/month)
VACANCY_RATE = 5.0             # Assumed vacancy (% of months)
PROPERTY_MGMT_FEE_PCT = 10.0   # Property manager cut of gross rent (%)

# -- Exit Costs ----------------------------------------------------------------
REALTOR_COMMISSION_PCT = 3.0   # Seller's agent + buyer's agent total (%)

# -- Metadata ------------------------------------------------------------------
DEFAULTS_LAST_UPDATED = "June 2026"  # Displayed in DisclaimerBanner (Story 3.2)
