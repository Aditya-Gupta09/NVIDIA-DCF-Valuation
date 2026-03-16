# NVIDIA DCF Valuation — Deal Analysis & Valuation Engine

> **A complete L3 institutional-grade DCF valuation of NVIDIA Corporation (NVDA)**
> built as a reproducible, interview-ready financial modelling package.

---

## What Is This?

A structured valuation framework built around a **cleaned L3 DCF Excel model** (FY2020–FY2030),
supported by Python automation for WACC recalculation, comparable company analysis,
and dataset export. The output is a defensible, reproducible valuation with a one-page
investment memo and full documentation.

**Valuation conclusion:** Implied intrinsic price **$109.26** vs. market price $183.22 on
October 17, 2025 → **Hold** (−40.0% downside on Gordon Growth basis).

---

## What Is Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| `models/Company_Valuation_Model.xlsx` | ✅ Complete | 23-tab L3 DCF model — IS, BS, CF, projections, WACC, FCFF, DCF, sensitivity, comps, validation |
| `src/wacc.py` | ✅ Complete | Reads WACC inputs via named ranges; independently recalculates WACC (0.00 bps error vs. model) |
| `src/comps.py` | ✅ Complete | Comparable company analysis — 5 peers, 3 multiples, implied prices at 6 statistic levels |
| `run_all.py` | ✅ Complete | End-to-end pipeline — validates model, runs WACC, runs comps, exports all datasets |
| `comps/comps_data.csv` | ✅ Complete | Structured peer table in Phase B format — 17 fields, tickers, LTM multiples, notes |
| `comps/comps_methodology.md` | ✅ Complete | Peer selection rationale, data sources, adjustment policy, implied valuation workings |
| `datasets/raw/` | ✅ Complete | Historical IS/BS/CF CSVs (FY2020–2025) + peer market data |
| `datasets/processed/` | ✅ Complete | `cleaned_financials.csv` (35 cols), `wacc_results.json`, `comps_results.json` |
| `reports/Investment_Memo_NVIDIA.pdf` | ✅ Complete | One-page interview-ready investment memo |
| `reports/memo_template.md` | ✅ Complete | Editable source for the memo |
| `screenshots/valuation_bridge.png` | ✅ Complete | EV→Equity bridge + implied price range chart |
| `docs/` | ✅ Complete | Architecture, methodology, valuation framework, roadmap |

---

## Repository Structure

```
NVIDIA-DCF-Valuation/
│
├── README.md
├── LICENSE                         MIT
├── .gitignore
├── requirements.txt                openpyxl only
├── run_all.py                      ← entry point: runs entire pipeline
│
├── models/
│   └── Company_Valuation_Model.xlsx   ← L3 DCF model (23 tabs)
│
├── src/
│   ├── wacc.py                     WACC extraction + independent recalculation
│   └── comps.py                    Comparable company analysis
│
├── comps/
│   ├── comps_data.csv              Peer table — Phase B format
│   └── comps_methodology.md        Selection rationale + adjustment policy
│
├── datasets/
│   ├── raw/
│   │   ├── nvidia_historical_IS.csv     FY2020–2025 income statement
│   │   ├── nvidia_historical_BS.csv     FY2021–2025 balance sheet
│   │   ├── nvidia_historical_CF.csv     FY2022–2025 cash flow statement
│   │   └── nvidia_market_data.csv       Peer company data (Oct 17, 2025)
│   └── processed/
│       ├── cleaned_financials.csv       Normalized — 35 cols, 6 years
│       ├── wacc_results.json            WACC outputs + cross-check
│       ├── comps_results.json           Comps outputs — all stat levels
│       └── pipeline_summary.json        Full pipeline run log
│
├── reports/
│   ├── Investment_Memo_NVIDIA.pdf       One-page investment memo
│   └── memo_template.md                 Editable memo source
│
├── screenshots/
│   ├── valuation_bridge.png             EV→Equity bridge + price range chart
│   └── dcf_sensitivity.png              WACC×g sensitivity table (Excel screenshot)
│
└── docs/
    ├── architecture.md                  System design + data flow
    ├── methodology.md                   Modelling rules + normalization
    ├── valuation-framework.md           DCF math + WACC breakdown
    └── roadmap.md                       Milestones + future work
```

---

## How to Inspect (No Code Required)

1. Open `models/Company_Valuation_Model.xlsx`
2. Start at **`00_Assumptions`** tab — all model inputs with rationale
3. Follow the chain: `15_WACC` → `05a_FCFF` → `05b_DCF`
4. Implied share price is at **`05b_DCF!C21`** (Gordon Growth) and **`05b_DCF!C51`** (Exit Multiple)
5. See `06_Sensitivity` for the full WACC×g grid
6. See `99_Validation` for balance sheet tie and cash flow reconciliation checks

---

## How to Reproduce (Python Pipeline)

```bash
# 1. Clone the repo
git clone https://github.com/Aditya-Gupta09/NVIDIA-DCF-Valuation.git
cd NVIDIA-DCF-Valuation

# 2. Install the single dependency
pip install -r requirements.txt

# 3. Open the model in Excel and recalculate
#    File: models/Company_Valuation_Model.xlsx
#    Press Ctrl+Alt+F9 → Save
#    (Required once to cache formula values for Python to read)

# 4. Run the full pipeline
python run_all.py

# Optional flags
python run_all.py --verbose          # detailed output
python run_all.py --skip-export      # skip CSV re-export, use existing
python run_all.py --model path/to/model.xlsx  # custom model path
```

**Pipeline output (9 files):**
```
datasets/processed/wacc_results.json
datasets/processed/comps_results.json
datasets/processed/pipeline_summary.json
datasets/raw/nvidia_historical_IS.csv
datasets/raw/nvidia_historical_BS.csv
datasets/raw/nvidia_historical_CF.csv
datasets/raw/nvidia_market_data.csv
datasets/processed/cleaned_financials.csv
comps/comps_data.csv
```

---

## Data Sources & Attribution

All data is **static as of October 17, 2025** and committed under `datasets/raw/`.
No runtime internet connection is required.

| Data | Source | File |
|------|--------|------|
| NVIDIA historical financials | NVIDIA 10-K FY2020–FY2025 (EDGAR) | `datasets/raw/nvidia_historical_IS/BS/CF.csv` |
| Peer company market data | Yahoo Finance (Oct 17, 2025) | `datasets/raw/nvidia_market_data.csv` |
| Beta | 60-month regression vs. S&P 500 (Yahoo Finance) | `14_Beta` sheet |
| Risk-free rate | US 10Y Treasury, Oct 17, 2025 | `00_Assumptions` |
| Equity risk premium | Damodaran implied ERP, January 2025 | `00_Assumptions` |

---

## Key Model Outputs

| Output | Value |
|--------|-------|
| WACC | 12.91% |
| Terminal Growth Rate | 4.00% |
| Sum of PV FCFs | $664,085M |
| PV of Terminal Value | $1,958,098M |
| Enterprise Value | $2,622,182M |
| Net Cash | +$32,940M |
| Equity Value | $2,655,122M |
| **Implied Price (Gordon Growth)** | **$109.26** |
| Market Price (Oct 17, 2025) | $183.22 |
| **Upside / Downside** | **−40.3%** |
| Comps — EV/EBITDA implied | $91.54 |
| Comps — P/E implied | $208.50 |

---

## Disclaimer

This project is for **educational and demonstrative purposes only**.
It is not investment advice. All projections and valuations are the author's own
and should not be used as the basis for any investment decision.

---

*Primary author: Aditya Gupta*
