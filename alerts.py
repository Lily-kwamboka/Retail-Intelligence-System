# alerts.py
import os, yagmail
from dotenv import load_dotenv

load_dotenv()

def send_alert(subject, message):
    """Send an email alert to LB Retail Hub management."""
    try:
        yag = yagmail.SMTP(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
        yag.send(
            to=os.getenv("ALERT_EMAIL_TO"),
            subject=f"LB ALERT — {subject}",
            contents=f"""
            <h2 style="color:#CC0000">Rubis Intelligence Alert</h2>
            <h3>{subject}</h3>
            <pre style="font-size:14px">{message}</pre>
            <hr>
            <small>Sent automatically by Rubis Intelligence pipeline</small>
            """
        )
        print(f"Alert sent: {subject}")
    except Exception as e:
        print(f"Alert failed: {e}")

def check_margin_alerts(df):
    low_margin = df[df["gross_margin_pct"] < 5]
    for _, row in low_margin.iterrows():
        send_alert(
            subject=f"Low Margin — {row['product_name']}",
            message=(
                f"Branch:   {row['branch']}\n"
                f"Product:  {row['product_name']}\n"
                f"Margin:   {row['gross_margin_pct']:.1f}%\n"
                f"Action:   Review pricing immediately."
            )
        )

def check_stockout_alerts(df):
    at_risk = df[df["days_of_stock"] <= 3]
    for _, row in at_risk.iterrows():
        send_alert(
            subject=f"Stockout Risk — {row['product_name']} at {row['branch']}",
            message=(
                f"Branch:        {row['branch']}\n"
                f"Product:       {row['product_name']}\n"
                f"Days of stock: {row['days_of_stock']}\n"
                f"Current qty:   {row['current_qty']} units\n"
                f"Action:        Reorder immediately."
            )
        )

def check_revenue_targets(df, targets):
    for branch, target in targets.items():
        actual = df[df["branch"] == branch]["revenue"].sum()
        if actual < target * 0.85:
            gap = target - actual
            send_alert(
                subject=f"Revenue Miss — {branch}",
                message=(
                    f"Branch:  {branch}\n"
                    f"Target:  KES {target:,.0f}\n"
                    f"Actual:  KES {actual:,.0f}\n"
                    f"Gap:     KES {gap:,.0f} "
                    f"({(gap/target)*100:.1f}% below target)\n"
                    f"Action:  Review sales team performance."
                )
            )