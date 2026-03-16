# Valuation Framework — NVIDIA DCF Valuation

## Overview

This document explains the complete DCF valuation methodology step by step,
including all formulas, the WACC derivation, terminal value methods, and the
comparable company bridge. Every number referenced here can be traced to a
specific cell in `models/Company_Valuation_Model.xlsx`.

---

## 1. Valuation Model Type

| Parameter | Value |
|-----------|-------|
| Model type | Unlevered DCF (FCFF-based) |
| Terminal value methods | Gordon Growth Model + EV/EBITDA Exit Multiple |
| Discount rate | WACC (Weighted Average Cost of Capital) |
| Projection horizon | 5 years (FY2026–FY2030) |
| Valuation date | October 17, 2025 |
| Currency | USD millions |

---

## 2. WACC Derivation

### Formula

```
WACC = wE × Ke + wD × Kd × (1 − t)

where:
  wE  = weight of equity = Market Cap / (Market Cap + Total Debt)
  Ke  = cost of equity (CAPM)
  wD  = weight of debt  = Total Debt / (Market Cap + Total Debt)
  Kd  = pre-tax cost of debt
  t   = effective tax rate
```

### Cost of Equity — CAPM

```
Ke = Rf + β_adj × ERP

where:
  Rf     = risk-free rate  = 4.07%   (US 10Y Treasury, Oct 17, 2025)
  β_adj  = Blume-adjusted beta = 1.7728
  ERP    = equity risk premium = 5.00%  (Damodaran implied, Jan 2025)

Ke = 4.07% + 1.7728 × 5.00% = 12.934%
```

### Beta — Blume Adjustment

Raw beta is estimated from a 60-month weekly regression of NVDA vs. S&P 500.
Blume adjustment pulls the raw beta toward 1.0 (mean reversion):

```
β_adj = 0.67 × β_raw + 0.33 × 1.0
β_adj = 0.67 × 2.109 + 0.33 = 1.7728
```

Source: Yahoo Finance price history. Calculation in `14_Beta` sheet.

### Capital Structure

```
Market Cap  = $4,452,000M  (shares × price = 24,300M × $183.22)
Total Debt  = $8,463M      (long-term debt only; leases excluded)
wE          = 4,452,000 / (4,452,000 + 8,463) = 99.81%
wD          = 8,463 / (4,452,000 + 8,463)     = 0.19%
```

NVIDIA is effectively an all-equity-financed company.
Debt is immaterial to WACC (contributes ~0.05% to the WACC value).

### Pre-Tax Cost of Debt

```
Kd = Interest Expense / Average Debt Balance
   = $252M / $8,913M = 2.83%
```

Source: `13_DebtSchedule` sheet.

### WACC Calculation

```
Ke (after-tax) component:  0.9981 × 12.934% = 12.912%
Kd (after-tax) component:  0.0019 × 2.83% × (1 − 13.26%) = 0.005%

WACC = 12.912% + 0.005% = 12.917% ≈ 12.91%
```

**Python cross-check (src/wacc.py):** Recalculated WACC = 12.9141%.
Model WACC = 12.9142%. Difference: 0.00 basis points. ✓

---

## 3. Unlevered Free Cash Flow (FCFF)

### Construction

```
Step 1:  EBIT (Operating Profit)
Step 2:  Operating Taxes  = EBIT × Effective Tax Rate
Step 3:  NOPAT            = EBIT − Operating Taxes
Step 4:  + Depreciation & Amortization
Step 5:  − Capital Expenditures
Step 6:  − Change in Net Working Capital
         ─────────────────────────────
Step 7:  = Unlevered Free Cash Flow (FCFF)
```

### Projected FCFFs (Base Case, $M)

| Year | Revenue | EBIT | NOPAT | D&A | CapEx | ΔNWC | FCFF |
|------|---------|------|-------|-----|-------|------|------|
| FY2026F | 211,566 | 134,448 | 113,302 | 3,046 | (6,347) | (10,686) | 99,315 |
| FY2027F | 295,121 | 193,766 | 164,515 | 4,817 | (9,444) | (9,942) | 149,946 |
| FY2028F | 371,459 | 251,944 | 213,877 | 6,921 | (12,258) | (8,305) | 200,235 |
| FY2029F | 429,311 | 299,977 | 256,174 | 9,078 | (12,879) | (5,950) | 246,423 |
| FY2030F | 521,671 | 376,425 | 321,576 | 11,117 | (14,607) | (10,031) | 308,056 |

Source: `05a_FCFF` sheet.

---

## 4. DCF Present Value Calculation

### Discount Factors

```
PV Factor(year t) = 1 / (1 + WACC)^t

Year 1 (FY2026):  1 / (1.1291)^1 = 0.8857
Year 2 (FY2027):  1 / (1.1291)^2 = 0.7844
Year 3 (FY2028):  1 / (1.1291)^3 = 0.6948
Year 4 (FY2029):  1 / (1.1291)^4 = 0.6154
Year 5 (FY2030):  1 / (1.1291)^5 = 0.5450
```

### Present Values of FCFFs ($M)

| Year | FCFF | PV Factor | PV of FCFF |
|------|------|-----------|-----------|
| FY2026F | 99,315 | 0.8857 | 87,956 |
| FY2027F | 149,946 | 0.7844 | 117,608 |
| FY2028F | 200,235 | 0.6948 | 139,089 |
| FY2029F | 246,423 | 0.6154 | 151,595 |
| FY2030F | 308,056 | 0.5450 | 167,836 |
| **Sum** | | | **$664,085M** |

---

## 5. Terminal Value — Method 1: Gordon Growth Model

```
Terminal Value = FCF₅ × (1 + g) / (WACC − g)

where:
  FCF₅ = $308,056M  (FY2030 FCFF)
  g    = 4.00%      (terminal growth rate)
  WACC = 12.91%

TV = $308,056M × (1.04) / (0.1291 − 0.04)
   = $320,378M / 0.0891
   = $3,593,999M  ($3.594 trillion)

PV of TV = $3,593,999M / (1.1291)^5
         = $3,593,999M × 0.5450
         = $1,958,098M
```

**Terminal value as % of EV:** $1,958,098 / $2,622,182 = **74.7%**

This is the key model sensitivity. At 74.7%, small changes in WACC or g
drive large changes in implied price — see `06_Sensitivity` for the full range.

---

## 6. Terminal Value — Method 2: EV/EBITDA Exit Multiple

```
Implied Terminal EV = FY2030 EBITDA × Exit Multiple

where:
  FY2030 EBITDA  = ~$387,543M  (from FCFF sheet projection)
  Exit Multiple  = 22.3x       (peer median EV/EBITDA — see comps_methodology.md)

Implied Terminal EV = $387,543M × 22.3 = $8,642,209M
PV of Terminal EV   = $8,642,209M / (1.1291)^5 = $4,709,684M

Enterprise Value (Exit Multiple) = $664,085M + $4,709,684M = $5,373,769M
Equity Value     = $5,373,769M + $32,940M = $5,406,709M
Implied Price    = $5,406,709M / 24,300M shares ≈ $225
```

**Cross-check of methods:**

| Method | Implied Price | Difference |
|--------|--------------|------------|
| Gordon Growth | $109.26 | — |
| Exit Multiple | ~$225 | +$116 (+106%) |
| Average of both | ~$167 | — |

The large divergence reflects the exit multiple method's use of FY2030 projected
EBITDA — which embeds very high growth assumptions — multiplied by a current
peer median that may not hold at NVIDIA's scale in 2030. The Gordon Growth
method is the base case; exit multiple serves as an optimistic cross-check.

---

## 7. Enterprise Value to Equity Value Bridge

```
Enterprise Value        = $2,622,182M   (Sum PV FCFs + PV Terminal Value)
  + Cash & Equivalents  = +$43,210M
  − Total Debt          = −$10,270M
  (= Net Cash)          = +$32,940M

Equity Value            = $2,655,122M

÷ Diluted Shares        = 24,300M

Implied Share Price     = $109.26
```

---

## 8. Sensitivity Analysis

The full WACC × Terminal Growth Rate sensitivity is in `06_Sensitivity` (two 9×9 grids).

Summary at selected nodes:

| WACC \ g | 2.0% | 3.0% | **4.0%** | 5.0% | 6.0% |
|-----------|------|------|----------|------|------|
| 10.9% | $98 | $117 | $144 | $188 | $290 |
| **12.9%** | $81 | $93 | **$109** | $132 | $174 |
| 14.9% | $66 | $75 | $85 | $99 | $117 |

Key observation: at the base case node (12.91% / 4.0%) the model produces
$109.26. A 1% decline in WACC to 11.9% lifts the price to $120 (+10%).
A 1% rise in terminal growth to 5.0% lifts the price to $132 (+21%).
Terminal value assumptions dominate the output.

---

## 9. Comparable Company Analysis Summary

Full detail in `comps/comps_methodology.md`. Summary:

| Multiple | Peer Median | NVIDIA LTM | NVIDIA FY1 Implied | 
|----------|------------|------------|---------------------|
| EV/Revenue | 9.8x | 26.8x | $68.05 (LTM) |
| EV/EBITDA | 22.3x | 44.8x | $91.54 (LTM) / $127.53 (FY1) |
| P/E | 59.4x | 52.2x | $208.50 |

NVIDIA trades at a significant premium to peer medians on EV-based multiples
(AI growth premium) but is near-median on P/E (reflecting high earnings base).

---

## 10. Final Valuation Conclusion

| Method | Weight | Implied Price |
|--------|--------|--------------|
| DCF — Gordon Growth | Primary | $109.26 |
| DCF — WACC×g range | Range | $77 – $194 |
| DCF — Exit Multiple | Secondary | ~$225 |
| Comps — EV/EBITDA median | Supporting | $91.54 |
| Comps — P/E median | Supporting | $208.50 |

**Recommendation: HOLD | Target: $110 | Downside: −40.0%**

The central estimate is $109.26. The weight of evidence from the Gordon Growth
DCF and EV/EBITDA comps suggests overvaluation. The P/E and exit multiple
methods offer support for current prices, but these embed aggressive terminal
assumptions. Given the asymmetric risk/reward, the base case recommendation is Hold.
