# Roadmap — NVIDIA DCF Valuation

## Current Status

**Phase 1 (Model Cleanup & Structure): Complete**
**Phase 2 (Comparable Analysis): Complete**
**Phase 3 (Investment Memo + Visuals): Complete**
**Phase 4 (Documentation & Repo Polish): Complete**

The repository is in a **fully functional, interview-ready state**.

---

## What Is Complete

### Model
- [x] L3 DCF Excel model — 23 tabs, fully linked formula chain
- [x] `00_Assumptions` — all model drivers in one place with rationale
- [x] Tabs renamed to 00–17 convention + metadata tabs
- [x] U-07: 170 text-formatted cells converted to numeric
- [x] U-14: 107 column headers standardized across all 20 sheets
- [x] U-10: 5 named ranges added to WACC sheet
- [x] U-13: Paste-as-values audit — formula chain confirmed intact
- [x] Exit Multiple terminal value (EV/EBITDA) added to `05b_DCF`
- [x] `06_Sensitivity` — two 9×9 WACC×g grids (implied price + EV)
- [x] `99_Validation` — BS tie, CF reconciliation, revenue cross-check, DCF snapshot

### Python Pipeline
- [x] `src/wacc.py` — WACC recalculation, 0.00 bps error vs. model
- [x] `src/comps.py` — 5-peer comps, 3 multiples, all stat levels
- [x] `run_all.py` — end-to-end pipeline orchestrator
- [x] `requirements.txt` — single dependency (openpyxl)

### Datasets
- [x] `datasets/raw/nvidia_historical_IS.csv` — FY2020–2025 (6 years, all gaps filled)
- [x] `datasets/raw/nvidia_historical_BS.csv` — FY2021–2025
- [x] `datasets/raw/nvidia_historical_CF.csv` — FY2022–2025
- [x] `datasets/raw/nvidia_market_data.csv` — 6 companies (NVDA + 5 peers)
- [x] `datasets/processed/cleaned_financials.csv` — 35 cols, derived ratios
- [x] `datasets/processed/wacc_results.json`
- [x] `datasets/processed/comps_results.json`

### Comps
- [x] `comps/comps_data.csv` — Phase B format, 17 fields, notes column
- [x] `comps/comps_methodology.md` — full peer selection and adjustment rationale

### Reports & Visuals
- [x] `reports/Investment_Memo_NVIDIA.pdf` — single-page professional memo
- [x] `reports/memo_template.md` — editable source
- [x] `screenshots/valuation_bridge.png` — EV→Equity + price range chart
- [ ] `screenshots/dcf_sensitivity.png` — **pending manual screenshot from Excel**

### Documentation
- [x] `README.md` — complete, up to date
- [x] `docs/architecture.md` — system design + data flow diagram
- [x] `docs/methodology.md` — modelling rules + normalization
- [x] `docs/valuation-framework.md` — DCF math + WACC breakdown
- [x] `docs/roadmap.md` — this file
- [x] `.gitignore` — Python + Excel patterns
- [x] `LICENSE` — MIT

---

## Remaining Manual Task

- [ ] `screenshots/dcf_sensitivity.png` — open `06_Sensitivity` in Excel,
  select the two WACC×g grids, screenshot, save as PNG. 5 minutes.

---

## Future Improvements (Post-Launch)

These are **not required** for the current state of the project.
Listed here for reference if the project is extended.

### Model Enhancements
- [ ] `models/templates/L3_Model_Template.xlsx` — strip NVIDIA-specific data;
  create reusable blank template for future case studies
- [ ] `08_Validation` — add FCFF cross-check (FCFF from CF vs. FCFF from FCFF sheet)
- [ ] Upside/downside scenario selector — toggle between base/bull/bear growth rates

### Python Automation
- [ ] `src/data_loader.py` — shared reader module to eliminate duplicated
  openpyxl load logic across `wacc.py`, `comps.py`, and `run_all.py`
- [ ] `tests/test_dcf.py` — automated numerical checks for key DCF outputs
- [ ] `src/export_sensitivity_png.py` — programmatic export of sensitivity
  table as PNG (using xlwings or matplotlib)

### Live Data (Optional)
- [ ] `src/data_refresh.py` — optional yfinance integration to pull current
  peer market data (price, market cap, shares) and update `comps_data.csv`
  Note: Requires `pip install yfinance`. Mark clearly as optional.

### Multi-Company Extension
The repo README describes an eventual "valuation engine" that could:
- [ ] Accept any ticker as input via `--ticker` flag
- [ ] Pull historical financials from a data provider
- [ ] Apply the same L3 DCF template to any company
- [ ] Generate a comparable memo PDF automatically

This is a significant extension and is deferred to a future version.

---

## Changelog

| Date | Change |
|------|--------|
| 2025-10 | Initial model built (NVIDIA FY2025 data) |
| 2026-03 | U-07: Text number fixes (170 cells) |
| 2026-03 | U-14: Column header standardization (107 headers) |
| 2026-03 | U-10: Named ranges + `src/wacc.py` built |
| 2026-03 | `src/comps.py` built and verified |
| 2026-03 | `run_all.py` pipeline orchestrator built |
| 2026-03 | Tab renaming (20 tabs → 00–17 convention) |
| 2026-03 | `00_Assumptions` sheet built |
| 2026-03 | Historical CSV export pipeline (all gaps filled) |
| 2026-03 | Exit Multiple TV added to `05b_DCF` |
| 2026-03 | `06_Sensitivity` WACC×g grids built |
| 2026-03 | `99_Validation` sheet built |
| 2026-03 | `reports/Investment_Memo_NVIDIA.pdf` generated |
| 2026-03 | `screenshots/valuation_bridge.png` generated |
| 2026-03 | Full documentation suite written |
| 2026-03 | **First clean push to GitHub** |
