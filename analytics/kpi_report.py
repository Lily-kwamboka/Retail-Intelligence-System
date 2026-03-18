# analytics/kpi_report.py
# Rubis POS Analytics Engine — KPI Report Generator

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine():
    return create_engine(os.getenv('DB_URL'))

def branch_performance():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM vw_branch_performance", engine)
    print("\n" + "="*60)
    print("BRANCH PERFORMANCE SUMMARY")
    print("="*60)
    print(df.to_string(index=False))
    return df

def department_performance():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM vw_department_performance", engine)
    print("\n" + "="*60)
    print("DEPARTMENT PERFORMANCE SUMMARY")
    print("="*60)
    print(df.to_string(index=False))
    return df

def top_products(limit=20):
    engine = get_engine()
    df = pd.read_sql(f"SELECT * FROM vw_top_products LIMIT {limit}", engine)
    print("\n" + "="*60)
    print(f"TOP {limit} PRODUCTS BY NET SALES")
    print("="*60)
    print(df.to_string(index=False))
    return df

def high_value_products():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM vw_high_value_products", engine)
    print("\n" + "="*60)
    print("HIGH VALUE PRODUCTS (contribution > KES 50,000)")
    print("="*60)
    print(df.to_string(index=False))
    return df

def low_margin_products():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM vw_low_margin_products", engine)
    print("\n" + "="*60)
    print("LOW MARGIN PRODUCTS (margin < 10%)")
    print("="*60)
    print(df.to_string(index=False))
    return df

def branch_department_matrix():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM vw_branch_department", engine)
    print("\n" + "="*60)
    print("BRANCH x DEPARTMENT MATRIX")
    print("="*60)
    print(df.to_string(index=False))
    return df

def run_full_report():
    print("\n" + "="*60)
    print("RUBIS POS — FULL KPI REPORT")
    print("="*60)

    branch_df       = branch_performance()
    dept_df         = department_performance()
    top_df          = top_products(20)
    high_value_df   = high_value_products()
    low_margin_df   = low_margin_products()
    matrix_df       = branch_department_matrix()

    # Save all to Excel
    os.makedirs('reports', exist_ok=True)
    with pd.ExcelWriter('reports/rubis_kpi_report.xlsx', engine='openpyxl') as writer:
        branch_df.to_excel(writer,     sheet_name='Branch Performance',    index=False)
        dept_df.to_excel(writer,       sheet_name='Department Performance', index=False)
        top_df.to_excel(writer,        sheet_name='Top Products',           index=False)
        high_value_df.to_excel(writer, sheet_name='High Value Products',    index=False)
        low_margin_df.to_excel(writer, sheet_name='Low Margin Products',    index=False)
        matrix_df.to_excel(writer,     sheet_name='Branch x Department',    index=False)

    print("\n" + "="*60)
    print("Report saved to: reports/rubis_kpi_report.xlsx")
    print("="*60)

if __name__ == '__main__':
    run_full_report()