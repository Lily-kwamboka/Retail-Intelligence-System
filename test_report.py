# test_report.py
from data.loader import load_sales, load_inventory
from reports import generate_daily_report, email_report

df_sales = load_sales()
df_inv   = load_inventory()

pdf = generate_daily_report(df_sales, df_inv)
email_report(pdf)