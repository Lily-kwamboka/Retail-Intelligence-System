"""
alert_engine.py
Rubis Intelligence — Alert Dispatcher
Sends HTML emails via Gmail SMTP (App Password).
No Twilio. No paid services.
"""

import os
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from dotenv import load_dotenv

from templates.margin_alert import render_margin_alert
from templates.stockout_alert import render_stockout_alert
from templates.revenue_alert import render_revenue_alert
from templates.pipeline_alert import render_pipeline_alert

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── SMTP CONFIG (from .env) ─────────────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")          # your Gmail address
SMTP_PASS = os.getenv("SMTP_PASS")          # Gmail App Password (16 chars)

# ── RECIPIENT LISTS (from .env, comma-separated) ────────────────────────────
RECIPIENTS = {
    "critical":  [r.strip() for r in os.getenv("RECIPIENTS_CRITICAL", "").split(",") if r.strip()],
    "warning":   [r.strip() for r in os.getenv("RECIPIENTS_WARNING",  "").split(",") if r.strip()],
    "info":      [r.strip() for r in os.getenv("RECIPIENTS_INFO",     "").split(",") if r.strip()],
}

# ── THRESHOLDS (configurable via .env) ──────────────────────────────────────
THRESHOLDS = {
    "margin_floor_pct":   float(os.getenv("THRESHOLD_MARGIN_FLOOR",   5.0)),
    "stockout_days":      int(os.getenv("THRESHOLD_STOCKOUT_DAYS",     3)),
    "revenue_miss_pct":   float(os.getenv("THRESHOLD_REVENUE_MISS",   10.0)),
}


# ── CORE SEND FUNCTION ───────────────────────────────────────────────────────

def send_email(subject: str, body_html: str, recipients: list[str],
               attachment_path: Path | None = None) -> bool:
    """
    Send an HTML email via Gmail SMTP.
    Returns True on success, False on failure.
    """
    if not recipients:
        logger.warning("send_email called with empty recipients list. Skipping.")
        return False
    if not SMTP_USER or not SMTP_PASS:
        logger.error("SMTP_USER or SMTP_PASS not set in .env. Cannot send email.")
        return False

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = f"Rubis Intelligence <{SMTP_USER}>"
    msg["To"]      = ", ".join(recipients)

    msg.attach(MIMEText(body_html, "html"))

    if attachment_path and attachment_path.exists():
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={attachment_path.name}")
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, recipients, msg.as_string())
        logger.info(f"Email sent → {recipients} | Subject: {subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("Gmail authentication failed. Check SMTP_USER and SMTP_PASS in .env.")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
    return False


# ── ALERT DISPATCHERS ────────────────────────────────────────────────────────

def fire_margin_alert(product: str, branch: str, current_margin_pct: float,
                      target_margin_pct: float = None):
    """
    Fire when a product's margin drops below THRESHOLD_MARGIN_FLOOR.
    """
    target = target_margin_pct or THRESHOLDS["margin_floor_pct"]
    subject = f"🔴 Margin Alert — {product} | {branch} ({current_margin_pct:.1f}%)"
    body = render_margin_alert(
        product=product,
        branch=branch,
        current_margin=current_margin_pct,
        threshold=target,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    return send_email(subject, body, RECIPIENTS["critical"])


def fire_stockout_alert(product: str, branch: str, days_cover: float,
                        avg_daily_sales: float, current_stock: int):
    """
    Fire when days-of-cover drops below THRESHOLD_STOCKOUT_DAYS.
    """
    subject = f"🔴 Stockout Risk — {product} | {branch} ({days_cover:.1f} days left)"
    body = render_stockout_alert(
        product=product,
        branch=branch,
        days_cover=days_cover,
        avg_daily_sales=avg_daily_sales,
        current_stock=current_stock,
        threshold=THRESHOLDS["stockout_days"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    return send_email(subject, body, RECIPIENTS["critical"])


def fire_revenue_alert(branch: str, actual_revenue: float, target_revenue: float,
                       date: str = None):
    """
    Fire when a branch misses its daily revenue target by more than
    THRESHOLD_REVENUE_MISS percent.
    """
    miss_pct = ((target_revenue - actual_revenue) / target_revenue) * 100
    subject = f"⚠️ Revenue Miss — {branch} | {miss_pct:.1f}% below target"
    body = render_revenue_alert(
        branch=branch,
        actual=actual_revenue,
        target=target_revenue,
        miss_pct=miss_pct,
        date=date or datetime.now().strftime("%Y-%m-%d"),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    return send_email(subject, body, RECIPIENTS["warning"])


def fire_pipeline_alert(error_message: str, pipeline_name: str = "main",
                        last_success: str = None):
    """
    Fire when the pipeline fails or a data gap is detected.
    """
    subject = f"⚙️ Pipeline Alert — {pipeline_name} | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body = render_pipeline_alert(
        pipeline_name=pipeline_name,
        error_message=error_message,
        last_success=last_success or "Unknown",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    return send_email(subject, body, RECIPIENTS["info"])


# ── MAIN BATCH CHECKER (called after each pipeline run) ─────────────────────

def run_all_checks(kpi_df, branch_targets: dict = None):
    """
    Pass the post-pipeline KPI dataframe here.
    Required columns: product, branch, margin_pct, days_cover,
                      avg_daily_sales, current_stock, daily_revenue
    """
    import pandas as pd

    alerts_fired = 0

    for _, row in kpi_df.iterrows():

        # 1. Margin check
        if row.get("margin_pct", 999) < THRESHOLDS["margin_floor_pct"]:
            fired = fire_margin_alert(
                product=row["product"],
                branch=row["branch"],
                current_margin_pct=row["margin_pct"],
            )
            if fired:
                alerts_fired += 1

        # 2. Stockout check
        if row.get("days_cover", 999) < THRESHOLDS["stockout_days"]:
            fired = fire_stockout_alert(
                product=row["product"],
                branch=row["branch"],
                days_cover=row["days_cover"],
                avg_daily_sales=row.get("avg_daily_sales", 0),
                current_stock=row.get("current_stock", 0),
            )
            if fired:
                alerts_fired += 1

    # 3. Revenue target check (per branch)
    if branch_targets:
        branch_revenue = kpi_df.groupby("branch")["daily_revenue"].sum()
        for branch, actual in branch_revenue.items():
            target = branch_targets.get(branch)
            if target and actual < target:
                miss_pct = ((target - actual) / target) * 100
                if miss_pct >= THRESHOLDS["revenue_miss_pct"]:
                    fired = fire_revenue_alert(branch, actual, target)
                    if fired:
                        alerts_fired += 1

    logger.info(f"Alert check complete. {alerts_fired} alert(s) fired.")
    return alerts_fired