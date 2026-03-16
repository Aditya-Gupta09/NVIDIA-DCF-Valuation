# Architecture — NVIDIA DCF Valuation

## System Overview

This is a **research-grade valuation repository**. The Excel model is the
primary instrument; Python scripts are supporting computational validators
and dataset exporters. There is no live data pipeline — all inputs are static
as of the valuation date (October 17, 2025).

---

## Repository Type

```
Type:     Static research package (not a production API)
Primary:  Excel L3 DCF model
Support:  Python — WACC recalculation, comps analysis, CSV export
Data:     Committed CSVs (no runtime internet dependency)
Output:   JSON results + cleaned CSVs + investment memo PDF
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                COMPANY_VALUATION_MODEL.XLSX                  │
│  (23 tabs — IS, BS, CF, Projections, WACC, FCFF, DCF,       │
│   Sensitivity, Comps, Validation, Assumptions)               │
└────────┬───────────────────┬────────────────────────────────┘
         │                   │
         ▼ Path A             ▼ Path B
┌─────────────────┐   ┌──────────────────────────┐
│  15_WACC sheet  │   │  17_ComparableAnalysis   │
│  F7:F19 (named  │   │  rows 6–11               │
│  ranges)        │   │  (peer market data)       │
└────────┬────────┘   └──────────┬───────────────┘
         │                       │
         ▼                       ▼
┌────────────────┐   ┌──────────────────────────┐
│  src/wacc.py   │   │  src/comps.py            │
│  • Named range │   │  • EV/Revenue            │
│    reads       │   │  • EV/EBITDA             │
│  • CAPM reCalc │   │  • P/E                   │
│  • Cross-check │   │  • Implied prices        │
└────────┬───────┘   └──────────┬───────────────┘
         │                       │
         ▼                       ▼
┌────────────────────────────────────────────────┐
│          datasets/processed/                    │
│  wacc_results.json                             │
│  comps_results.json                            │
│  pipeline_summary.json                         │
└────────────────────────────────────────────────┘

         Path C (Historical Export)
┌─────────────────────────────────────────────────┐
│  01_Historical_IS / 02_Historical_BS            │
│  03_Historical_CF                               │
└────────┬────────────────────────────────────────┘
         │ run_all.py → Step 4 (export)
         ▼
┌────────────────────────────────────────────────┐
│          datasets/raw/                          │
│  nvidia_historical_IS.csv  (FY2020–2025)       │
│  nvidia_historical_BS.csv  (FY2021–2025)       │
│  nvidia_historical_CF.csv  (FY2022–2025)       │
│  nvidia_market_data.csv    (6 companies)       │
└────────┬────────────────────────────────────────┘
         │ normalization
         ▼
┌────────────────────────────────────────────────┐
│  datasets/processed/cleaned_financials.csv      │
│  (35 cols, 6 years, derived ratios)             │
└────────────────────────────────────────────────┘
```

---

## Excel Model — Tab Structure

| Tab | Type | Description |
|-----|------|-------------|
| `00_Assumptions` | Input | All model drivers — WACC inputs, growth rates, margins, CapEx |
| `01_Historical_IS` | Historical | Income statement FY2020–2025 |
| `02_Historical_BS` | Historical | Balance sheet FY2021–2025 |
| `03_Historical_CF` | Historical | Cash flow statement FY2022–2025 |
| `04a_Projection_IS` | Forecast | Revenue build (5 segments) + IS projection |
| `04b_Projection_BS` | Forecast | Balance sheet modelling FY2026–2030 |
| `04c_Projection_CF` | Forecast | Cash flow projection |
| `05a_FCFF` | Valuation | FCFF schedule — EBIT → NOPAT → FCFF |
| `05b_DCF` | Valuation | Gordon Growth TV + Exit Multiple TV + sensitivity grids |
| `06_Sensitivity` | Analysis | WACC×g grids — Implied Price + EV (9×9 each) |
| `07_CommonSize` | Analysis | Common-size income statement |
| `08_RatioAnalysis` | Analysis | Growth, profitability, solvency ratios |
| `09_WorkingCapital` | Supporting | NWC schedule |
| `10_GrowthRates` | Supporting | Historical revenue growth by segment |
| `11_DA` | Supporting | D&A schedule (straight-line, 5-year useful life) |
| `12_FixedAssets` | Supporting | CapEx schedule + fixed asset roll-forward |
| `13_DebtSchedule` | Supporting | Debt roll-forward |
| `14_Beta` | WACC input | Beta regression (60M weekly vs. S&P 500) |
| `15_WACC` | WACC | WACC calculation with named ranges |
| `16_MarketData` | Reference | 52-week high/low + market statistics |
| `17_ComparableAnalysis` | Comps | 5-peer comps table with multiples |
| `98_Notes` | Metadata | Version, author, data sources |
| `99_Validation` | Checks | BS tie, CF recon, revenue cross-check, DCF snapshot |

---

## Named Ranges (WACC Sheet)

Five named ranges enable row-shift-resilient Python reads:

| Name | Cell | Value |
|------|------|-------|
| `risk_free_rate` | `15_WACC!$F$10` | 4.07% |
| `adjusted_beta` | `15_WACC!$F$11` | 1.7728 (formula `=Beta!L13`) |
| `equity_risk_premium` | `15_WACC!$F$12` | 5.00% |
| `effective_tax_rate` | `15_WACC!$F$17` | 13.26% (formula `=IS_modelling!F71`) |
| `wacc_output` | `15_WACC!$F$19` | 12.91% (formula `=F8*F9+F15*F16*(1-F17)`) |

---

## Python Modules

### `src/wacc.py`
- Reads 5 named ranges from WACC sheet
- Reads 5 address-based inputs (market cap, debt weights, cost of debt)
- Independently recalculates WACC via CAPM formula
- Cross-checks result against model output (tolerance: 1 basis point)
- Writes `datasets/processed/wacc_results.json`

### `src/comps.py`
- Reads peer data from `17_ComparableAnalysis` rows 6–11
- Calculates EV/Revenue, EV/EBITDA, P/E per peer
- Computes 6-level statistics (high, P75, mean, median, P25, low)
- Derives NVIDIA implied prices at each level via EV bridge
- Writes `datasets/processed/comps_results.json`

### `run_all.py`
- Step 1: Model validation (tabs, named ranges, DCF output cell)
- Step 2: WACC recalculation
- Step 3: Comparable analysis
- Step 4: Dataset export (5 CSVs)
- Step 5: `comps/comps_data.csv` in Phase B format
- Writes `datasets/processed/pipeline_summary.json`

---

## Known Coverage Gaps

| Statement | Coverage | Reason |
|-----------|----------|--------|
| BS FY2020 | Absent | Pre-model period; not in any source sheet |
| CF FY2020–2021 | Absent | Detailed CF not in model for these years |
| CF FY2022 | Partial (summary) | Secondary section — CFO/CFI/CFF/CapEx only |

These gaps are documented in `datasets/raw/nvidia_historical_CF.csv`
via the `_note` column and do not affect the DCF (which uses projected FCFs).

---

## Dependency Map

```
run_all.py
    └── openpyxl (read model)
    └── src/wacc.py
    └── src/comps.py
    └── csv (stdlib)
    └── json (stdlib)

requirements.txt: openpyxl>=3.1.0  (only external dependency)
```
