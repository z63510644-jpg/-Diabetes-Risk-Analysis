"""Matplotlib charts used by the Streamlit presentation layer."""
from __future__ import annotations

import matplotlib.pyplot as plt


def glucose_reference_chart(glucose: float, glucose_type: str):
    fig, ax = plt.subplots(figsize=(8, 1.8))
    if glucose_type != "Fasting":
        ax.text(0.5, 0.5, "Fasting reference bands not applied to this measurement", ha="center", va="center", fontsize=10)
        ax.axis("off")
        fig.tight_layout()
        return fig

    bands = [(0, 100, "Below 100"), (100, 126, "100–125"), (126, 220, "126+")]
    colors = ["#36A879", "#E5AD43", "#D96A66"]
    for (start, end, label), color in zip(bands, colors):
        ax.barh([0], [end - start], left=start, color=color, height=0.38, edgecolor="white")
        ax.text((start + end) / 2, -0.35, label, ha="center", va="top", fontsize=9)
    ax.axvline(glucose, color="#253247", linewidth=2.2, ymin=0.15, ymax=0.88)
    ax.text(glucose, 0.34, f"Entered: {glucose:g}", ha="center", va="bottom", fontsize=9, color="#253247")
    ax.set_xlim(0, 220)
    ax.set_yticks([])
    ax.set_xlabel("Fasting glucose (mg/dL)")
    ax.spines[["top", "left", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=0.15)
    fig.tight_layout()
    return fig


def indicator_bar_chart(data: dict):
    labels = ["Systolic BP", "Diastolic BP"]
    values = [data["systolic_bp"], data["diastolic_bp"]]
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.bar(labels, values, color=["#5B8DEF", "#8AA9E8"], width=0.55)
    ax.bar_label(bars, padding=3, fmt="%.0f")
    ax.set_ylabel("Blood pressure (mmHg)")
    ax.set_ylim(0, max(values) * 1.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.18)
    fig.tight_layout()
    return fig


def triggered_rules_chart(result: dict):
    counts: dict[str, int] = {}
    for rule in result.get("triggered_rules", []):
        group = rule["indicator"]
        counts[group] = counts.get(group, 0) + 1
    fig, ax = plt.subplots(figsize=(7, 3))
    labels = list(counts.keys()) or ["No rules"]
    values = list(counts.values()) or [0]
    bars = ax.bar(labels, values, color="#83A6D9")
    ax.bar_label(bars, padding=3)
    ax.set_ylabel("Triggered rules (count)")
    ax.tick_params(axis="x", rotation=20)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.18)
    fig.tight_layout()
    return fig


def synthetic_demo_chart():
    """Fixed synthetic counts; not population statistics or medical evidence."""
    labels = ["Low", "Moderate", "High"]
    counts = [10, 10, 10]
    fig, ax = plt.subplots(figsize=(6, 2.8))
    bars = ax.bar(labels, counts, color=["#36A879", "#E5AD43", "#D96A66"])
    ax.bar_label(bars, padding=3)
    ax.set_ylabel("Synthetic example records")
    ax.set_title("Demo dataset distribution (30 artificial records)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.15)
    fig.tight_layout()
    return fig


def bmi_reference_chart(bmi: float):
    fig, ax = plt.subplots(figsize=(8, 1.8))
    bands = [(10, 18.5, "Below 18.5"), (18.5, 25, "18.5–24.9"), (25, 30, "25–29.9"), (30, 35, "30–34.9"), (35, 40, "35–39.9"), (40, 50, "40+")]
    colors = ["#8AA9E8", "#36A879", "#E5AD43", "#D98A62", "#D96A66", "#B84D59"]
    for (start, end, label), color in zip(bands, colors):
        ax.barh([0], [end - start], left=start, color=color, height=0.38, edgecolor="white")
        ax.text((start + end) / 2, -0.35, label, ha="center", va="top", fontsize=8)
    ax.axvline(bmi, color="#253247", linewidth=2.2, ymin=0.15, ymax=0.88)
    ax.text(bmi, 0.34, f"Entered: {bmi:g}", ha="center", va="bottom", fontsize=9, color="#253247")
    ax.set_xlim(10, 50)
    ax.set_yticks([])
    ax.set_xlabel("BMI (kg/m²) — adult screening categories")
    ax.spines[["top", "left", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=0.15)
    fig.tight_layout()
    return fig
