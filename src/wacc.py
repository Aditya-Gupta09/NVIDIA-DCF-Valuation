"""
src/wacc.py — WACC Extraction & Independent Recalculation
===========================================================
Reads WACC inputs from the Excel model via named ranges,
independently recalculates WACC using the CAPM formula,
compares the result to the model's own WACC output, and
writes structured results to datasets/processed/.

Named ranges used (defined in WACC sheet):
    risk_free_rate       WACC!$F$10
    adjusted_beta        WACC!$F$11  (=Beta!L13, Blume-adjusted)
    equity_risk_premium  WACC!$F$12
    effective_tax_rate   WACC!$F$17  (=Income statement modelling!F71)
    wacc_output          WACC!$F$19  (=F8*F9+F15*F16*(1-F17))

Additional inputs read directly from WACC sheet by address
(stable cells with no risk of row-shift):
    F7   Market cap (equity market value, $M)
    F8   Weight of equity
    F14  Total debt ($M)
    F15  Weight of debt
    F16  Pre-tax cost of debt

Usage:
    python src/wacc.py
    python src/wacc.py --model path/to/model.xlsx
    python src/wacc.py --verbose

Output:
    datasets/processed/wacc_results.json
"""

import os
import sys
import json
import argparse
from datetime import datetime

import openpyxl


# ─── CONFIGURATION ────────────────────────────────────────────────────────────

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "Company_Valuation_Model.xlsx"
)

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "wacc_results.json")

# Named ranges to read (defined in Excel via U-10 fix)
NAMED_RANGE_INPUTS = [
    "risk_free_rate",
    "adjusted_beta",
    "equity_risk_premium",
    "effective_tax_rate",
    "wacc_output",
]

# Additional cells read by address (WACC sheet only — stable, no row-shift risk)
ADDRESS_INPUTS = {
    "market_cap_equity":    ("WACC", "F7"),
    "weight_equity":        ("WACC", "F8"),
    "total_debt":           ("WACC", "F14"),
    "weight_debt":          ("WACC", "F15"),
    "pretax_cost_of_debt":  ("WACC", "F16"),
}

# Tolerance for model vs recalculated WACC comparison
WACC_TOLERANCE = 0.0001   # 1 basis point


# ─── NAMED RANGE READER ───────────────────────────────────────────────────────

def resolve_named_range(wb, name):
    """
    Resolves a named range to its cell value.
    Returns (value, sheet_name, cell_address) or raises ValueError.
    """
    if name not in wb.defined_names:
        raise ValueError(f"Named range '{name}' not found in workbook. "
                         f"Run u10_fix.py to add named ranges first.")

    defn = wb.defined_names[name]
    ref  = defn.attr_text  # e.g. "'WACC'!$F$10"

    # Parse sheet and cell from reference string
    # Format: 'Sheet Name'!$COL$ROW  or  SheetName!$COL$ROW
    try:
        if "!" not in ref:
            raise ValueError(f"Cannot parse reference '{ref}'")
        sheet_part, cell_part = ref.rsplit("!", 1)
        sheet_name = sheet_part.strip("'")
        cell_addr  = cell_part.replace("$", "")        # $F$10 → F10
        val = wb[sheet_name][cell_addr].value
        return val, sheet_name, cell_addr
    except Exception as e:
        raise ValueError(f"Error resolving named range '{name}' → '{ref}': {e}")


# ─── ADDRESS READER ───────────────────────────────────────────────────────────

def read_address_inputs(wb, addr_map):
    """
    Reads cells by explicit sheet + address.
    Returns dict of {key: value}.
    """
    results = {}
    for key, (sheet_name, addr) in addr_map.items():
        val = wb[sheet_name][addr].value
        if val is None:
            raise ValueError(
                f"Cell {sheet_name}!{addr} ({key}) is None — "
                f"open the model in Excel, press Ctrl+Alt+F9, and save."
            )
        if not isinstance(val, (int, float)):
            raise TypeError(
                f"Cell {sheet_name}!{addr} ({key}) = {repr(val)} is not numeric. "
                f"Run u07_fix.py to fix text-formatted numbers."
            )
        results[key] = float(val)
    return results


# ─── WACC RECALCULATION ───────────────────────────────────────────────────────

def recalculate_wacc(rf, beta, erp, tax_rate, w_equity, pretax_cod, w_debt):
    """
    Independently recalculates WACC using standard CAPM formula.

    CAPM:   Cost of equity = rf + beta * erp
    WACC:   w_equity * ke + w_debt * kd * (1 - tax_rate)

    Returns (wacc, cost_of_equity, after_tax_cost_of_debt).
    """
    cost_of_equity       = rf + beta * erp
    after_tax_cost_debt  = pretax_cod * (1 - tax_rate)
    wacc                 = w_equity * cost_of_equity + w_debt * after_tax_cost_debt
    return wacc, cost_of_equity, after_tax_cost_debt


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="WACC extraction and recalculation")
    parser.add_argument(
        "--model", default=DEFAULT_MODEL_PATH,
        help=f"Path to Excel model (default: {DEFAULT_MODEL_PATH})"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print detailed workings"
    )
    args = parser.parse_args()

    model_path = os.path.abspath(args.model)

    print(f"\n{'─'*60}")
    print(f"  wacc.py — WACC Extraction & Recalculation")
    print(f"{'─'*60}")
    print(f"\n  Model : {model_path}")

    # ── Validate file ──────────────────────────────────────────────────────
    if not os.path.exists(model_path):
        print(f"\n  ERROR: Model file not found: {model_path}")
        print(f"  Adjust --model path or place the model in models/ folder.\n")
        sys.exit(1)

    # ── Load workbook ──────────────────────────────────────────────────────
    print(f"\n  [1/4] Loading model...")
    wb = openpyxl.load_workbook(model_path, data_only=True)

    # ── Read named range inputs ────────────────────────────────────────────
    print(f"\n  [2/4] Reading named range inputs from WACC sheet...")
    named_values = {}
    for name in NAMED_RANGE_INPUTS:
        try:
            val, sheet, addr = resolve_named_range(wb, name)
            if val is None:
                print(f"\n  ERROR: Named range '{name}' resolved to None.")
                print(f"  The model has formula cells that need Excel recalculation.")
                print(f"  Open the model → Ctrl+Alt+F9 → Save → re-run this script.\n")
                sys.exit(1)
            named_values[name] = float(val)
            if args.verbose:
                print(f"    {name:<25} = {val}  ({sheet}!{addr})")
        except ValueError as e:
            print(f"\n  ERROR: {e}\n")
            sys.exit(1)

    # ── Read address inputs ────────────────────────────────────────────────
    print(f"\n  [3/4] Reading supporting inputs by cell address...")
    try:
        addr_values = read_address_inputs(wb, ADDRESS_INPUTS)
        if args.verbose:
            for k, v in addr_values.items():
                print(f"    {k:<25} = {v}")
    except (ValueError, TypeError) as e:
        print(f"\n  ERROR: {e}\n")
        sys.exit(1)

    # ── Recalculate WACC independently ────────────────────────────────────
    print(f"\n  [4/4] Recalculating WACC independently...")

    rf       = named_values["risk_free_rate"]
    beta     = named_values["adjusted_beta"]
    erp      = named_values["equity_risk_premium"]
    tax      = named_values["effective_tax_rate"]
    w_eq     = addr_values["weight_equity"]
    kd_pre   = addr_values["pretax_cost_of_debt"]
    w_debt   = addr_values["weight_debt"]
    wacc_mdl = named_values["wacc_output"]

    wacc_calc, ke, kd_post = recalculate_wacc(rf, beta, erp, tax, w_eq, kd_pre, w_debt)

    diff_bp   = abs(wacc_calc - wacc_mdl) * 10000    # in basis points
    match     = diff_bp < (WACC_TOLERANCE * 10000)

    # ── Print results ──────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  WACC CALCULATION RESULTS")
    print(f"{'─'*60}\n")
    print(f"  INPUTS")
    print(f"    Risk-free rate            {rf*100:.4f}%")
    print(f"    Adjusted beta (Blume)     {beta:.4f}")
    print(f"    Equity risk premium       {erp*100:.4f}%")
    print(f"    Effective tax rate        {tax*100:.4f}%")
    print(f"    Weight of equity          {w_eq*100:.4f}%")
    print(f"    Weight of debt            {w_debt*100:.4f}%")
    print(f"    Pre-tax cost of debt      {kd_pre*100:.4f}%\n")
    print(f"  CAPM WORKINGS")
    print(f"    Cost of equity  =  {rf*100:.4f}% + {beta:.4f} × {erp*100:.4f}%")
    print(f"                    =  {ke*100:.4f}%")
    print(f"    After-tax CoD   =  {kd_pre*100:.4f}% × (1 - {tax*100:.4f}%)")
    print(f"                    =  {kd_post*100:.4f}%\n")
    print(f"  WACC FORMULA")
    print(f"    WACC  =  {w_eq*100:.4f}% × {ke*100:.4f}%")
    print(f"           + {w_debt*100:.4f}% × {kd_post*100:.4f}%")
    print(f"          =  {wacc_calc*100:.4f}%\n")
    print(f"  CROSS-CHECK vs MODEL")
    print(f"    Model WACC (wacc_output)  {wacc_mdl*100:.4f}%")
    print(f"    Recalculated WACC         {wacc_calc*100:.4f}%")
    print(f"    Difference                {diff_bp:.2f} bps")
    status = "✓ MATCH" if match else "✗ MISMATCH — investigate formula inputs"
    print(f"    Status                    {status}\n")

    # ── Build output JSON ──────────────────────────────────────────────────
    output = {
        "meta": {
            "script":          "src/wacc.py",
            "model_file":      os.path.basename(model_path),
            "run_timestamp":   datetime.now().isoformat(),
            "cross_check":     "PASS" if match else "FAIL",
            "diff_basis_pts":  round(diff_bp, 4),
        },
        "inputs": {
            "risk_free_rate":       rf,
            "adjusted_beta":        beta,
            "equity_risk_premium":  erp,
            "effective_tax_rate":   tax,
            "weight_equity":        w_eq,
            "weight_debt":          w_debt,
            "pretax_cost_of_debt":  kd_pre,
            "market_cap_equity_m":  addr_values["market_cap_equity"],
            "total_debt_m":         addr_values["total_debt"],
        },
        "outputs": {
            "cost_of_equity":           round(ke, 8),
            "after_tax_cost_of_debt":   round(kd_post, 8),
            "wacc_recalculated":        round(wacc_calc, 8),
            "wacc_from_model":          round(wacc_mdl, 8),
        },
        "display": {
            "cost_of_equity_pct":         f"{ke*100:.4f}%",
            "after_tax_cost_of_debt_pct": f"{kd_post*100:.4f}%",
            "wacc_recalculated_pct":      f"{wacc_calc*100:.4f}%",
            "wacc_from_model_pct":        f"{wacc_mdl*100:.4f}%",
        }
    }

    # ── Write JSON ─────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"{'─'*60}")
    print(f"  Output written: {os.path.abspath(OUTPUT_FILE)}")
    print(f"{'─'*60}\n")

    return 0 if match else 1


if __name__ == "__main__":
    sys.exit(main())
