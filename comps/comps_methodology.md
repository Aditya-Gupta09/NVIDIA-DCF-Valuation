# Comparable Company Analysis — Methodology
## NVIDIA Corporation (NVDA) | Valuation Date: October 17, 2025

---

## 1. Peer Selection Rationale

### Selection Criteria
Peers were selected based on three filters applied in order:

1. **Business overlap** — companies deriving material revenue from semiconductors, GPU/CPU silicon, or data center silicon
2. **Scale comparability** — enterprises with enterprise values above $100B (avoids micro-cap noise in multiples)
3. **Public market visibility** — actively traded on major exchanges with reliable LTM financials

### Peer Universe (5 companies)

| Ticker | Company | Rationale | Caveat |
|--------|---------|-----------|--------|
| AMD | Advanced Micro Devices | Closest comparable: GPU + CPU, data center exposure, fabless model, AI accelerator growth | Lower revenue scale; AI GPU market share much smaller than NVDA |
| INTC | Intel Corporation | CPU/semiconductor giant; data center exposure; comparable revenue scale | Vertically integrated (IDM model vs. fabless); FY2024 net loss excludes from P/E |
| QCOM | Qualcomm | Fabless semiconductor; mobile/automotive/IoT overlap; comparable WACC profile | Lower AI/data center exposure; predominantly mobile |
| AVGO | Broadcom | ASIC + networking chips; significant data center revenue; high EBITDA margins | Diversified into software (VMware); EBITDA not pure-semiconductor |
| TSM | TSMC | Foundry leader; semiconductor scale; data center capex exposure | Foundry business model differs fundamentally from fabless NVDA |

### What Was Excluded
- **Marvell (MRVL)** — considered but excluded; smaller scale and lower liquidity
- **ASML** — semiconductor equipment (different value chain)
- **Arm Holdings** — IP licensing model; not directly comparable

---

## 2. Data Sources and Collection Date

All peer financial data reflects **LTM (Last Twelve Months) as of October 17, 2025** and was sourced from:

- **Yahoo Finance** — share price, market capitalization, EPS, shares outstanding
- **Company filings (10-K / 20-F)** — revenue, EBITDA, net income
- **NVIDIA 10-K FY2025** — subject company financials

Raw data is committed at `datasets/raw/nvidia_market_data.csv`.  
Processed comps table is at `comps/comps_data.csv`.

---

## 3. Enterprise Value Calculation

**Formula:**
```
EV = Market Capitalization + Total Debt − Cash and Cash Equivalents
   = Market Cap + Net Debt
```

Where Net Debt = Total Debt (including leases) − Cash & Short-Term Investments.

**NVIDIA net debt:**
- Total Debt: $10,270M (long-term debt $8,463M + leases $1,807M)
- Cash & Equivalents: $43,210M
- **Net Debt: −$32,940M (net cash position)**

---

## 4. Multiples Calculated

| Multiple | Formula | Period | Notes |
|----------|---------|--------|-------|
| EV/Revenue | EV ÷ LTM Revenue | LTM | Useful for high-growth companies with variable margins |
| EV/EBITDA | EV ÷ LTM EBITDA | LTM | Primary valuation multiple; capital-structure neutral |
| P/E | Share Price ÷ LTM EPS | LTM | Excluded for Intel (negative earnings) |

---

## 5. Peer Multiple Summary

| Company | EV ($B) | Revenue ($B) | EBITDA ($B) | EV/Revenue | EV/EBITDA | P/E |
|---------|---------|-------------|------------|-----------|---------|-----|
| AMD | 376.3 | 29.6 | 5.5 | 12.7x | 68.3x | 134.7x |
| Intel | 205.2 | 53.1 | 9.2 | 3.9x | 22.3x | n/m |
| Qualcomm | 180.2 | 43.3 | 13.9 | 4.2x | 13.0x | 15.8x |
| Broadcom | 1,703.2 | 59.9 | 32.8 | 28.4x | 52.0x | 89.1x |
| TSMC | 1,168.5 | 119.1 | 81.8 | 9.8x | 14.3x | 29.7x |
| **Median** | — | — | — | **9.8x** | **22.3x** | **59.4x** |
| **Mean** | — | — | — | **11.8x** | **34.0x** | **67.3x** |

*Intel excluded from P/E (net loss FY2024).*

---

## 6. EBITDA Adjustments

### Adjustment Policy
No material EBITDA adjustments were applied. The following one-off items were considered and excluded from adjustment for the reasons stated:

| Company | Item | Amount | Decision | Reason |
|---------|------|--------|----------|--------|
| Intel | FY2024 restructuring charges | ~$2.8B | **Not adjusted** | Recurring risk in turnaround; conservative approach |
| Intel | FY2024 goodwill impairment | ~$15.9B | **Not adjusted** | Non-cash but reflects structural issues; keep in |
| AMD | Amortization of acquired intangibles | ~$1.3B | **Not adjusted** | Consistent with peers; no selective normalization |
| Broadcom | VMware integration costs | Immaterial to EBITDA % | **Not adjusted** | Below materiality threshold |
| NVIDIA | Mellanox amortization | Zero FY2025 | N/A | Fully amortized |

**Rationale for conservative approach:** Adjusting only NVIDIA's peers' EBITDA upward would inflate peer multiples, making NVIDIA appear cheaper on a relative basis. To avoid this bias, reported EBITDA is used throughout.

`ltm_ebitda_adj` column in `comps/comps_data.csv` equals `ltm_ebitda` (no adjustments) with the above rationale documented in the `notes` column.

---

## 7. Implied Valuation for NVIDIA

**Using LTM EBITDA ($83,317M) and peer median EV/EBITDA (22.3x):**

```
Implied EV      = 22.3 × $83,317M  = $1,857,969M
Implied Equity  = $1,857,969M − (−$32,940M)  = $1,890,909M
Implied Price   = $1,890,909M ÷ 24,300M shares  = $77.82
```

**Using FY1 projected EBITDA ($137,494M) and peer median EV/EBITDA (22.3x):**

```
Implied EV      = 22.3 × $137,494M  = $3,066,116M
Implied Equity  = $3,066,116M + $32,940M  = $3,099,056M
Implied Price   = $3,099,056M ÷ 24,300M  = $127.53
```

*Note: `comps_results.json` uses the model's LTM EBITDA ($98,280M from the Comparable Analysis sheet, which aggregates the trailing period) and produces median EV/EBITDA implied price of **$91.54**.*

---

## 8. Key Observations

1. **NVIDIA's current EV/EBITDA of 44.8x is 2x the peer median of 22.3x** — the market is pricing in a significant growth premium versus semiconductor peers.

2. **P/E comparison is less informative** — the peer P/E range is extremely wide (15.8x QCOM to 134.7x AMD), driven by very different earnings growth trajectories.

3. **TSMC and Intel compress the median** — including the foundry (TSMC) and loss-making peer (Intel) pulls medians down. On a pure-fabless, AI-exposed comps basis (AMD + AVGO only), median EV/EBITDA would be ~60x, which would suggest NVIDIA is fairly valued.

4. **Comps analysis is directional, not definitive** for NVIDIA at this stage of its AI cycle — no peer is building the same product at the same scale with the same margin profile.

---

*See `src/comps.py` for the Python implementation of all multiple calculations and implied price derivations.*
*See `datasets/processed/comps_results.json` for full output including all statistic levels (high / P75 / mean / median / P25 / low).*
