"""Medical-luxury Matplotlib visualizations for the Streamlit presentation layer.

Charts V2
- Keeps the original public chart function names and call signatures.
- Adds clearer labels, consistent styling, input guards, and new overview charts.
- Supports the expanded result structure from analysis_v2.py while remaining
  compatible with the earlier analysis result dictionary.
- Visualizations are educational displays, not diagnoses or risk scores.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


# Centralized visual theme. Change colors here to restyle every chart.
THEME = {
    "background": "#FFFFFF",
    "surface": "#F6F8FC",
    "text": "#253247",
    "muted": "#718096",
    "grid": "#E8EDF4",
    "blue": "#4778C7",
    "blue_light": "#91ACD8",
    "green": "#36A879",
    "amber": "#E5AD43",
    "orange": "#D98A62",
    "red": "#D96A66",
    "red_dark": "#B84D59",
    "grey": "#AAB5C4",
}

GLUCOSE_BANDS = [
    (0, 100, "Below 100", THEME["green"]),
    (100, 126, "100–125", THEME["amber"]),
    (126, 220, "126+", THEME["red"]),
]
BMI_BANDS = [
    (10, 18.5, "Below 18.5", THEME["blue_light"]),
    (18.5, 25, "18.5–24.9", THEME["green"]),
    (25, 30, "25–29.9", THEME["amber"]),
    (30, 35, "30–34.9", THEME["orange"]),
    (35, 40, "35–39.9", THEME["red"]),
    (40, 50, "40+", THEME["red_dark"]),
]


def _valid_number(value: Any) -> bool:
    """Return True for finite numeric values (excluding booleans)."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _number(value: Any, fallback: float | None = None) -> float | None:
    """Safely convert a value to a finite float."""
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return fallback
    return converted if math.isfinite(converted) else fallback


def _base_chart(
    figsize: tuple[float, float] = (7.2, 3.0),
    *,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> tuple[Figure, Any]:
    """Create a chart using the shared GlycoSense visual theme."""
    fig, ax = plt.subplots(figsize=figsize, dpi=110)
    fig.patch.set_facecolor(THEME["background"])
    ax.set_facecolor(THEME["background"])
    if title:
        ax.set_title(title, loc="left", fontsize=11, fontweight="bold",
                     color=THEME["text"], pad=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=8.5, color=THEME["muted"], labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8.5, color=THEME["muted"], labelpad=8)
    ax.tick_params(axis="both", labelsize=8, colors=THEME["muted"], length=0, pad=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(THEME["grid"])
    ax.spines["bottom"].set_color(THEME["grid"])
    fig.tight_layout(pad=1.6)
    return fig, ax


def _empty_chart(message: str, title: str = "Chart unavailable",
                 figsize: tuple[float, float] = (7.2, 2.6)) -> Figure:
    """Return a friendly placeholder instead of raising on missing data."""
    fig, ax = _base_chart(figsize, title=title)
    ax.text(0.5, 0.5, message, transform=ax.transAxes, ha="center", va="center",
            color=THEME["muted"], fontsize=9, wrap=True)
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def _add_reference_bands(
    ax: Any,
    bands: Iterable[tuple[float, float, str, str]],
    *,
    y: float = 0,
    height: float = 0.36,
    label_y: float = -0.32,
    fontsize: int = 8,
) -> None:
    """Draw a segmented horizontal reference bar and labels."""
    for start, end, label, color in bands:
        ax.barh([y], [end - start], left=start, color=color, height=height,
                edgecolor="white", linewidth=1.2, zorder=2)
        ax.text((start + end) / 2, label_y, label, ha="center", va="top",
                fontsize=fontsize, color=THEME["muted"])


def _marker_label(ax: Any, value: float, y: float, text: str, xmin: float, xmax: float) -> None:
    """Place the measurement marker label without clipping at chart edges."""
    ax.axvline(value, color=THEME["text"], linewidth=2, ymin=0.17, ymax=0.88, zorder=4)
    x_position = min(max(value, xmin + (xmax - xmin) * 0.08),
                     xmax - (xmax - xmin) * 0.08)
    ax.text(x_position, y, text, ha="center", va="bottom", fontsize=8.5,
            fontweight="bold", color=THEME["text"], zorder=5)


def glucose_reference_chart(glucose: float, glucose_type: str) -> Figure:
    """Show fasting glucose reference bands; never apply them to random/unknown."""
    value = _number(glucose)
    kind = str(glucose_type or "Unknown").strip().title()
    if kind != "Fasting":
        return _empty_chart(
            "Fasting reference bands are not applied to this measurement type.",
            title="Glucose measurement",
            figsize=(8, 2.0),
        )
    if value is None or value < 0:
        return _empty_chart("Enter a valid non-negative glucose value.",
                            title="Fasting glucose reference")

    fig, ax = _base_chart(
        (8, 2.25),
        title="Fasting glucose reference",
        xlabel="Fasting glucose (mg/dL)",
    )
    xmin, xmax = 0.0, max(220.0, value * 1.08)
    bands = list(GLUCOSE_BANDS)
    # Extend the last visual band if the value exceeds the standard display range.
    if xmax > 220:
        bands[-1] = (126, xmax, "126+", THEME["red"])
    _add_reference_bands(ax, bands)
    _marker_label(ax, value, 0.34, f"Entered: {value:g}", xmin, xmax)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.55, 0.62)
    ax.set_yticks([])
    ax.grid(axis="x", color=THEME["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def bmi_reference_chart(bmi: float) -> Figure:
    """Show adult BMI screening bands and the entered value."""
    value = _number(bmi)
    if value is None or value <= 0:
        return _empty_chart("Enter a valid positive BMI value.",
                            title="Adult BMI reference")
    fig, ax = _base_chart(
        (8, 2.25),
        title="Adult BMI reference",
        xlabel="BMI (kg/m²) — adult screening categories",
    )
    xmin = 10.0
    xmax = max(50.0, value * 1.08)
    bands = list(BMI_BANDS)
    if xmax > 50:
        bands[-1] = (40, xmax, "40+", THEME["red_dark"])
    _add_reference_bands(ax, bands, fontsize=7.5)
    _marker_label(ax, value, 0.34, f"Entered: {value:g}", xmin, xmax)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.55, 0.62)
    ax.set_yticks([])
    ax.grid(axis="x", color=THEME["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def blood_pressure_chart(systolic: float, diastolic: float) -> Figure:
    """Compare systolic and diastolic readings as separate measurements."""
    sys_value = _number(systolic)
    dia_value = _number(diastolic)
    if sys_value is None or dia_value is None or sys_value <= 0 or dia_value <= 0:
        return _empty_chart("Valid systolic and diastolic values are required.",
                            title="Blood pressure")
    labels = ["Systolic", "Diastolic"]
    values = [sys_value, dia_value]
    fig, ax = _base_chart(
        (7.2, 2.8),
        title="Blood pressure readings",
        xlabel="Pressure (mmHg)",
    )
    bars = ax.barh(labels, values, color=[THEME["blue"], THEME["blue_light"]],
                   height=0.48, edgecolor="none", zorder=3)
    ax.bar_label(bars, labels=[f"{v:g} mmHg" for v in values], padding=6,
                 fontsize=8.5, color=THEME["text"])
    ax.set_xlim(0, max(values) * 1.28)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax.grid(axis="x", color=THEME["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def indicator_bar_chart(data: dict) -> Figure:
    """Legacy-compatible wrapper for the blood pressure comparison chart."""
    if not isinstance(data, dict):
        return _empty_chart("Blood pressure data is unavailable.", title="Blood pressure")
    return blood_pressure_chart(data.get("systolic_bp"), data.get("diastolic_bp"))


def indicator_overview_chart(result: dict) -> Figure:
    """Summarize which independent indicators have a reported classification.

    This chart intentionally does not combine indicators into a score.
    """
    indicators = result.get("indicators", {}) if isinstance(result, dict) else {}
    if not isinstance(indicators, dict) or not indicators:
        return _empty_chart("Indicator details are unavailable.", title="Indicator overview")

    glucose = indicators.get("glucose", {})
    bmi = indicators.get("bmi", {})
    bp = indicators.get("blood_pressure", {})
    entries = [
        ("Glucose", glucose.get("classification", "Not classified") if isinstance(glucose, dict) else "Not classified"),
        ("BMI", bmi.get("classification", "Not available") if isinstance(bmi, dict) else "Not available"),
        ("Blood pressure", bp.get("classification", "Not available") if isinstance(bp, dict) else "Not available"),
    ]
    color_map = {
        "Low Indicator Level": THEME["green"],
        "Moderate Indicator Level": THEME["amber"],
        "High Indicator Level": THEME["red"],
        "Not classified": THEME["grey"],
        "Not available": THEME["grey"],
    }
    fig, ax = _base_chart((7.2, 2.8), title="Independent indicator overview")
    y_positions = list(range(len(entries)))[::-1]
    for y, (label, status) in zip(y_positions, entries):
        color = color_map.get(status, THEME["blue"])
        ax.scatter([0.04], [y], s=95, color=color, transform=ax.get_yaxis_transform(),
                   clip_on=False, zorder=3)
        ax.text(0.09, y, label, transform=ax.get_yaxis_transform(),
                va="center", fontsize=9, color=THEME["text"])
        ax.text(0.98, y, str(status), transform=ax.get_yaxis_transform(),
                va="center", ha="right", fontsize=8.5, color=THEME["muted"])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, len(entries) - 0.4)
    ax.set_axis_off()
    ax.text(0.02, -0.18, "Indicators are displayed separately; no combined risk score is calculated.",
            transform=ax.transAxes, fontsize=7.5, color=THEME["muted"])
    fig.tight_layout()
    return fig


def triggered_rules_chart(result: dict) -> Figure:
    """Show triggered-rule counts by indicator, not as a severity score."""
    rules = result.get("triggered_rules", []) if isinstance(result, dict) else []
    counts: Counter[str] = Counter()
    for rule in rules:
        if isinstance(rule, dict):
            group = str(rule.get("indicator", "Other"))
            counts[group] += 1
    if not counts:
        return _empty_chart("No triggered-rule details are available.",
                            title="Rule activity")
    labels = list(counts.keys())
    values = [counts[label] for label in labels]
    fig, ax = _base_chart((7.2, max(2.8, 0.48 * len(labels) + 1.2)),
                          title="Triggered rules by indicator",
                          xlabel="Number of triggered rules")
    bars = ax.barh(labels[::-1], values[::-1], color=THEME["blue_light"],
                   height=0.55, edgecolor="none", zorder=3)
    ax.bar_label(bars, padding=5, fontsize=8.5, color=THEME["text"])
    ax.set_xlim(0, max(values) + 1.2)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", color=THEME["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def rule_activation_chart(result: dict) -> Figure:
    """Display the rule audit as triggered vs not-triggered counts."""
    audit = result.get("rule_audit", {}) if isinstance(result, dict) else {}
    triggered = audit.get("triggered", result.get("triggered_rules", [])) if isinstance(audit, dict) else []
    not_triggered = audit.get("not_triggered", result.get("not_triggered_rules", [])) if isinstance(audit, dict) else []
    triggered_count = len(triggered) if isinstance(triggered, list) else 0
    inactive_count = len(not_triggered) if isinstance(not_triggered, list) else 0
    if triggered_count + inactive_count == 0:
        return _empty_chart("Rule audit details are unavailable.", title="Rule audit")
    fig, ax = _base_chart((6.6, 2.5), title="Rule evaluation summary")
    labels = ["Triggered", "Not triggered"]
    values = [triggered_count, inactive_count]
    bars = ax.bar(labels, values, color=[THEME["blue"], THEME["grey"]],
                  width=0.52, edgecolor="none", zorder=3)
    ax.bar_label(bars, padding=4, fontsize=9, color=THEME["text"])
    ax.set_ylabel("Rule records")
    ax.set_ylim(0, max(values) * 1.25 + 1)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", color=THEME["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def synthetic_demo_chart(counts: dict[str, int] | None = None) -> Figure:
    """Display synthetic demo counts; never present them as population statistics."""
    demo_counts = counts or {"Low": 10, "Moderate": 10, "High": 10}
    labels = ["Low", "Moderate", "High"]
    values = []
    for label in labels:
        value = demo_counts.get(label, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return _empty_chart("Demo counts must be non-negative integers.",
                                title="Synthetic demo distribution")
        values.append(value)
    if sum(values) == 0:
        return _empty_chart("No synthetic demo records to display.",
                            title="Synthetic demo distribution")
    fig, ax = _base_chart(
        (6.6, 2.8),
        title="Synthetic demo dataset distribution",
        ylabel="Artificial example records",
    )
    bars = ax.bar(labels, values,
                  color=[THEME["green"], THEME["amber"], THEME["red"]],
                  width=0.55, edgecolor="none", zorder=3)
    ax.bar_label(bars, padding=4, fontsize=9, color=THEME["text"])
    ax.set_ylim(0, max(values) * 1.25 + 1)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", color=THEME["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.text(0.5, -0.23, "Synthetic examples only — not population statistics or medical evidence.",
            transform=ax.transAxes, ha="center", fontsize=7.5, color=THEME["muted"])
    fig.tight_layout()
    return fig


def render_chart_safely(chart_function: Any, *args: Any, **kwargs: Any) -> Figure:
    """Guard the Streamlit presentation layer from an unexpected chart exception.

    Returns a placeholder figure. The caller may log the exception separately.
    """
    try:
        figure = chart_function(*args, **kwargs)
        if not isinstance(figure, Figure):
            raise TypeError("Chart function did not return a Matplotlib Figure.")
        return figure
    except Exception as exc:  # presentation guard; do not expose traceback to users
        return _empty_chart(
            f"This visualization could not be rendered ({type(exc).__name__}). "
            "The analysis result is not changed.",
            title="Visualization unavailable",
        )
