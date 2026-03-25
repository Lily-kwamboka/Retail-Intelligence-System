# data/loader.py
import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()

def get_engine():
    return create_engine(os.getenv("DB_URL"))

def load_sales(branches=None):
    engine = get_engine()
    query = "SELECT * FROM pos_sales"
    df = pd.read_sql(query, engine)

    # Rename to standard names used across all modules
    df = df.rename(columns={
        "net_sale":         "revenue",
        "cost_ex_vat":      "cogs",
        "margin_pct":       "gross_margin_pct",
        "quantity":         "quantity_sold",
    })

    # Clean margin column — ensure it is numeric
    df["gross_margin_pct"] = pd.to_numeric(df["gross_margin_pct"], errors="coerce").fillna(0)
    df["revenue"]          = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
    df["cogs"]             = pd.to_numeric(df["cogs"], errors="coerce").fillna(0)

    # Filter by branch if requested
    if branches:
        df = df[df["branch"].isin(branches)]

    return df

def load_inventory(branches=None):
    """
    Your pos_sales table does not have inventory columns like
    days_of_stock and current_qty yet. This function estimates
    stockout risk from sales velocity until you add a real
    inventory table.
    """
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM pos_sales", engine)

    df = df.rename(columns={"quantity": "quantity_sold"})

    # Estimate days of stock from average daily sales velocity
    # Assumes 30 days of data — adjust if your data covers a different period
    df["avg_daily_sales"] = df["quantity_sold"] / 30
    df["current_qty"]     = df["quantity_sold"]  # proxy until real inventory exists
    df["days_of_stock"]   = (
        df["current_qty"] / df["avg_daily_sales"].replace(0, 1)
    ).round(1)

    if branches:
        df = df[df["branch"].isin(branches)]

    return df[["branch", "product_name", "current_qty", "days_of_stock"]]