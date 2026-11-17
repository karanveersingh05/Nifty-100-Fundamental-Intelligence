import os
import sys
import pandas as pd
from sqlalchemy import text

# Setup path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import get_engine

def verify_phase2_paths():
    print("\n[PHASE 2] Power BI File Path Verification:")
    expected_files = [
        "01_executive_overview.pbix",
        "02_company_deep_dive.pbix",
        "03_sector_comparison.pbix",
        "04_health_scorecard.pbix",
        "05_growth_analytics.pbix",
        "06_debt_leverage.pbix",
        "07_dividend_returns.pbix"
    ]
    
    powerbi_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'powerbi')
    if not os.path.exists(powerbi_dir):
        print(" [FAIL] 'powerbi' directory is missing.")
        return False
        
    all_present = True
    for pbix in expected_files:
        pbix_path = os.path.join(powerbi_dir, pbix)
        if os.path.exists(pbix_path):
            print(f" [PASS] Found: powerbi/{pbix}")
        else:
            print(f" [FAIL] Missing: powerbi/{pbix}")
            all_present = False
            
    return all_present

def run_verification():
    print("="*50)
    print(" POWER BI DATA VERIFICATION MODULE ")
    print("="*50)
    
    verify_phase2_paths()
    
    engine = get_engine()
    
    # Test 1: TCS Overall Score
    print("\n[TEST 1] TCS Health Score Check:")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT overall_score FROM fact_ml_scores WHERE symbol = 'TCS' ORDER BY computed_at DESC LIMIT 1")).fetchone()
            if result and result[0] is not None:
                print(f" [PASS] TCS Latest Overall Score in DB: {result[0]}")
                print(f"        Ensure Power BI Dashboard shows exactly {result[0]} for TCS.")
            else:
                print(" [FAIL] TCS Score not found or is NULL.")
    except Exception as e:
        print(f" [ERROR] Query error (Ensure Docker PostgreSQL is running): {e}")
            
    # Test 2: Debt-to-Equity Validation
    print("\n[TEST 2] Debt-to-Equity Ratio Check (HDFCBANK):")
    try:
        with engine.connect() as conn:
            query = """
            SELECT 
                borrowings, 
                (equity_capital + reserves) as equity,
                debt_to_equity
            FROM fact_balance_sheet 
            WHERE symbol = 'HDFCBANK'
            ORDER BY year_id DESC
            LIMIT 1
            """
            result = conn.execute(text(query)).fetchone()
            if result:
                borrowings, equity, dte = result
                borrowings = borrowings or 0
                equity = equity or 0
                calculated_dte = borrowings / equity if equity else 0
                dte = dte or 0
                print(f" [PASS] HDFCBANK Latest - Borrowings: {borrowings}, Equity: {equity}")
                print(f"        DB Stored Ratio: {dte:.4f} | Calculated Ratio: {calculated_dte:.4f}")
                print(f"        Ensure Power BI [Debt-to-Equity Ratio] measure outputs {calculated_dte:.4f} for HDFCBANK.")
            else:
                print(" [WARN] HDFCBANK data not found.")
    except Exception as e:
        print(f" [ERROR] Query error: {e}")

    # Test 3: Solvency Radar (Interest Coverage < 2.0 based on Phase 2 Page 5.2)
    print("\n[TEST 3] Solvency Radar Check (Companies with Interest Coverage < 2.0 latest year):")
    try:
        with engine.connect() as conn:
            query = """
            SELECT symbol, interest_coverage 
            FROM fact_profit_loss 
            WHERE interest_coverage < 2.0 AND interest_coverage > 0
            ORDER BY year_id DESC
            LIMIT 5
            """
            results = conn.execute(text(query)).fetchall()
            if results:
                print(" [PASS] The following companies should be highlighted in your Power BI Solvency Radar:")
                for r in results:
                    print(f"        - {r[0]}: {r[1]:.2f}")
            else:
                print(" [PASS] No companies found with Interest Coverage < 2.0.")
    except Exception as e:
         print(f" [ERROR] Query error: {e}")
             
    print("\n" + "="*50)
    print("Verification complete. Cross-check these exact numbers against your PBIX visuals.")

if __name__ == "__main__":
    run_verification()
