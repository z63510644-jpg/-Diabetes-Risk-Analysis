"""Build a readable, auditable report from analysis results."""
from __future__ import annotations

DISCLAIMER = (
    "This educational application is not a medical device and does not diagnose, "
    "predict, or estimate the probability of diabetes. It applies disclosed rules "
    "to entered values only. A single reading cannot confirm a diagnosis. Consult "
    "a qualified healthcare professional about concerning readings or health questions."
)


def build_report(data: dict, result: dict) -> dict:
    if not result.get("valid"):
        return {
            "classification": "Insufficient Data",
            "summary": result.get("summary", "Analysis could not be completed."),
            "triggered_rules": result.get("triggered_rules", []),
            "contributing_indicators": [],
            "indicators_without_triggered_rules": result.get("not_triggered_rules", []),
            "input_summary": data,
            "recommendations": ["Correct the input errors and run the analysis again."],
            "disclaimer": DISCLAIMER,
        }

    indicators = result["indicators"]
    if indicators["glucose"]["type"] == "Fasting":
        contributors = [f"Fasting Glucose: {indicators['glucose']['value']} mg/dL (the only indicator used for final classification)."]
    else:
        contributors = ["No glucose indicator contributes to a final classification because the measurement is not confirmed as fasting."]
    contextual_indicators = [
        f"BMI: {indicators['bmi']['value']} kg/m² — {indicators['bmi']['classification']} (reported independently)",
        f"Blood Pressure: {indicators['blood_pressure']['systolic']}/{indicators['blood_pressure']['diastolic']} mmHg — {indicators['blood_pressure']['classification']} (reported independently)",
        f"Age: {indicators['age']['value']} years (context only)",
        f"Family History: {indicators['family_history']['display']} (context only)",
        f"Insulin: {indicators['insulin']['display']} (display only)",
    ]

    recommendations = [
        "Use laboratory measurements and discuss questions about results with a qualified healthcare professional.",
        "A single blood glucose or blood pressure reading is not enough to establish a diagnosis.",
        "General wellbeing habits include balanced meals, regular age-appropriate physical activity, and routine preventive care.",
    ]
    if result.get("warnings"):
        recommendations.insert(0, "Review the safety notice shown with this report and seek appropriate professional guidance.")

    return {
        "classification": result["classification_label"],
        "summary": result["summary"],
        "triggered_rules": result["triggered_rules"],
        "contributing_indicators": contributors,
        "contextual_indicators": contextual_indicators,
        "indicators_without_triggered_rules": result["not_triggered_rules"],
        "input_summary": data,
        "recommendations": recommendations,
        "disclaimer": DISCLAIMER,
    }
