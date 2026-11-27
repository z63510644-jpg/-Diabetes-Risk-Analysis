"""Input validation for Diabetes Risk Analysis.

Ranges in this module are technical input guardrails, not medical limits.
"""
from __future__ import annotations

from typing import Any

# Technical guardrails only; they prevent obvious data-entry mistakes.
INPUT_LIMITS = {
    "age": (1, 120),
    "glucose": (20, 600),
    "bmi": (10, 80),
    "systolic_bp": (50, 300),
    "diastolic_bp": (30, 200),
    "insulin": (0, 1000),
}


def validate_patient_data(data: dict[str, Any]) -> list[str]:
    """Return human-readable validation errors. Empty list means valid input."""
    errors: list[str] = []

    required = [
        "age", "glucose", "glucose_type", "bmi",
        "systolic_bp", "diastolic_bp", "family_history",
    ]
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    if errors:
        return errors

    numeric_fields = ["age", "glucose", "bmi", "systolic_bp", "diastolic_bp"]
    if data.get("insulin") is not None:
        numeric_fields.append("insulin")

    for field in numeric_fields:
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"{field.replace('_', ' ').title()} must be numeric.")
            continue
        low, high = INPUT_LIMITS[field]
        if not low <= value <= high:
            errors.append(
                f"{field.replace('_', ' ').title()} must be between {low} and {high} "
                "for input validation only. These are not medical thresholds."
            )

    if data.get("glucose_type") not in {"Fasting", "Random", "Unknown"}:
        errors.append("Glucose Type must be Fasting, Random, or Unknown.")

    if not isinstance(data.get("family_history"), bool):
        errors.append("Family History must be Yes or No.")

    systolic = data.get("systolic_bp")
    diastolic = data.get("diastolic_bp")
    if isinstance(systolic, (int, float)) and isinstance(diastolic, (int, float)):
        if systolic <= diastolic:
            errors.append("Systolic pressure must be greater than diastolic pressure.")

    return errors
