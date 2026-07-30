"""
CX Analytics Dashboard
-----------------------
Analyzes a customer support ticket dataset to answer the questions a CX
or Customer Success leader actually cares about: which channels perform
best, where CSAT is at risk, and what's correlated with churn.

Produces four charts (saved to charts/) and a printed summary of the
business-relevant findings — not just numbers, but what to do about them.

Run:
    python analyze.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "cx_tickets.csv"
CHARTS_DIR = Path(__file__).parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["ticket_date"])
    return df


def chart_csat_by_channel(df: pd.DataFrame):
    summary = df.groupby("channel")["csat_score"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(summary.index, summary.values, color="#2f6f4f")
    ax.set_xlabel("Average CSAT (1-5)")
    ax.set_title("Average CSAT by Support Channel")
    for i, v in enumerate(summary.values):
        ax.text(v + 0.02, i, f"{v:.2f}", va="center")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "csat_by_channel.png")
    plt.close(fig)


def chart_resolution_vs_csat(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6, 4))
    sample = df.sample(min(600, len(df)), random_state=1)
    ax.scatter(sample["resolution_hours"], sample["csat_score"], alpha=0.25, s=14, color="#c25b27")
    ax.set_xlabel("Resolution Time (hours)")
    ax.set_ylabel("CSAT Score")
    ax.set_title("Resolution Time vs. CSAT")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "resolution_vs_csat.png")
    plt.close(fig)


def chart_churn_by_csat_band(df: pd.DataFrame):
    df = df.copy()
    df["csat_band"] = pd.cut(df["csat_score"], [0, 2, 3, 4, 5], labels=["1-2", "2-3", "3-4", "4-5"])
    churn_rate = df.groupby("csat_band", observed=True)["churned_within_90d"].mean() * 100
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(churn_rate.index.astype(str), churn_rate.values, color="#8b3a3a")
    ax.set_xlabel("CSAT Band")
    ax.set_ylabel("Churn Rate within 90 Days (%)")
    ax.set_title("Churn Risk by CSAT Band")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "churn_by_csat_band.png")
    plt.close(fig)


def chart_fcr_by_channel(df: pd.DataFrame):
    fcr = df.groupby("channel")["first_contact_resolution"].mean().sort_values() * 100
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(fcr.index, fcr.values, color="#3a5a8b")
    ax.set_xlabel("First Contact Resolution Rate (%)")
    ax.set_title("First Contact Resolution by Channel")
    for i, v in enumerate(fcr.values):
        ax.text(v + 0.5, i, f"{v:.0f}%", va="center")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "fcr_by_channel.png")
    plt.close(fig)


def print_insights(df: pd.DataFrame):
    overall_csat = df["csat_score"].mean()
    worst_channel = df.groupby("channel")["csat_score"].mean().idxmin()
    best_fcr_channel = df.groupby("channel")["first_contact_resolution"].mean().idxmax()
    high_risk_churn = df[df["csat_score"] < 3]["churned_within_90d"].mean() * 100
    low_risk_churn = df[df["csat_score"] >= 4]["churned_within_90d"].mean() * 100

    print("=== CX Insights Summary ===\n")
    print(f"Overall average CSAT: {overall_csat:.2f} / 5")
    print(f"Lowest-CSAT channel: {worst_channel} — investigate staffing/process there first")
    print(f"Highest first-contact-resolution channel: {best_fcr_channel}")
    print(f"Churn rate when CSAT < 3: {high_risk_churn:.1f}%")
    print(f"Churn rate when CSAT >= 4: {low_risk_churn:.1f}%")
    print(
        f"\nRecommendation: tickets with CSAT below 3 churn at "
        f"{high_risk_churn / max(low_risk_churn, 0.1):.1f}x the rate of high-CSAT tickets — "
        f"a proactive save-play triggered on low CSAT scores is likely the highest-ROI CX investment here."
    )


def main():
    df = load_data()
    chart_csat_by_channel(df)
    chart_resolution_vs_csat(df)
    chart_churn_by_csat_band(df)
    chart_fcr_by_channel(df)
    print_insights(df)
    print(f"\nCharts saved to {CHARTS_DIR}/")


if __name__ == "__main__":
    main()
