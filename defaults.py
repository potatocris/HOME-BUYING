"""
Miami-specific default input values and last-reviewed date.

Isolated from calculation logic so defaults can be updated independently.
All percentage values stored as human-readable floats (6.5 = 6.5%, not 0.065)
so they feed directly into Streamlit sliders without conversion.
"""

# -- Property ------------------------------------------------------------------
HOME_PRICE = 300_000.0        # Miami condo target price (dollars)
APPRECIATION_RATE = 3.0       # Conservative Miami appreciation (% per year)
PROPERTY_TAX_RATE = 1.3       # Miami-Dade effective rate (% of value)
HOA_MONTHLY = 500.0           # Average HOA fee ($/month)
HO6_INSURANCE_ANNUAL = 1_200.0  # Florida HO-6 condo unit policy ($/year)

# -- Mortgage ------------------------------------------------------------------
MORTGAGE_RATE = 6.5           # 30-year fixed (% per year)
CLOSING_COST_PCT = 3.5        # FL avg: title, recording, lender fees (% of price)

# -- Renting / Opportunity Cost ------------------------------------------------
MARKET_RENT = 2_000.0         # Comparable Miami unit monthly rent ($/month)
INVESTMENT_RETURN_RATE = 7.0  # Long-run stock market return assumption (% per year)

# -- Upfront Costs -------------------------------------------------------------
FURNITURE_BUDGET = 15_000.0   # Furniture and improvements estimate (dollars)

# -- Scenario Inputs -----------------------------------------------------------
DOWN_PCT = 20.0           # Default down payment % for rent-vs-buy main page (conventional, no PMI)
HORIZON_YEARS = 10        # Default comparison horizon (years); Story 2.6 uses as timeline slider default

# -- Special Assessment --------------------------------------------------------
SPECIAL_ASSESSMENT_AMOUNT = 0.0  # Default: no assessment (dollars)
SPECIAL_ASSESSMENT_MONTH = 1   # Month the assessment lands (1-60)

# -- Landlord Scenario ---------------------------------------------------------
RENTAL_INCOME_MONTHLY = 2_000.0  # Expected gross rent if unit rented out ($/month)
VACANCY_RATE = 5.0             # Assumed vacancy (% of months)
PROPERTY_MGMT_FEE_PCT = 10.0   # Property manager cut of gross rent (%)

# -- Exit Costs ----------------------------------------------------------------
REALTOR_COMMISSION_PCT = 3.0   # Seller's agent + buyer's agent total (%)

# -- Metadata ------------------------------------------------------------------
DEFAULTS_LAST_UPDATED = "May 2026"  # Displayed in DisclaimerBanner (Story 3.2)
