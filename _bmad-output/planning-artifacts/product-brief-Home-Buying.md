---
title: "Product Brief: Miami Home Buying Decision Tool"
status: "complete"
created: "2026-04-28"
updated: "2026-04-28"
inputs: ["user discovery session", "web research — Miami housing market 2025-2026", "Florida homebuying cost data"]
---

# Product Brief: Miami Home Buying Decision Tool

## Executive Summary

Buying a first home is one of the most consequential financial decisions a person makes — and most people make it with dangerously incomplete information. Existing rent-vs-buy calculators are either too simplistic (single scenario, national averages) or too complex (10+ assumption sliders with no guidance). None of them model what actually matters for a first-time buyer in Miami: Florida-specific insurance costs, condo HOA fees that can rival a mortgage payment, PMI across multiple down payment tiers, and what happens at the 5-year mark when the decision to sell, rent out, or keep renting plays out.

The Miami Home Buying Decision Tool is a personal Streamlit application that gives one buyer — and eventually anyone in a similar position — a transparent, fully interactive financial model for the biggest decision of their financial life. It compares four down payment scenarios (5%, 10%, 15%, 20%) against market renting with the alternative capital invested in the market, and projects three distinct 5-year exit paths: sell the property, rent it out and become a landlord, or continue renting. Every assumption is a slider. Nothing is hidden.

Built for a first-time buyer targeting a ~$300K Miami condo while moving out of a family home, this tool turns an overwhelming decision into a clear financial picture.

---

## The Problem

A first-time buyer in Miami faces a uniquely hostile combination of costs that generic tools consistently understate:

- **Insurance crisis:** Florida homeowner's insurance averages $3,000–$5,000/year for a $300K condo — two to three times national averages — and is rising.
- **HOA shock:** Miami condo HOAs average $835–$965/month and are spiking further due to Florida's mandatory reserve funding law (post-Surfside). This can add more to monthly costs than the principal payment.
- **PMI complexity:** Down payments under 20% trigger PMI, adding $100–$266/month depending on the tier — and most tools don't break this out by scenario.
- **Hidden upfront costs:** Closing costs ($6,000–$15,000), furniture, and initial improvements add $10,000–$35,000 on top of the down payment, rarely modeled alongside it.
- **The opportunity cost blind spot:** Every dollar in a down payment is a dollar not compounding in the market. At a 7% annual return, the difference between a 5% and 20% down payment on a $300K home is $45,000 invested — $63,000+ after 5 years. Standard calculators ignore this entirely.

Today, a buyer faces this decision by piecing together a Bankrate mortgage calculator, a Zillow rental search, and a gut feeling. The result is a decision made on incomplete information, often with the wrong assumptions baked in.

---

## The Solution

A Streamlit web application with a clean, interactive dashboard that models the full financial picture across every meaningful scenario — side by side, in real time.

**Core experience:**

1. **Set your inputs once** — home price, mortgage rate, HOA, insurance, property tax, market rent, investment return rate, home appreciation rate, and furniture/improvement budget. Every input is a slider with sensible Miami-specific defaults.

2. **See all four down payment scenarios at a glance** — 5%, 10%, 15%, 20% shown side-by-side. Monthly cost breakdown for each: mortgage (P&I), PMI, HOA, property tax, insurance, and total vs. renting.

3. **Compare the three 5-year paths:**
   - **Buy → Sell:** Net equity after realtor fees (~5–6%) and seller costs vs. renter's investment portfolio
   - **Buy → Rent out:** User-input rental income minus vacancy, property management, and carrying costs vs. continued renting
   - **Rent + Invest:** Monthly savings invested at 7% annual return, accumulated over 5 years

4. **Net worth comparison at year 5** — the single most important output: which path leaves you wealthiest, under which assumptions? Liquid (portfolio) vs. illiquid (equity) clearly distinguished.

5. **Break-even output** — for each down payment scenario, a plain-language statement: *"At these assumptions, buying breaks even with renting + investing at month X."*

6. **Shareable URL** — all slider values encoded in the URL, so any scenario can be shared with a realtor, partner, or family member with a single link. No backend required.

**Key inputs (all dynamic sliders with Miami defaults):**

| Input | Default | Range |
|-------|---------|-------|
| Home price | $300,000 | $200K–$600K |
| Mortgage rate (fixed, 30-yr) | 6.5% | 4%–9% |
| HOA | $500/month | $0–$1,500 |
| Condo insurance (HO-6) | $1,200/year | $500–$3,000 |
| Property tax rate | 1.0% | 0.8%–1.5% |
| Market rent | $2,750/month | $1,500–$5,000 |
| Investment return | 7% | 3%–12% |
| Home appreciation | 3% | 0%–6% |
| Closing costs | 3.5% of price | 2%–5% |
| Furniture/improvements | $10,000 | $0–$30,000 |

> **Note on insurance:** For a condo, the HOA master policy covers the building exterior and structure. The buyer's personal HO-6 policy covers interior contents and liability only — typically $800–$2,000/year, significantly lower than a standalone home policy.

---

## What Makes This Different

**1. Multi-scenario, not single-scenario.** All four down payment tiers shown simultaneously — not one at a time. The user sees how PMI and opportunity cost interact across scenarios without re-entering data.

**2. Florida-specific defaults.** Pre-populated with Miami-Dade cost norms for insurance, property tax (with homestead exemption), and HOA ranges. Not national averages.

**3. Three exit paths, not one.** Every other tool assumes you either buy or rent forever. This tool models the landlord path — rental income, vacancy rate, and net cash flow — alongside the sell and continue-renting paths at year 5.

**4. Opportunity cost is front and center.** The renter's invested capital grows at the user's chosen return rate. This is displayed alongside equity accumulation — making the trade-off explicit rather than invisible.

**5. Transparent assumptions, no hidden bias.** No lender affiliation. Every number is user-controlled and shown. The tool does not advocate for buying or renting.

---

## Who This Serves

**Primary user: Cris** — a first-time buyer in Miami, FL, targeting a ~$300K condo, currently paying $1,000/month to family, planning to move out in early 2027. Financially literate but not a finance professional. Wants to make a confident, data-backed decision — not guess.

**Secondary users (future):** Friends, family, or colleagues in similar situations — first-time buyers in high-cost Florida markets who need a tool built for their reality, not a national average.

---

## Success Criteria

- The tool produces a clear net worth comparison at year 5 for all three paths across all four down payment scenarios
- Every major cost line item is modeled (mortgage, PMI, HOA, taxes, insurance, closing costs, furniture, seller costs)
- All key assumptions are adjustable via sliders with sensible Miami defaults
- The landlord path models rental income, vacancy, and property management cost
- A first-time user can reach a meaningful output within 5 minutes of opening the app
- Break-even month is clearly surfaced for each down payment scenario
- Any scenario can be shared via URL with no account required
- The tool supports a confident buy/rent/wait decision for the primary user before their target move-out date (early 2027)

---

## Scope

**In scope (v1):**
- 4 down payment scenarios: 5%, 10%, 15%, 20%
- Full monthly cost breakdown per scenario (mortgage, PMI, HOA, taxes, insurance)
- Upfront cost modeling: down payment + closing costs + furniture/improvements
- 5-year projection with configurable appreciation and investment return rates
- Three year-5 exit paths: sell, rent out, continue renting
- Net worth comparison across all paths at year 5
- PMI auto-calculation and automatic cancellation at 78% LTV
- Florida homestead exemption applied to property tax calculation
- Seller cost deduction from sale proceeds (~5–6% + transfer costs)
- Landlord scenario: user-set rental income, vacancy rate (default 7%), property management fee (default 10%) sliders
- PMI tracked via amortization schedule (loan balance), cancels automatically at 78% LTV per federal law
- Net worth output clearly distinguishes liquid assets (investment portfolio) vs. illiquid equity (home)
- Special assessment risk slider: one-time dollar amount + year it hits (for condo reserve funding scenarios)
- Break-even month output per down payment scenario
- URL-encoded state: all slider values serialized into the URL for shareable scenarios

**Not in scope (v1):**
- Tax optimization (mortgage interest deduction, depreciation on rental, capital gains on investments)
- Multi-property comparison
- Amortization schedule visualization
- Mobile-optimized UI
- User accounts or saved scenarios
- Cities outside Miami
- ARM (adjustable-rate mortgage) scenarios — v1 assumes a 30-year fixed rate

---

## Vision

The v1 tool solves one buyer's decision. If shared, it becomes a reference tool for anyone navigating the Miami housing market — a transparent, unbiased alternative to lender-sponsored calculators that use national averages and a single optimistic scenario.

In 2–3 years, this could expand to cover other high-cost Florida markets (Orlando, Tampa, Fort Lauderdale), add tax optimization modeling, and support a "when to buy" timeline view that factors in mortgage rate trends. With minimal infrastructure investment, a Streamlit app deployed to Streamlit Cloud becomes a shareable URL — no backend, no database, just a tool that tells the truth.
