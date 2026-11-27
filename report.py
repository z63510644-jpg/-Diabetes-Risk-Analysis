"""GlycoSense report builder — Report Engine V2.

Creates a readable, explainable, auditable report from the rule-based analysis
engine. It preserves build_report(data, result) and the legacy report keys.

This module formats supplied analysis output. It does not diagnose, calculate
probabilities, modify clinical thresholds, or replace professional care.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable
import json


REPORT_VERSION = "2.0"

DISCLAIMER = (
    "This educational application is not a medical device and does not diagnose, "
    "predict, or estimate the probability of diabetes. It applies disclosed rules "
    "to entered values only. A single reading cannot confirm a diagnosis. "
    "Discuss concerning readings and health questions with a qualified healthcare professional."
)

SCOPE_NOTE = (
    "This project is designed for adults aged 20 years and older. Its glucose "
    "classification uses fasting glucose thresholds only when the measurement "
    "type is confirmed as fasting. BMI, blood pressure, age, family history, "
    "and insulin are reported separately and are not combined into a risk score."
)

PRIORITY_ORDER = {
    "urgent_review": 0,
    "attention": 1,
    "medical_review": 2,
    "follow_up": 3,
    "maintenance": 4,
    "information": 5,
}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _display(value: Any, fallback: str = "Not available") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _normalise_recommendations(items: Any) -> list[dict[str, str]]:
    """Accept both legacy string recommendations and V2 recommendation objects."""
    normalised: list[dict[str, str]] = []
    for item in _safe_list(items):
        if isinstance(item, str):
            normalised.append({
                "category": "general",
                "priority": "information",
                "title": "Recommended next step",
                "message": item,
            })
        elif isinstance(item, dict):
            normalised.append({
                "category": _display(item.get("category"), "general"),
                "priority": _display(item.get("priority"), "information"),
                "title": _display(item.get("title"), "Recommended next step"),
                "message": _display(item.get("message"), "No additional details provided."),
            })
    return sorted(
        normalised,
        key=lambda item: PRIORITY_ORDER.get(item["priority"], 99),
    )


def _normalise_rules(items: Any) -> list[dict[str, str]]:
    """Normalise rule records while retaining IDs and explanatory details."""
    output: list[dict[str, str]] = []
    for item in _safe_list(items):
        if isinstance(item, dict):
            output.append({
                "rule_id": _display(item.get("rule_id"), "Unspecified"),
                "name": _display(item.get("name"), "Unnamed rule"),
                "indicator": _display(item.get("indicator"), "General"),
                "result": _display(item.get("result"), "Triggered"),
                "explanation": _display(item.get("explanation"), "No explanation supplied."),
                "source": _display(item.get("source"), "Not specified"),
                "status": "triggered",
            })
        elif isinstance(item, str):
            rule_id, separator, name = item.partition(" — ")
            output.append({
                "rule_id": rule_id if separator else "Unspecified",
                "name": name if separator else item,
                "indicator": "General",
                "result": "Not triggered",
                "explanation": "This rule was not activated for the supplied inputs.",
                "source": "Not specified",
                "status": "not_triggered",
            })
    return output


def _input_summary(data: Any) -> dict[str, Any]:
    """Copy only known project input fields into a stable report structure."""
    source = _safe_dict(data)
    keys = (
        "age", "glucose", "glucose_type", "bmi", "height", "weight",
        "systolic_bp", "diastolic_bp", "family_history", "insulin",
    )
    return {key: source.get(key) for key in keys if key in source}


def _indicator_sections(indicators: Any) -> dict[str, dict[str, Any]]:
    source = _safe_dict(indicators)
    glucose = _safe_dict(source.get("glucose"))
    bmi = _safe_dict(source.get("bmi"))
    bp = _safe_dict(source.get("blood_pressure"))
    age = _safe_dict(source.get("age"))
    family = _safe_dict(source.get("family_history"))
    insulin = _safe_dict(source.get("insulin"))

    glucose_type = _display(glucose.get("type"), "Unknown")
    glucose_class = _display(glucose.get("classification"), "Not classified")
    glucose_is_fasting = glucose_type.lower() == "fasting"

    return {
        "glucose": {
            "name": "Glucose",
            "value": glucose.get("value"),
            "unit": _display(glucose.get("unit"), "mg/dL"),
            "measurement_type": glucose_type,
            "classification": glucose_class,
            "rule_id": glucose.get("rule_id"),
            "used_for_final_classification": glucose_is_fasting,
            "interpretation": (
                "Used as the sole basis for the project's glucose classification."
                if glucose_is_fasting
                else "Not classified using fasting thresholds because the measurement is not confirmed as fasting."
            ),
        },
        "bmi": {
            "name": "BMI",
            "value": bmi.get("value"),
            "unit": _display(bmi.get("unit"), "kg/m²"),
            "classification": _display(bmi.get("classification"), "Not available"),
            "rule_id": bmi.get("rule_id"),
            "used_for_final_classification": False,
            "interpretation": "Reported independently; BMI is a screening measure and is not a diagnosis.",
        },
        "blood_pressure": {
            "name": "Blood Pressure",
            "systolic": bp.get("systolic"),
            "diastolic": bp.get("diastolic"),
            "unit": _display(bp.get("unit"), "mmHg"),
            "classification": _display(bp.get("classification"), "Not available"),
            "rule_id": bp.get("rule_id"),
            "used_for_final_classification": False,
            "interpretation": "Reported independently; one reading cannot establish a diagnosis.",
        },
        "age": {
            "name": "Age",
            "value": age.get("value"),
            "unit": _display(age.get("unit"), "years"),
            "used_for_final_classification": False,
            "interpretation": "Context only; it does not change the glucose classification.",
        },
        "family_history": {
            "name": "Family History",
            "value": family.get("value"),
            "display": _display(family.get("display")),
            "used_for_final_classification": False,
            "interpretation": "Context only; it does not change the glucose classification.",
        },
        "insulin": {
            "name": "Insulin",
            "value": insulin.get("value"),
            "unit": _display(insulin.get("unit"), "µIU/mL"),
            "display": _display(insulin.get("display")),
            "used_for_final_classification": False,
            "interpretation": "Optional display-only value; no insulin category is inferred.",
        },
    }


def _build_contributors(indicators: dict[str, dict[str, Any]]) -> list[str]:
    glucose = indicators["glucose"]
    if glucose["used_for_final_classification"]:
        return [
            f"Fasting glucose: {_display(glucose['value'])} {glucose['unit']} "
            "(the only indicator used for the final glucose classification)."
        ]
    return [
        "No glucose indicator contributes to a final glucose classification "
        "because the measurement is not confirmed as fasting."
    ]


def _build_contextual_text(indicators: dict[str, dict[str, Any]]) -> list[str]:
    bmi = indicators["bmi"]
    bp = indicators["blood_pressure"]
    age = indicators["age"]
    family = indicators["family_history"]
    insulin = indicators["insulin"]
    return [
        f"BMI: {_display(bmi['value'])} {bmi['unit']} — {bmi['classification']} (independent screening indicator)",
        f"Blood pressure: {_display(bp['systolic'])}/{_display(bp['diastolic'])} {bp['unit']} — {bp['classification']} (independent indicator)",
        f"Age: {_display(age['value'])} {age['unit']} (context only)",
        f"Family history: {family['display']} (context only)",
        f"Insulin: {insulin['display']} (display only)",
    ]


def _build_quality_notes(result: dict[str, Any], indicators: dict[str, dict[str, Any]]) -> dict[str, Any]:
    quality = _safe_dict(result.get("data_quality"))
    notes = [str(item) for item in _safe_list(quality.get("notes"))]
    issues = [str(item) for item in _safe_list(quality.get("issues"))]
    if not indicators["glucose"]["used_for_final_classification"]:
        note = "Fasting glucose thresholds were not applied."
        if note not in notes:
            notes.append(note)
    if indicators["insulin"]["value"] is None:
        note = "Insulin was not provided; this does not block the analysis."
        if note not in notes:
            notes.append(note)
    return {
        "status": _display(quality.get("status"), "not specified"),
        "issues": issues,
        "notes": notes,
    }


def _build_safety_section(result: dict[str, Any]) -> dict[str, Any]:
    flags = []
    for item in _safe_list(result.get("safety_flags")):
        if isinstance(item, dict):
            flags.append({
                "level": _display(item.get("level"), "information"),
                "indicator": _display(item.get("indicator"), "General"),
                "message": _display(item.get("message")),
            })
    warnings = [str(item) for item in _safe_list(result.get("warnings"))]
    # Preserve warnings that were not already represented by a structured flag.
    known_messages = {flag["message"] for flag in flags}
    for warning in warnings:
        if warning not in known_messages:
            flags.append({
                "level": "attention",
                "indicator": "General",
                "message": warning,
            })
    flags.sort(key=lambda item: PRIORITY_ORDER.get(item["level"], 99))
    return {"flags": flags, "has_alerts": bool(flags)}


def _build_rule_audit(result: dict[str, Any]) -> dict[str, Any]:
    audit = _safe_dict(result.get("rule_audit"))
    triggered_source = audit.get("triggered", result.get("triggered_rules", []))
    inactive_source = audit.get("not_triggered", result.get("not_triggered_rules", []))
    triggered = _normalise_rules(triggered_source)
    inactive = _normalise_rules(inactive_source)
    declared_total = audit.get("total_project_rules", 27)
    return {
        "declared_project_rule_count": declared_total,
        "triggered_count": len(triggered),
        "not_triggered_count": len(inactive),
        "triggered": triggered,
        "not_triggered": inactive,
        "note": (
            "Rule counts describe rule activation only. They are not a severity score, "
            "risk score, or probability."
        ),
    }


def build_report(data: dict, result: dict) -> dict[str, Any]:
    """Build a structured report while preserving the original report keys.

    The returned dictionary includes:
    - legacy keys used by the original Streamlit/report layer;
    - structured sections for dashboard rendering;
    - normalized recommendations, safety flags, and rule audit details;
    - report and engine version metadata.
    """
    result = _safe_dict(result)
    valid = bool(result.get("valid"))

    if not valid:
        errors = [str(item) for item in _safe_list(result.get("errors"))]
        if not errors:
            errors = ["Analysis could not be completed because the input was invalid or incomplete."]
        report = {
            "report_version": REPORT_VERSION,
            "engine_version": _display(result.get("engine_version"), "Unknown"),
            "status": "blocked",
            "classification": "Insufficient Data",
            "summary": _display(result.get("summary"), "Analysis could not be completed."),
            "triggered_rules": _normalise_rules(result.get("triggered_rules")),
            "contributing_indicators": [],
            "contextual_indicators": [],
            "indicators_without_triggered_rules": _normalise_rules(result.get("not_triggered_rules")),
            "input_summary": _input_summary(data),
            "recommendations": [{
                "category": "data_quality",
                "priority": "information",
                "title": "Correct the input data",
                "message": "Correct the input errors and run the analysis again.",
            }],
            "data_quality": {
                "status": "blocked",
                "issues": errors,
                "notes": [],
            },
            "safety": _build_safety_section(result),
            "explanations": _safe_list(result.get("explanations")),
            "rule_audit": _build_rule_audit(result),
            "disclaimer": DISCLAIMER,
            "scope_note": SCOPE_NOTE,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "analysis_timestamp_utc": result.get("analysis_timestamp_utc"),
        }
        # Backward-compatible plain text recommendation list.
        report["recommendation_text"] = [item["message"] for item in report["recommendations"]]
        return report

    indicators = _indicator_sections(result.get("indicators"))
    recommendations = _normalise_recommendations(result.get("recommendations"))
    if not recommendations:
        recommendations = _normalise_recommendations([
            "Discuss questions about health measurements with a qualified healthcare professional.",
            "A single reading is not enough to establish a diagnosis.",
        ])

    rules = _normalise_rules(result.get("triggered_rules"))
    inactive = _normalise_rules(result.get("not_triggered_rules"))
    safety = _build_safety_section(result)
    quality = _build_quality_notes(result, indicators)
    audit = _build_rule_audit(result)

    # Legacy human-readable fields retained for compatibility.
    contributors = _build_contributors(indicators)
    contextual = _build_contextual_text(indicators)
    recommendation_text = [item["message"] for item in recommendations]

    report = {
        "report_version": REPORT_VERSION,
        "engine_version": _display(result.get("engine_version"), "Unknown"),
        "status": "complete",
        "classification": _display(result.get("classification_label"), "Insufficient Data"),
        "summary": _display(result.get("summary"), "No summary supplied."),
        "triggered_rules": rules,
        "contributing_indicators": contributors,
        "contextual_indicators": contextual,
        "indicators_without_triggered_rules": inactive,
        "input_summary": _input_summary(data),
        "recommendations": recommendations,
        "recommendation_text": recommendation_text,
        "indicators": indicators,
        "data_quality": quality,
        "safety": safety,
        "explanations": _safe_list(result.get("explanations")),
        "rule_audit": audit,
        "disclaimer": DISCLAIMER,
        "scope_note": SCOPE_NOTE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_timestamp_utc": result.get("analysis_timestamp_utc"),
    }
    return report


def report_to_markdown(report: dict[str, Any]) -> str:
    """Render a report as readable Markdown for Streamlit or file export."""
    report = _safe_dict(report)
    lines = [
        "# GlycoSense — Diabetes Risk Analysis Report",
        "",
        f"**Report version:** {_display(report.get('report_version'))}  ",
        f"**Engine version:** {_display(report.get('engine_version'))}  ",
        f"**Status:** {_display(report.get('status'))}  ",
        f"**Generated (UTC):** {_display(report.get('generated_at_utc'))}",
        "",
        "## Assessment",
        "",
        f"**{_display(report.get('classification'))}**",
        "",
        _display(report.get("summary")),
        "",
        "## Indicator overview",
        "",
    ]

    indicators = _safe_dict(report.get("indicators"))
    if indicators:
        glucose = indicators.get("glucose", {})
        bmi = indicators.get("bmi", {})
        bp = indicators.get("blood_pressure", {})
        lines.extend([
            f"- **Glucose:** {_display(glucose.get('value'))} {_display(glucose.get('unit'))}; "
            f"{_display(glucose.get('classification'))}; type: {_display(glucose.get('measurement_type'))}.",
            f"- **BMI:** {_display(bmi.get('value'))} {_display(bmi.get('unit'))}; "
            f"{_display(bmi.get('classification'))}.",
            f"- **Blood pressure:** {_display(bp.get('systolic'))}/{_display(bp.get('diastolic'))} "
            f"{_display(bp.get('unit'))}; {_display(bp.get('classification'))}.",
        ])
    else:
        lines.append("Indicator details are unavailable.")

    lines.extend(["", "## Contributing indicator", ""])
    lines.extend(f"- {item}" for item in _safe_list(report.get("contributing_indicators")))
    lines.extend(["", "## Contextual indicators", ""])
    lines.extend(f"- {item}" for item in _safe_list(report.get("contextual_indicators")))

    lines.extend(["", "## Safety notices", ""])
    safety = _safe_dict(report.get("safety"))
    flags = _safe_list(safety.get("flags"))
    if flags:
        for flag in flags:
            if isinstance(flag, dict):
                lines.append(
                    f"- **{_display(flag.get('level'))} — {_display(flag.get('indicator'))}:** "
                    f"{_display(flag.get('message'))}"
                )
    else:
        lines.append("No additional safety notice was returned by the analysis engine.")

    lines.extend(["", "## Recommendations", ""])
    for item in _safe_list(report.get("recommendations")):
        if isinstance(item, dict):
            lines.append(
                f"- **{_display(item.get('title'))}:** {_display(item.get('message'))}"
            )
        else:
            lines.append(f"- {item}")

    lines.extend(["", "## Rule audit", ""])
    audit = _safe_dict(report.get("rule_audit"))
    lines.append(
        f"- Declared project rules: {_display(audit.get('declared_project_rule_count'))}"
    )
    lines.append(f"- Triggered rule records: {_display(audit.get('triggered_count'), '0')}")
    lines.append(f"- Not-triggered rule records: {_display(audit.get('not_triggered_count'), '0')}")
    lines.append(f"- {_display(audit.get('note'))}")

    lines.extend(["", "## Data quality", ""])
    quality = _safe_dict(report.get("data_quality"))
    lines.append(f"- Status: {_display(quality.get('status'))}")
    for issue in _safe_list(quality.get("issues")):
        lines.append(f"- Issue: {issue}")
    for note in _safe_list(quality.get("notes")):
        lines.append(f"- Note: {note}")

    lines.extend([
        "",
        "## Scope and disclaimer",
        "",
        _display(report.get("scope_note"), SCOPE_NOTE),
        "",
        _display(report.get("disclaimer"), DISCLAIMER),
        "",
    ])
    return "\n".join(lines)


def report_to_json(report: dict[str, Any], *, indent: int = 2) -> str:
    """Serialize a report to JSON without failing on unexpected custom objects."""
    return json.dumps(report, ensure_ascii=False, indent=indent, default=str)
