# Manual Test Checks — NVIDIA DCF Valuation

Run these checks after every model change and after every `python run_all.py` execution.
All checks are implemented in `99_Validation` sheet with conditional red/green formatting.

---

## How to Run

**Excel checks (99_Validation sheet):**
1. Open `models/Company_Valuation_Model.xlsx`
2. Press `Ctrl+Alt+F9` to force full recalculation
3. Navigate to `99_Validation` tab
4. All "Difference" rows should show **green (0.00)**
5. Any red cell = model integrity issue — investigate before pushing

**Python checks:**
```bash
python run_all.py --verbose
```
All steps should complete with ✓. Any ⚠ warning should be investigated.

---

## Check 1 — Balance Sheet Tie

**What it checks:** Total Assets = Total Liabilities + Shareholders' Equity for each year

| Year | Total Assets | Liabilities + Equity | Difference | Expected |
|------|-------------|---------------------|------------|---------|
| 2021 | $28,791M | $28,791M | **0** | ✓ |
| 2022 | $44,187M | $44,187M | **0** | ✓ |
| 2023 | $41,182M | $41,182M | **0** | ✓ |
| 2024 | $65,728M | $65,728M | **0** | ✓ |
| 2025 | $111,601M | $111,601M | **0** | ✓ |

**Formula:** `=Total_Assets − (Total_Liabilities + Shareholders_Equity)`
**Location:** `99_Validation` rows 8–10 | `02_Historical_BS` row 40 (existing check)
**Tolerance:** |difference| ≤ $0.01M (rounding)

---

## Check 2 — Cash Flow Reconciliation

**What it checks:** CFO + CFI + CFF = Net Change in Cash per CF statement

| Year | CFO | CFI | CFF | Sum | Net Cash Change | Difference | Expected |
|------|-----|-----|-----|-----|----------------|------------|---------|
| 2023 | $5,641M | $7,375M | $(11,617M) | $1,399M | $1,399M | **0** | ✓ |
| 2024 | $28,090M | $(10,566M) | $(13,633M) | $3,891M | $3,891M | **0** | ✓ |
| 2025 | $64,089M | $(20,421M) | $(42,359M) | $1,309M | $1,309M | **0** | ✓ |

**Formula:** `=(CFO + CFI + CFF) − Net_Change_in_Cash`
**Location:** `99_Validation` rows 17–23
**Tolerance:** |difference| ≤ $0.01M

---

## Check 3 — Revenue Cross-Check

**What it checks:** Revenue in `01_Historical_IS` matches revenue in `05a_FCFF` (which pulls from projection IS)

| Year | IS Revenue | FCFF Revenue | Difference | Expected |
|------|-----------|-------------|------------|---------|
| 2023 | $26,974M | $26,974M | **0** | ✓ |
| 2024 | $60,922M | $60,922M | **0** | ✓ |
| 2025 | $130,497M | $130,497M | **0** | ✓ |

**Formula:** `=IS_Revenue − FCFF_Revenue`
**Location:** `99_Validation` rows 26–29

---

## Check 4 — WACC Cross-Check (Python)

**What it checks:** Python-recalculated WACC matches model WACC within 1 basis point

```bash
python run_all.py 2>&1 | grep "Cross-check"
# Expected output: ✓ Cross-check: PASS (0.00 bps difference)
```

| Input | Python Value | Model Value | Match |
|-------|-------------|-------------|-------|
| WACC | 12.9141% | 12.9142% | ✓ |
| Cost of Equity | 12.934% | 12.934% | ✓ |
| After-tax CoD | 2.455% | 2.455% | ✓ |

---

## Check 5 — DCF Output Snapshot

After Ctrl+Alt+F9, verify these cells in `05b_DCF`:

| Cell | Label | Expected Value | Tolerance |
|------|-------|---------------|-----------|
| C13 | Terminal Growth (g) | 4.00% | Exact |
| C20 | Diluted Shares | 24,300 | Exact |
| C21 | Implied Share Price | ~$109.26 | ±$0.01 |
| C11 | Sum PV FCFs | ~$664,085M | ±$1M |
| C17 | Enterprise Value | ~$2,622,182M | ±$1M |
| C19 | Equity Value | ~$2,655,122M | ±$1M |

---

## Check 6 — Comps Implied Prices (Python)

```bash
python run_all.py 2>&1 | grep "implied"
```

Expected output:
```
✓  Median EV/Revenue:  9.8x  → implied $68.05
✓  Median EV/EBITDA:   22.3x → implied $91.54
✓  Median P/E:         59.4x → implied $208.5
```

| Multiple | Peer Median | Implied Price | Expected |
|----------|------------|--------------|---------|
| EV/Revenue | 9.8x | $68.05 | ✓ |
| EV/EBITDA | 22.3x | $91.54 | ✓ |
| P/E | 59.4x | $208.50 | ✓ |

---

## Failure Response Protocol

If any check fails:

1. **BS tie fails:** Check if a row was accidentally added/deleted in BS modelling sheets.
   Verify `04b_Projection_BS` formula integrity.

2. **CF reconciliation fails:** Check if `03_Historical_CF` rows 19/29/38/39
   are still formula-driven. Run `python run_all.py` to re-export.

3. **WACC cross-check fails (>1 bps):** Open model in Excel, Ctrl+Alt+F9, Save,
   then re-run pipeline. If still failing, check `15_WACC!F19` formula integrity.

4. **Implied share price changes unexpectedly:** Check `05b_DCF!C13` (g),
   `05b_DCF!C14` (WACC). Run Go To Special → Constants to find any
   inadvertently pasted static cells.
