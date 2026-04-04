import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    return create_engine(os.getenv('DB_URL'))

def log_run(engine, rows, branches, status, error=None):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO load_log (rows_loaded, branches_loaded, status, error_message)
            VALUES (:rows, :branches, :status, :error)
        """), {"rows": rows, "branches": branches, "status": status, "error": error})

def clean_df(df):
    """Fix column types before loading to DB"""

    # Fix sales_month — extract integer month from "2026-03" or any format
    if 'sales_month' in df.columns:
        df['sales_month'] = pd.to_datetime(df['sales_month'], errors='coerce').dt.month.fillna(0).astype(int)

    # Fix sales_year — extract integer year
    if 'sales_year' in df.columns:
        df['sales_year'] = pd.to_datetime(df['sales_year'].astype(str), errors='coerce').dt.year.fillna(0).astype(int)

    # Fix sales_date — ensure it's a proper date
    if 'sales_date' in df.columns:
        df['sales_date'] = pd.to_datetime(df['sales_date'], errors='coerce')

    # Fix numeric columns
    numeric_cols = [
        'quantity', 'gross_sales', 'discount', 'sales_after_discount',
        'vat_amount', 'net_sale', 'cost_ex_vat', 'net_contribution',
        'margin_pct', 'markup_pct'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

def load_to_db(df):
    engine = get_engine()

    # Clean types before loading
    df = clean_df(df)

    rows = len(df)
    branches = df['source_branch'].nunique() if 'source_branch' in df.columns else 0

    try:
        # Write to staging table first
        df.to_sql(
            name='pos_sales_staging',
            con=engine,
            if_exists='replace',
            index=False,
            chunksize=500
        )

        # Upsert from staging into main table
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO pos_sales (
                    branch, department, class, sku_code, product_name,
                    quantity, gross_sales, discount, sales_after_discount,
                    vat_amount, net_sale, cost_ex_vat, net_contribution,
                    margin_pct, markup_pct, source_file, source_branch,
                    sales_date, sales_month, sales_year, loaded_at
                )
                SELECT
                    branch, department, class, sku_code, product_name,
                    quantity, gross_sales, discount, sales_after_discount,
                    vat_amount, net_sale, cost_ex_vat, net_contribution,
                    margin_pct, markup_pct, source_file, source_branch,
                    sales_date, sales_month, sales_year, loaded_at
                FROM pos_sales_staging
                ON CONFLICT (source_file, source_branch, sku_code, department)
                DO NOTHING;
            """))

        # Log successful run
        log_run(engine, rows, branches, 'success')
        print(f'Loaded {rows} rows across {branches} branches into pos_sales')

    except Exception as e:
        try:
            log_run(engine, 0, 0, 'failed', str(e))
        except:
            pass
        raise