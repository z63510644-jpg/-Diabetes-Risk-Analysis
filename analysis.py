"""Explainable rule-based analysis engine for Diabetes Risk Analysis.

Engine version: 2.0
- Preserves the existing analyze_data(data) entry point and legacy result keys.
- Keeps the project's 27 rule IDs and the approved rule-based approach.
- Does not use machine learning, weighted scores, or probability estimates.
- Educational screening support only; not a diagnostic system.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from validation import validate_patient_data

ENGINE_VERSION = "2.0"
RULE_COUNT = 27

GLUCOSE_SOURCE = "ADA Standards of Care in Diabetes—2026"
BMI_SOURCE = "CDC Adult BMI Categories"
BP_SOURCE = "2025 AHA/ACC Blood Pressure Guideline"

GLUCOSE_RULES = {
    "G001": "Fasting glucose below 100",
    "G002": "Fasting glucose 100 to below 126",
    "G003": "Fasting glucose 126 or above",
}
BMI_RULES = {
    "B001": "Underweight BMI category",
    "B002": "Healthy-weight BMI category",
    "B003": "Overweight BMI category",
    "B004": "Class 1 obesity BMI category",
    "B005": "Class 2 obesity BMI category",
    "B006": "Class 3 obesity BMI category",
}
BP_RULES = {
    "BP001": "Normal blood pressure category",
    "BP002": "Elevated blood pressure category",
    "BP003": "Stage 1 hypertension range",
    "BP004": "Stage 2 hypertension range",
    "BP005": "Severe blood pressure range",
}


def _rule(
    rule_id: str,
    name: str,
    indicator: str,
    result: str,
    explanation: str,
    source: str,
) -> dict[str, str]:
    """Build a consistent, UI-friendly rule result."""
    return {
        "rule_id": rule_id,
        "name": name,
        "indicator": indicator,
        "result": result,
        "explanation": explanation,
        "source": source,
    }


def _inactive(rule_id: str, name: str, reason: str = "Condition not met.") -> dict[str, str]:
    """Represent a rule that was evaluated but did not activate."""
    return {"rule_id": rule_id, "name": name, "reason": reason, "status": "not_triggered"}


def _bp_component_level(value: int, component: str) -> int:
    """Map one BP component to the project's ordered category levels."""
    if component == "systolic":
        if value > 180:
            return 4
        if value >= 140:
            return 3
        if value >= 130:
            return 2
        if value >= 120:
            return 1
        return 0

    if value > 120:
        return 4
    if value >= 90:
        return 3
    if value >= 80:
        return 2
    return 0


def classify_bmi(bmi: float) -> tuple[str, str, str]:
    """Return adult BMI category, rule ID, and a cautious explanation."""
    if bmi < 18.5:
        return "Underweight", "B001", "BMI is below 18.5 kg/m². BMI is a screening measure, not a diagnosis."
    if bmi < 25:
        return "Healthy Weight", "B002", "BMI is from 18.5 to below 25 kg/m². BMI is a screening measure, not a diagnosis."
    if bmi < 30:
        return "Overweight", "B003", "BMI is from 25 to below 30 kg/m². BMI is a screening measure, not a diagnosis."
    if bmi < 35:
        return "Class 1 Obesity", "B004", "BMI is from 30 to below 35 kg/m². BMI is a screening measure, not a diagnosis."
    if bmi < 40:
        return "Class 2 Obesity", "B005", "BMI is from 35 to below 40 kg/m². BMI is a screening measure, not a diagnosis."
    return "Class 3 Obesity", "B006", "BMI is 40 kg/m² or higher. BMI is a screening measure, not a diagnosis."


def classify_blood_pressure(systolic: int, diastolic: int) -> tuple[str, str, str]:
    """Return the highest category reached by either BP component."""
    if systolic > 180 or diastolic > 120:
        return (
            "Severe Range", "BP005",
            "The reading is above 180 systolic or above 120 diastolic. Repeat the measurement as directed by a healthcare professional and seek prompt medical guidance. If concerning symptoms occur, seek emergency medical help.",
        )
    if systolic >= 140 or diastolic >= 90:
        return "Stage 2 Range", "BP004", "At least one value is in the Stage 2 range. A single reading does not establish a diagnosis."
    if systolic >= 130 or diastolic >= 80:
        return "Stage 1 Range", "BP003", "At least one value is in the Stage 1 range. A single reading does not establish a diagnosis."
    if 120 <= systolic <= 129 and diastolic < 80:
        return "Elevated Range", "BP002", "Systolic pressure is 120–129 mm Hg and diastolic pressure is below 80 mm Hg."
    return "Normal Range", "BP001", "Both values are below 120/80 mm Hg."


def _empty_result(errors: list[str], rule: dict[str, str], summary: str) -> dict[str, Any]:
    """Return the stable result structure when analysis cannot proceed."""
    return {
        "valid": False,
        "errors": errors,
        "classification": None,
        "classification_label": "Insufficient Data",
        "triggered_rules": [rule],
        "not_triggered_rules": [],
        "warnings": [],
        "indicators": {},
        "summary": summary,
        "engine_version": ENGINE_VERSION,
        "data_quality": {"status": "blocked", "issues": errors, "notes": []},
        "explanations": [],
        "recommendations": [],
        "safety_flags": [],
        "rule_audit": {"triggered": [rule], "not_triggered": [], "total_project_rules": RULE_COUNT},
        "analysis_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def _build_recommendations(
    glucose_class: str | None,
    glucose: float,
    glucose_type: str,
    bp_rule: str,
    bmi_rule: str,
) -> list[dict[str, str]]:
    """Create cautious educational next steps; never prescribe treatment."""
    items: list[dict[str, str]] = []

    if glucose_type != "Fasting":
        items.append({
            "category": "glucose",
            "priority": "information",
            "title": "A fasting comparison is unavailable",
            "message": "This reading was not classified using fasting thresholds. Ask a qualified healthcare professional which test and timing are appropriate.",
        })
    elif glucose < 70:
        items.append({
            "category": "glucose",
            "priority": "attention",
            "title": "Review the low glucose reading",
            "message": "A value below 70 mg/dL should not be treated as a reassuring result. Seek qualified medical advice, especially if symptoms are present.",
        })
    elif glucose_class == "Low Indicator Level":
        items.append({
            "category": "glucose",
            "priority": "maintenance",
            "title": "Maintain healthy routines",
            "message": "Continue balanced meals, suitable regular activity, and routine health checks. A result in this range does not rule out diabetes.",
        })
    elif glucose_class == "Moderate Indicator Level":
        items.append({
            "category": "glucose",
            "priority": "follow_up",
            "title": "Discuss the result with a healthcare professional",
            "message": "Ask whether repeat testing or an A1C test is appropriate. Balanced meals and limiting sugary drinks may support general health.",
        })
    elif glucose_class == "High Indicator Level":
        items.append({
            "category": "glucose",
            "priority": "medical_review",
            "title": "Arrange clinical evaluation",
            "message": "This result reaches a laboratory threshold that requires clinical confirmation. Do not self-diagnose or start medication based on this report.",
        })

    if bp_rule == "BP005":
        items.append({
            "category": "blood_pressure",
            "priority": "urgent_review",
            "title": "Blood pressure needs prompt attention",
            "message": "Seek prompt medical guidance. If concerning symptoms occur, seek emergency medical help.",
        })
    elif bp_rule in {"BP003", "BP004"}:
        items.append({
            "category": "blood_pressure",
            "priority": "follow_up",
            "title": "Review the blood pressure reading",
            "message": "A single measurement cannot diagnose hypertension. Discuss repeat measurements and interpretation with a healthcare professional.",
        })
    elif bp_rule == "BP002":
        items.append({
            "category": "blood_pressure",
            "priority": "maintenance",
            "title": "Keep monitoring blood pressure",
            "message": "Use correct measurement technique and discuss repeated elevated readings with a healthcare professional.",
        })

    if bmi_rule != "B002":
        items.append({
            "category": "bmi",
            "priority": "information",
            "title": "Interpret BMI in context",
            "message": "BMI is a screening measure and does not describe health on its own. Discuss its meaning in the context of age, health history, and other measurements.",
        })

    return items


def analyze_data(data: dict[str, Any]) -> dict[str, Any]:
    """Analyze one patient record and return legacy plus expanded result fields.

    The glucose classification is based only on fasting glucose. BMI, blood
    pressure, age, family history, and insulin remain separate indicators.
    """
    errors = validate_patient_data(data)
    triggered: list[dict[str, str]] = []
    inactive: list[dict[str, str]] = []
    warnings: list[str] = []
    explanations: list[dict[str, str]] = []
    safety_flags: list[dict[str, str]] = []

    if errors:
        block_rule = _rule(
            "C004", "Invalid or missing input blocks analysis", "Validation",
            "Blocked", "; ".join(errors), "Project logic",
        )
        return _empty_result(
            errors, block_rule,
            "Analysis was not performed because one or more inputs are invalid.",
        )

    if data["age"] < 20:
        eligibility_rule = _rule(
            "C003", "Age below project eligibility", "Age", "Not eligible",
            "This educational project is scoped to adults aged 20 years and older.",
            "Project scope",
        )
        return _empty_result(
            ["This project supports adults aged 20 years and older."],
            eligibility_rule,
            "Analysis was not performed because the age is outside the project's defined scope.",
        )

    # These control rules were evaluated and did not block this valid adult record.
    inactive.extend([
        "C003 — Age below project eligibility",
        "C004 — Invalid or missing input blocks analysis",
    ])

    age = int(data["age"])
    glucose = float(data["glucose"])
    glucose_type = data["glucose_type"]
    bmi = float(data["bmi"])
    systolic = int(data["systolic_bp"])
    diastolic = int(data["diastolic_bp"])
    family_history = data["family_history"]
    insulin = data.get("insulin")

    # Age context
    if age >= 45:
        triggered.append(_rule("A001", "Age 45 or older", "Age", "Risk factor present",
            "Age 45 or older is a recognized type 2 diabetes risk factor; it does not determine the glucose category.",
            "CDC Diabetes Risk Factors"))
        inactive.append("A002 — Age below 45")
    else:
        triggered.append(_rule("A002", "Age below 45", "Age", "Context only",
            "The age-related risk factor at 45 years or older is not present; this does not mean there is no risk.",
            "Project logic"))
        inactive.append("A001 — Age 45 or older")

    # Family history context
    if family_history:
        triggered.append(_rule("F001", "Parent or sibling with type 2 diabetes", "Family History",
            "Risk factor present",
            "A parent or sibling with type 2 diabetes is a recognized risk factor. It does not change the glucose category.",
            "CDC Diabetes Risk Factors"))
        inactive.append("F002 — No reported family history")
    else:
        triggered.append(_rule("F002", "No reported parent or sibling with type 2 diabetes",
            "Family History", "Context only",
            "No such family history was reported. This does not rule out risk.",
            "Project logic"))
        inactive.append("F001 — Parent or sibling with type 2 diabetes")

    # BMI: independent indicator
    bmi_label, bmi_rule, bmi_explanation = classify_bmi(bmi)
    triggered.append(_rule(bmi_rule, BMI_RULES[bmi_rule], "BMI", bmi_label, bmi_explanation, BMI_SOURCE))
    inactive.extend(f"{rid} — {name}" for rid, name in BMI_RULES.items() if rid != bmi_rule)

    # Blood pressure: highest category reached by either component
    bp_label, bp_rule, bp_explanation = classify_blood_pressure(systolic, diastolic)
    triggered.append(_rule(bp_rule, BP_RULES[bp_rule], "Blood Pressure", bp_label, bp_explanation, BP_SOURCE))
    inactive.extend(f"{rid} — {name}" for rid, name in BP_RULES.items() if rid != bp_rule)

    if bp_rule == "BP005":
        message = "Blood pressure is in a severe range. Seek prompt medical guidance; if concerning symptoms occur, seek emergency medical help."
        warnings.append(message)
        safety_flags.append({"level": "urgent_review", "indicator": "Blood Pressure", "message": message})

    # Insulin remains optional and display-only
    if insulin is None:
        triggered.append(_rule("I002", "Insulin value not provided", "Insulin", "Not Provided",
            "Insulin is optional and is not used in the final classification.", "Project logic"))
        inactive.append("I001 — Insulin value provided")
    else:
        triggered.append(_rule("I001", "Insulin value provided", "Insulin",
            f"{insulin} µIU/mL (display only)",
            "The value is displayed without a medical category because interpretation depends on context and laboratory methods.",
            "MedlinePlus Insulin Blood Test"))
        inactive.append("I002 — Insulin value not provided")

    # Glucose classification: fasting thresholds are never applied to random/unknown values.
    glucose_class: str | None = None
    glucose_rule: str | None = None
    if glucose_type == "Random":
        triggered.append(_rule("C001", "Random glucose disables fasting thresholds", "Combined Logic",
            "Fasting rules disabled",
            "Random glucose is shown as context only; fasting thresholds were not applied.",
            "Project logic"))
        inactive.append("C002 — Unknown glucose type disables fasting thresholds")
        glucose_message = "Random glucose is shown as context only; fasting thresholds were not applied."
    elif glucose_type == "Unknown":
        triggered.append(_rule("C002", "Unknown glucose type disables fasting thresholds", "Combined Logic",
            "Fasting rules disabled",
            "The measurement type is unknown, so fasting thresholds cannot be safely applied.",
            "Project logic"))
        inactive.append("C001 — Random glucose disables fasting thresholds")
        glucose_message = "Measurement type is unknown; no fasting glucose classification was produced."
    else:  # validation restricts this branch to "Fasting"
        inactive.extend([
            "C001 — Random glucose disables fasting thresholds",
            "C002 — Unknown glucose type disables fasting thresholds",
        ])
        if glucose < 100:
            glucose_class, glucose_rule = "Low Indicator Level", "G001"
            glucose_message = "Fasting glucose is below 100 mg/dL, within the reference range used by this educational system."
            rule_name = GLUCOSE_RULES[glucose_rule]
        elif glucose < 126:
            glucose_class, glucose_rule = "Moderate Indicator Level", "G002"
            glucose_message = "Fasting glucose is 100 to below 126 mg/dL, within the impaired fasting glucose range."
            rule_name = GLUCOSE_RULES[glucose_rule]
        else:
            glucose_class, glucose_rule = "High Indicator Level", "G003"
            glucose_message = "Fasting glucose is 126 mg/dL or higher, reaching a laboratory threshold that requires clinical confirmation. This application does not diagnose."
            rule_name = GLUCOSE_RULES[glucose_rule]

        triggered.append(_rule(glucose_rule, rule_name, "Glucose", glucose_class, glucose_message, GLUCOSE_SOURCE))
        inactive.extend(f"{rid} — {name}" for rid, name in GLUCOSE_RULES.items() if rid != glucose_rule)

        if glucose < 70:
            low_message = (
                "The entered glucose value is below 70 mg/dL. The Low Indicator label does not mean "
                "this low reading is necessarily healthy; seek qualified medical advice, especially if symptoms are present."
            )
            warnings.append(low_message)
            safety_flags.append({"level": "attention", "indicator": "Glucose", "message": low_message})

    # Combined rule C006: compare the component categories, not raw numbers.
    systolic_level = _bp_component_level(systolic, "systolic")
    diastolic_level = _bp_component_level(diastolic, "diastolic")
    if systolic_level != diastolic_level:
        triggered.append(_rule("C006", "Use the higher BP category when numbers differ",
            "Combined Logic", f"Selected: {bp_label}",
            "Systolic and diastolic components reach different categories; the higher category is displayed.",
            "AHA/ACC category structure"))
    else:
        inactive.append("C006 — Use the higher BP category when numbers differ")

    # Combined rule C007: BMI never modifies glucose classification.
    triggered.append(_rule("C007", "BMI remains independent of glucose classification",
        "Combined Logic", "Independent indicator",
        "BMI is reported separately and never adds points or changes the glucose classification.",
        "Project logic"))

    # Combined rule C005: missing insulin never blocks analysis.
    if insulin is None:
        triggered.append(_rule("C005", "Missing insulin does not block analysis",
            "Combined Logic", "Analysis continues",
            "Insulin is optional; its absence does not prevent other indicator analysis.",
            "Project logic"))
    else:
        inactive.append("C005 — Missing insulin does not block analysis")

    indicators = {
        "glucose": {
            "value": glucose, "unit": "mg/dL", "type": glucose_type,
            "classification": glucose_class or "Not classified", "rule_id": glucose_rule,
        },
        "bmi": {"value": bmi, "unit": "kg/m²", "classification": bmi_label, "rule_id": bmi_rule},
        "blood_pressure": {
            "systolic": systolic, "diastolic": diastolic, "unit": "mmHg",
            "classification": bp_label, "rule_id": bp_rule,
        },
        "family_history": {"value": family_history, "display": "Yes" if family_history else "No"},
        "age": {"value": age, "unit": "years"},
        "insulin": {
            "value": insulin, "unit": "µIU/mL",
            "display": "Not Provided" if insulin is None else str(insulin),
        },
    }

    if glucose_class is None:
        final_label = "Insufficient Data"
        summary = glucose_message
    else:
        final_label = glucose_class
        summary = (
            f"The final classification is based only on fasting glucose ({glucose:g} mg/dL). "
            "BMI, blood pressure, age, family history, and insulin are reported separately "
            "and do not change this classification."
        )

    # Explainability records are intentionally separate from the legacy rule objects.
    for item in triggered:
        explanations.append({
            "rule_id": item["rule_id"],
            "title": item["name"],
            "why": item["explanation"],
            "effect": item["result"],
        })

    quality_notes = []
    if glucose_type != "Fasting":
        quality_notes.append("Glucose measurement type does not support fasting-threshold classification.")
    if insulin is None:
        quality_notes.append("Insulin is optional and was not supplied.")
    if glucose_type == "Fasting":
        quality_notes.append("Fasting classification assumes the measurement was collected after the required fasting period.")
    data_quality = {
        "status": "valid_with_notes" if quality_notes else "valid",
        "issues": [],
        "notes": quality_notes,
        "required_fields_valid": True,
    }

    recommendations = _build_recommendations(glucose_class, glucose, glucose_type, bp_rule, bmi_rule)

    return {
        # Legacy keys retained for compatibility with the existing dashboard/report.
        "valid": True,
        "errors": [],
        "classification": glucose_class,
        "classification_label": final_label,
        "triggered_rules": triggered,
        "not_triggered_rules": inactive,
        "warnings": warnings,
        "indicators": indicators,
        "summary": summary,
        # Expanded V2 fields.
        "engine_version": ENGINE_VERSION,
        "data_quality": data_quality,
        "explanations": explanations,
        "recommendations": recommendations,
        "safety_flags": safety_flags,
        "rule_audit": {
            "triggered": triggered,
            "not_triggered": [_inactive(
                item.split(" — ", 1)[0],
                item.split(" — ", 1)[1] if " — " in item else item,
            ) for item in inactive],
            "total_project_rules": RULE_COUNT,
            "evaluated_triggered_count": len(triggered),
            "evaluated_not_triggered_count": len(inactive),
        },
        "analysis_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
