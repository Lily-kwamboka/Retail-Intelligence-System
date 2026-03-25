# scheduler.py
import schedule, time, datetime
from data.loader import load_sales, load_inventory
from reports import generate_daily_report, email_report
from alerts import check_margin_alerts, check_stockout_alerts, check_revenue_targets

BRANCH_TARGETS = {
    "Tigoni":  500000,
    "Kingo":   350000,
    "Thika":   420000,
    "Limuru":  380000,
}

def run_pipeline():
    print(f"\n--- Pipeline started at {datetime.datetime.now()} ---")

    # 1. Load data
    df_sales = load_sales()
    df_inv   = load_inventory()

    # 2. Run alert checks
    check_margin_alerts(df_sales)
    check_stockout_alerts(df_inv)
    check_revenue_targets(df_sales, BRANCH_TARGETS)

    # 3. Generate and email PDF report
    pdf = generate_daily_report(df_sales, df_inv)
    email_report(pdf)

    print(f"--- Pipeline complete at {datetime.datetime.now()} ---\n")

# Run every day at 7:00am
schedule.every().day.at("07:00").do(run_pipeline)

print("Scheduler is running — waiting for 07:00...")
print("Press Ctrl+C to stop.\n")

while True:
    schedule.run_pending()
    time.sleep(60)