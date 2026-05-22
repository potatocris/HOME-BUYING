---
title: "Product Brief Distillate: Miami Home Buying Decision Tool"
type: llm-distillate
source: "product-brief-Home-Buying.md"
created: "2026-04-28"
purpose: "Token-efficient context for downstream PRD creation"
---

# Product Brief Distillate: Miami Home Buying Decision Tool

## Primary User Context

- **User:** Cris, Miami FL, first-time buyer, intermediate financial literacy
- **Current housing:** Paying $1,000/month to parents — this is NOT a market-rate rent; do not use as a comparison baseline
- **Market rent baseline for comparison:** $2,500–$3,000/month (Miami 1–2BR condo)
- **Target property:** ~$300K condo in Miami-Dade County
- **Timeline:** Moving out early 2027; tool must be ready well before that date
- **Use case:** Personal decision support first; open to sharing with friends/family later but not a launch priority

---

## Financial Model — Inputs & Defaults

### Dynamic Sliders (all user-adjustable)

| Input | Default | Range | Notes |
|-------|---------|-------|-------|
| Home price | $300,000 | $200K–$600K | |
| Mortgage rate | 6.5% | 4%–9% | Fixed 30-year only in v1; ARM explicitly out of scope |
| Down payment | 5/10/15/20% | — | Four discrete scenarios, shown simultaneously |
| HOA | $500/month | $0–$1,500 | Miami condo avg $835–$965; user chose $500 as conservative default |
| Condo insurance (HO-6) | $1,200/year | $500–$3,000 | HO-6 only — HOA master policy covers building exterior; do NOT use full homeowner's insurance range ($3K–$5K) for condo |
| Property tax rate | 1.0% | 0.8%–1.5% | Miami-Dade effective rate; apply Florida Homestead Exemption ($50K reduction on assessed value) |
| Market rent | $2,750/month | $1,500–$5,000 | Used for rent comparison path AND as reference for landlord rental income |
| Rental income (landlord path) | User-input | — | Manually entered; NOT auto-derived from market rent slider |
| Investment return | 7% | 3%–12% | S&P 500 historical average; user confirmed this assumption |
| Home appreciation | 3% | 0%–6% | User confirmed; market projects ~3.4% — conservative is fine |
| Closing costs | 3.5% of price | 2%–5% | Florida-specific line items: doc stamps (0.35% of loan), intangible tax (0.2% of loan), owner's title insurance (~$1,500–$2,500) |
| Furniture/improvements | $10,000 | $0–$30,000 | One-time upfront; industry range $5K–$20K for first-time buyers |
| Special assessment (condo) | $0 | $0–$50,000 | One-time cost; user also sets which year (1–5) it hits; models post-Surfside reserve funding risk |
| Vacancy rate (landlord) | 7% | 0%–20% | Applied to rental income in landlord path |
| Property mgmt fee (landlord) | 10% | 0%–15% | % of gross rental income; optional (user may self-manage) |
| Seller costs | 5.5% of sale price | 4%–7% | Realtor commission + Florida transfer costs; deducted from sale proceeds in Buy→Sell path |

### PMI by Down Payment Scenario (auto-calculated, not a slider)

| Down Payment | Approx PMI Rate | Monthly PMI on $300K home |
|---|---|---|
| 5% ($15K down, $285K loan) | 0.85%–1.28%/yr | ~$202–$304/month |
| 10% ($30K down, $270K loan) | 0.49%–0.65%/yr | ~$110–$146/month |
| 15% ($45K down, $255K loan) | 0.30%–0.50%/yr | ~$64–$106/month |
| 20% ($60K down) | None | $0 |

- PMI must be calculated via amortization schedule tracking outstanding loan balance — NOT via appreciation alone
- PMI cancels automatically at 78% LTV per federal law (Homeowners Protection Act)
- PMI cancellation year varies by scenario and should be surfaced in the output

---

## Financial Model — Scenarios & Outputs

### Three Paths Modeled Over 5 Years

**Path A: Buy → Sell at Year 5**
- Track monthly: mortgage P&I, PMI (until 78% LTV), HOA, property tax, HO-6 insurance, maintenance (optional slider or fixed %)
- Year 5 sale: home value after 3% annual appreciation → deduct seller costs (5.5% default) → net proceeds
- Net worth = home sale proceeds + any remaining cash savings
- Compare vs. renter's investment portfolio at year 5

**Path B: Buy → Rent Out at Year 5**
- Same monthly costs as Path A for years 1–5
- At year 5: user inputs target rental income; model deducts vacancy (default 7%) + property mgmt (default 10%) + continuing carrying costs (HOA, tax, insurance, mortgage)
- Show: monthly net cash flow from rental; equity position; total net worth
- Note: model does not address mortgage refinance to rental terms — out of scope for v1

**Path C: Rent + Invest**
- Monthly rent = market rent slider ($2,750 default)
- Down payment amount (per scenario) invested at t=0 at 7% annual return
- Monthly delta between buying costs and renting costs also invested (positive delta = extra invested; negative = would reduce portfolio)
- Net worth at year 5 = investment portfolio value (liquid)

### Key Outputs Required

- **Side-by-side monthly cost breakdown** for all 4 down payment scenarios (mortgage, PMI, HOA, tax, insurance, total)
- **Upfront cost summary** per scenario (down payment + closing costs + furniture = total cash needed at close)
- **Net worth at year 5** across all three paths — must clearly label liquid (portfolio) vs. illiquid (equity)
- **Break-even month** per down payment scenario: the month at which buying overtakes renting+investing in net worth terms
- **PMI cancellation year** per scenario

---

## Technical Decisions & Preferences

- **Platform:** Streamlit (confirmed preferred over Excel due to dynamic interactivity, sliders, side-by-side display)
- **Deployment:** Streamlit Community Cloud (free, no backend, shareable URL)
- **URL state encoding:** All slider values serialized into URL query params so any scenario is shareable via link — v1 requirement
- **Language:** Python (Streamlit standard)
- **No user accounts, no database, no authentication** — purely stateless client-side tool
- **No mobile optimization** in v1 — desktop browser only
- **ARM mortgages:** Explicitly out of scope for v1 — fixed 30-year only

---

## Florida / Miami-Specific Facts to Preserve

- Miami-Dade effective property tax rate: ~1.0%–1.02% of assessed value
- Florida Homestead Exemption: $50,000 reduction on assessed value for primary residence; Save Our Homes cap limits annual assessment increases to 3% for homesteaded properties
- On $300K home: expect ~$2,500–$3,000/year property tax after exemption in year 1
- HO-6 condo insurance (interior only): $800–$2,000/year — building exterior covered by HOA master policy
- Florida SB 4-D (2022): requires condo associations to fully fund structural reserves by end of 2024/2025 phase-in; driving special assessments and HOA fee increases in aging Miami buildings — this is the primary justification for the special assessment slider
- Florida has no state income tax — mortgage interest deduction is federal only; less impactful than in high-tax states (PRD should NOT overstate tax benefit of homeownership)
- Miami rental market: among highest-demand in US (RentCafe #1 in 2024); $2,500–$3,000/month for 1–2BR condo is well-supported by current data
- Miami-Dade median home price: ~$674K as of early 2026 — $300K is entry-level/condo segment, meaningfully undersupplied
- Mortgage rates (2026): 6.0%–6.6% for 30-year fixed, conventional loan, good credit; model default of 6.5% is appropriate
- Seller concessions in current buyer's market: 2%–3% not uncommon — could be an optional toggle in v2

---

## Competitive Intelligence (What to Avoid Replicating)

| Tool | Core Gap |
|------|----------|
| NerdWallet | Single scenario; national insurance defaults; no exit path modeling |
| Bankrate | Binary buy/rent; no PMI by tier; no opportunity cost |
| NYT Calculator | Gold standard for sophistication but overwhelming for first-timers; no exit paths |
| Zillow | Extremely simplified; omits PMI, HOA, closing costs entirely |
| SmartAsset | Location estimates understate Miami insurance; no exit branching |
| Excel (DIY) | Transparent but requires financial expertise; not pre-configured for FL |

**Differentiation to emphasize in PRD:**
- Only tool modeling all 4 down payment scenarios simultaneously
- Only tool with 3 exit paths (sell / rent out / continue renting)
- Only tool with Florida-specific defaults (HO-6 insurance, Miami-Dade tax, HOA ranges)
- Only tool surfacing break-even month as a primary output
- Only tool with URL-shareable scenarios and no lender affiliation

---

## Rejected / Deferred Ideas (Do Not Re-Propose for v1)

- **ARM mortgage scenarios** — explicitly out of scope; adds complexity, fixed-rate sufficient for decision
- **Tax optimization** (mortgage interest deduction, rental depreciation, capital gains on investments) — too complex for v1; user acknowledged; note tax treatment is pre-tax throughout
- **Multi-property comparison** — not needed for this use case
- **Amortization schedule visualization** — nice-to-have but not a core output; consider v2
- **Mobile-optimized UI** — personal/desktop tool; not a priority
- **User accounts / saved scenarios** — URL encoding handles sharing; no auth needed
- **Other Florida cities** — v2+ if tool is shared publicly
- **Automatic rental income derivation from market rent** — user explicitly chose manual input for the landlord path
- **Capital gains tax on investment portfolio** — acknowledged by user; excluded for simplicity; PRD should note this means the rent+invest path is slightly overstated in net worth terms

---

## Open Questions / Assumptions to Validate in PRD

- **Maintenance cost:** Not yet specified as a line item. Industry rule of thumb is 1%–2% of home value/year (~$3,000–$6,000/year on $300K). Should this be a fixed default, a slider, or excluded?
- **HOA trend:** Should the model assume HOA increases at a fixed % per year (e.g., 3–5% annual increase) or hold it flat? Miami HOAs are rising materially due to reserve funding mandates.
- **Rent growth rate:** Should market rent increase annually in the model (e.g., 2–3%/year) or stay flat? Flat rent understates the cost of the renting path over time.
- **Investment compounding frequency:** Annual vs. monthly compounding on the 7% return — monthly is more accurate for dollar-cost averaging; clarify in PRD.
- **Landlord: does the owner need to move out?** If the user buys and then rents out at year 5, they need a new place to live. Should the model account for the cost of their new rent? This could materially change the landlord path economics.
- **Special assessment:** Should it be modeled as a lump sum paid out-of-pocket, or financed (added to loan)? Both scenarios are possible in practice.
