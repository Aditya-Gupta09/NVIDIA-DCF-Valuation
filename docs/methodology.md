# Modelling Methodology — NVIDIA DCF Valuation

## Overview

This document defines the modelling rules, normalization conventions,
and data treatment decisions applied throughout the model. Every rule
here has a corresponding implementation in the Excel model and/or Python scripts.

---

## 1. Historical Period & Coverage

| Statement | Years Covered | Source |
|-----------|--------------|--------|
| Income Statement | FY2020–FY2025 (6 years) | NVIDIA 10-K (EDGAR) |
| Balance Sheet | FY2021–FY2025 (5 years) | NVIDIA 10-K |
| Cash Flow | FY2022–FY2025 (4 years; FY2022 summary only) | NVIDIA 10-K |

**Why FY2020 as the starting year:** FY2020 marks the pre-Data Center inflection point
and provides context for the margin expansion trajectory. The balance sheet
for FY2020 is not available in the model (pre-coverage) — this is documented
and does not affect valuation outputs.

**Fiscal year convention:** NVIDIA's fiscal year ends in late January.
FY2025 = February 2024 – January 2025.
All labels in the model use the fiscal year designation (not the calendar year).

---

## 2. Income Statement Normalization

### Non-Recurring Items

| Item | FY | Amount | Treatment |
|------|-----|--------|-----------|
| Acquisition termination cost (Arm) | FY2023 | $1,353M | **Included in model as reported** — excluded from projections |
| No other material one-offs identified | FY2020–2025 | — | No adjustments |

**Rule:** One-off items are **kept in historical reported figures** (no normalization)
to preserve comparability to reported filings. They are explicitly zeroed in
the projection period as non-recurring.

### Revenue Build
Revenue is projected **segment-by-segment** (5 segments), not as a single blended growth rate:
1. Data Center
2. Gaming
3. Professional Visualization
4. Automotive
5. OEM & Other

Each segment has base / upside / downside case growth rates defined in `00_Assumptions`
and `04a_Projection_IS`. The model uses the **base case** throughout.

### COGS and Gross Profit
COGS is modelled as a **gross margin percentage of revenue** derived from
the historical trend and applied in the projection period.
FY2025 gross margin: 75.0% — at a multi-year high driven by Data Center mix.
Projection assumes gradual normalization toward 72–74% by FY2030.

### Operating Expenses (R&D and SG&A)
Modelled as **percentage of revenue** with historical anchors:
- R&D: ~10% of revenue in FY2025; held at 9–10% through FY2030
- SG&A: ~2.7% in FY2025; modest decline through FY2030

### Interest Income
Modelled as:  `Average Cash Balance × Assumed Yield`
Cash held as % of revenue declines from 28% (FY2026F) to 21% (FY2030F).
Yield assumptions reflect declining rate environment.

### Tax Rate
- **Historical:** FY2025 actual ETR = 13.26% (low due to stock compensation deductions)
- **Projected:** Steps up to 15% (FY2026F) then gradually declining to 14%,
  reflecting Pillar Two global minimum tax implementation offset by R&D credits

---

## 3. FCFF Construction

```
EBIT (Operating Profit)
  × (1 – Effective Tax Rate)
= NOPAT  (Net Operating Profit After Tax)
  + Depreciation & Amortization
  – Capital Expenditures
  – Change in Net Working Capital
= Unlevered Free Cash Flow (FCFF)
```

**Key rules:**

- **EBIT is used, not EBITDA** — D&A is added back separately so the tax shield
  on depreciation is correctly captured via the NOPAT step
- **Operating taxes** = EBIT × ETR (not income taxes — avoids leverage effects)
- **CapEx** is modelled as % of revenue (3.0% FY2026F, declining to 2.8% FY2030F)
  based on NVIDIA's fabless model and historical range of 1.7%–6.8%
- **Change in NWC** = Change in (Receivables + Inventory + Prepaid) minus
  Change in (Payables + Accrued Liabilities). A positive NWC change is a cash use.

---

## 4. Net Working Capital (NWC) Calculation

```
NWC = (Receivables + Inventory + Prepaid Expenses)
    – (Accounts Payable + Accrued Liabilities)

Change in NWC (FY_t) = NWC(FY_t) – NWC(FY_{t-1})
```

**Included in NWC:**
- Current receivables
- Inventory
- Prepaid expenses

**Excluded from NWC:**
- Cash and short-term investments (financing item)
- Current portion of debt (financing item)
- Income taxes payable (tax item, not operational)

---

## 5. Capital Expenditure Rules

CapEx is gross capital spending on property, equipment, and leasehold improvements.
Lease payments are excluded (treated as financing).

**Historical CapEx/Revenue:**
| Year | CapEx | Revenue | CapEx % |
|------|-------|---------|---------|
| FY2022 | $976M | $26,914M | 3.6% |
| FY2023 | $1,833M | $26,974M | 6.8% |
| FY2024 | $1,069M | $60,922M | 1.8% |
| FY2025 | $3,236M | $130,497M | 2.5% |

**Projection:** 3.0% FY2026 → 2.8% FY2030 (NVIDIA is fabless; CapEx growth
lags revenue growth significantly).

---

## 6. Depreciation & Amortization

D&A is modelled via a **straight-line depreciation schedule** in `11_DA`:
- Average useful life: **5 years**
- Each year's CapEx vintage generates equal annual depreciation over 5 years
- Total D&A = sum of active CapEx vintages

FY2026F D&A: $3,046M → FY2030F D&A: $11,117M (growing with CapEx base)

---

## 7. Balance Sheet Modelling

The projected balance sheet (`04b_Projection_BS`) is driven by operational ratios:
- Receivables: Days Sales Outstanding applied to revenue
- Inventory: Days Inventory Outstanding applied to COGS
- Payables: Days Payable Outstanding applied to COGS
- Cash: modelled as % of revenue (declining over time)

**Balance sheet check (99_Validation):**
`Total Assets = Total Liabilities + Shareholders' Equity` must = 0 for all years.
Conditional red formatting flags any year where the tie fails.

---

## 8. CSV Normalization Rules

All historical CSVs exported from the model follow these conventions:

| Rule | Application |
|------|-------------|
| Currency | USD millions throughout |
| Sign convention | CapEx is **negative** in CF statement; positive in CapEx-specific fields |
| Missing data | `None` / blank — not zero. Zeros are genuine zeros. |
| Coverage gaps | Documented in `_note` column (CF FY2020–2021 absent) |
| Derived fields | `gross_profit = revenue − cogs` computed where missing in source sheet |
| Percentage fields | Stored as decimals (0.75, not 75%) |
| Year label | Integer fiscal year (2025, not "FY2025" or "FY 2025") |

---

## 9. What Is Not Modelled

| Item | Status | Reason |
|------|--------|--------|
| Minority interests | Not present | NVIDIA has no material minority interests |
| Preferred equity | Not present | No preferred stock outstanding |
| Options / warrants dilution | Simplified | Uses reported diluted share count from 10-K |
| Lease capitalization | Not adjusted | Leases treated as operating; immaterial at NVIDIA's scale |
| Revenue synergies | Not modelled | No pending acquisitions in forecast period |
| Scenario switching | Not automated | Base case only in pipeline; upside/downside rates defined in model |
