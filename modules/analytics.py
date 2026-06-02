from datetime import datetime
from typing import Dict, List

import pandas as pd
import plotly.express as px


def build_metrics(applications: List[Dict[str, str]]) -> Dict[str, object]:
    df = pd.DataFrame(applications)
    if df.empty:
        return {
            "total": 0,
            "interview": 0,
            "rejected": 0,
            "offer": 0,
            "success_rate": 0.0,
            "status_chart": None,
            "monthly_chart": None,
            "conversion_chart": None,
        }

    df["application_date"] = pd.to_datetime(df["application_date"], errors="coerce")
    status_counts = df["status"].value_counts().to_dict()
    total = len(df)
    offer = status_counts.get("Offer", 0)
    success_rate = round((offer / total) * 100, 1) if total else 0.0

    status_chart = px.pie(
        df,
        names="status",
        title="Application Status Distribution",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    monthly = (
        df.dropna(subset=["application_date"])
        .groupby(pd.Grouper(key="application_date", freq="M"))
        .size()
        .reset_index(name="applications")
    )
    monthly_chart = px.bar(
        monthly,
        x="application_date",
        y="applications",
        title="Monthly Applications",
        labels={"application_date": "Month", "applications": "Applications"},
    )

    interview_rate = (
        df[df["status"].isin(["Interview", "Offer"])].groupby("status").size().reset_index(name="count")
    )
    conversion_chart = px.bar(
        interview_rate,
        x="status",
        y="count",
        title="Interview and Offer Conversion",
        labels={"count": "Count", "status": "Stage"},
        color="status",
        color_discrete_sequence=["#636EFA", "#00CC96"],
    )

    return {
        "total": total,
        "interview": status_counts.get("Interview", 0),
        "rejected": status_counts.get("Rejected", 0),
        "offer": offer,
        "success_rate": success_rate,
        "status_chart": status_chart,
        "monthly_chart": monthly_chart,
        "conversion_chart": conversion_chart,
    }
