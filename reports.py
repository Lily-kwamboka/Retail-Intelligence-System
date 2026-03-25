# reports.py
import os, io, datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # prevents GUI popup when running headless

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image, HRFlowable
)
from dotenv import load_dotenv
import yagmail

load_dotenv()

RUBIS_RED   = colors.HexColor("#CC0000")
RUBIS_LIGHT = colors.HexColor("#FFF5F5")
RUBIS_GRAY  = colors.HexColor("#F5F5F5")

# ── Chart builder ─────────────────────────────────────────────────────────────
def build_revenue_chart(df):
    data = df.groupby("branch")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 3))
    bars = ax.bar(data.index, data.values, color="#CC0000", edgecolor="none", width=0.5)
    ax.set_title("Revenue by branch", fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel("KES", fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="both", labelsize=8)

    # Add value labels on top of each bar
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (data.max() * 0.01),
            f"KES {bar.get_height():,.0f}",
            ha="center", va="bottom", fontsize=7, color="#333333"
        )

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

def build_margin_chart(df):
    data = df.groupby("branch")["gross_margin_pct"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 3))
    bar_colors = ["#CC0000" if v < 5 else "#2E7D32" for v in data.values]
    ax.bar(data.index, data.values, color=bar_colors, edgecolor="none", width=0.5)
    ax.axhline(y=5, color="orange", linestyle="--", linewidth=1, label="5% threshold")
    ax.set_title("Average gross margin by branch", fontsize=11, fontweight="bold", pad=10)
    ax.set_ylabel("%", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="both", labelsize=8)
    ax.legend(fontsize=8)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

# ── PDF builder ───────────────────────────────────────────────────────────────
def generate_daily_report(df_sales, df_inventory, output_path="rubis_daily_report.pdf"):
    today     = datetime.date.today().strftime("%d %B %Y")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d %B %Y")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )

    styles  = getSampleStyleSheet()
    story   = []

    # ── Header ────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "title", parent=styles["Normal"],
        fontSize=22, fontName="Helvetica-Bold",
        textColor=RUBIS_RED, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#666666"), spaceAfter=2
    )

    story.append(Paragraph("Rubis Intelligence", title_style))
    story.append(Paragraph(f"Daily Operations Report — {today}", sub_style))
    story.append(Paragraph(f"Data period: {yesterday}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RUBIS_RED, spaceAfter=12))

    # ── KPI summary cards ─────────────────────────────────────────────────────
    total_revenue   = df_sales["revenue"].sum()
    avg_margin      = df_sales["gross_margin_pct"].mean()
    low_margin_count= int((df_sales["gross_margin_pct"] < 5).sum())
    stockout_count  = int((df_inventory["days_of_stock"] <= 3).sum())
    top_branch      = df_sales.groupby("branch")["revenue"].sum().idxmax()

    kpi_data = [
        ["Metric", "Value", "Status"],
        ["Total Revenue",        f"KES {total_revenue:,.0f}",  ""],
        ["Avg Gross Margin",     f"{avg_margin:.1f}%",          "ALERT" if avg_margin < 5 else "OK"],
        ["Low Margin Products",  str(low_margin_count),         "ALERT" if low_margin_count > 0 else "OK"],
        ["Stockout Alerts",      str(stockout_count),           "ALERT" if stockout_count > 0 else "OK"],
        ["Top Branch",           top_branch,                    ""],
    ]

    kpi_table = Table(kpi_data, colWidths=[7*cm, 5*cm, 3*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  RUBIS_RED),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1),  [colors.white, RUBIS_LIGHT]),
        ("GRID",         (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("TEXTCOLOR",    (2, 1), (2, -1),  RUBIS_RED),
        ("FONTNAME",     (2, 1), (2, -1),  "Helvetica-Bold"),
    ]))

    story.append(Paragraph("Key Performance Indicators", styles["Heading2"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(kpi_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Revenue chart ─────────────────────────────────────────────────────────
    story.append(Paragraph("Revenue by Branch", styles["Heading2"]))
    story.append(Spacer(1, 0.2*cm))
    rev_chart = build_revenue_chart(df_sales)
    story.append(Image(rev_chart, width=15*cm, height=6.5*cm))
    story.append(Spacer(1, 0.4*cm))

    # ── Margin chart ──────────────────────────────────────────────────────────
    story.append(Paragraph("Gross Margin by Branch", styles["Heading2"]))
    story.append(Spacer(1, 0.2*cm))
    margin_chart = build_margin_chart(df_sales)
    story.append(Image(margin_chart, width=15*cm, height=6.5*cm))
    story.append(Spacer(1, 0.4*cm))

    # ── Stockout alerts section ───────────────────────────────────────────────
    at_risk = df_inventory[df_inventory["days_of_stock"] <= 3]
    story.append(Paragraph("Stockout Alerts", styles["Heading2"]))
    story.append(Spacer(1, 0.2*cm))

    if at_risk.empty:
        story.append(Paragraph("No stockout risks detected today.", styles["Normal"]))
    else:
        stock_data = [["Branch", "Product", "Days of Stock", "Current Qty"]]
        for _, row in at_risk.iterrows():
            stock_data.append([
                row["branch"],
                row["product_name"],
                str(row["days_of_stock"]),
                str(row["current_qty"])
            ])
        stock_table = Table(stock_data, colWidths=[4*cm, 6*cm, 3.5*cm, 3.5*cm])
        stock_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  RUBIS_RED),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, RUBIS_LIGHT]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(stock_table)

    story.append(Spacer(1, 0.5*cm))

    # ── Low margin products section ───────────────────────────────────────────
    low_margin = df_sales[df_sales["gross_margin_pct"] < 5]
    story.append(Paragraph("Low Margin Products (below 5%)", styles["Heading2"]))
    story.append(Spacer(1, 0.2*cm))

    if low_margin.empty:
        story.append(Paragraph("All products are above the 5% margin threshold.", styles["Normal"]))
    else:
        margin_data = [["Branch", "Product", "Margin %", "Revenue"]]
        for _, row in low_margin.iterrows():
            margin_data.append([
                row["branch"],
                row["product_name"],
                f"{row['gross_margin_pct']:.1f}%",
                f"KES {row['revenue']:,.0f}"
            ])
        margin_table = Table(margin_data, colWidths=[4*cm, 6*cm, 3*cm, 4*cm])
        margin_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  RUBIS_RED),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, RUBIS_LIGHT]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(margin_table)

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 0.2*cm))
    footer_style = ParagraphStyle(
        "footer", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#999999")
    )
    story.append(Paragraph(
        f"Generated automatically by Rubis Intelligence · {today} · Confidential",
        footer_style
    ))

    doc.build(story)
    print(f"PDF generated: {output_path}")
    return output_path

# ── Email the PDF ─────────────────────────────────────────────────────────────
def email_report(pdf_path):
    today = datetime.date.today().strftime("%d %B %Y")
    yag   = yagmail.SMTP(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
    yag.send(
        to=os.getenv("ALERT_EMAIL_TO"),
        subject=f"Rubis Intelligence — Daily Report {today}",
        contents=f"""
        <h2 style="color:#CC0000">Rubis Intelligence</h2>
        <p>Please find attached the daily operations report for <b>{today}</b>.</p>
        <p>This report was generated automatically by the Rubis Intelligence pipeline.</p>
        <br>
        <small style="color:#999">Do not reply to this email.</small>
        """,
        attachments=pdf_path
    )
    print(f"Report emailed to {os.getenv('ALERT_EMAIL_TO')}")