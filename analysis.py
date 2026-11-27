"""Rule-based analysis engine. No machine learning or weighted scoring."""
from __future__ import annotations

from typing import Any
from validation import validate_patient_data

GLUCOSE_SOURCE = "ADA Standards of Care in Diabetes—2026"
BMI_SOURCE = "CDC Adult BMI Categories"
BP_SOURCE = "2025 AHA/ACC Blood Pressure Guideline"


def _rule(rule_id: str, name: str, indicator: str, result: str, explanation: str, source: str) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "name": name,
        "indicator": indicator,
        "result": result,
        "explanation": explanation,
        "source": source,
    }


def classify_bmi(bmi: float) -> tuple[str, str, str]:
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
    """Return the highest category reached by either systolic or diastolic value."""
    if systolic > 180 or diastolic > 120:
        return "Severe Range", "BP005", "The reading is above 180 systolic or above 120 diastolic. Repeat the measurement as directed by a healthcare professional and seek prompt medical guidance. If concerning symptoms occur, seek emergency medical help."
    if systolic >= 140 or diastolic >= 90:
        return "Stage 2 Range", "BP004", "At least one value is in the Stage 2 range. A single reading does not establish a diagnosis."
    if systolic >= 130 or diastolic >= 80:
        return "Stage 1 Range", "BP003", "At least one value is in the Stage 1 range. A single reading does not establish a diagnosis."
    if 120 <= systolic <= 129 and diastolic < 80:
        return "Elevated Range", "BP002", "Systolic pressure is 120–129 mm Hg and diastolic pressure is below 80 mm Hg."
    return "Normal Range", "BP001", "Both values are below 120/80 mm Hg."


def analyze_data(data: dict[str, Any]) -> dict[str, Any]:
    errors = validate_patient_data(data)
    triggered: list[dict[str, str]] = []
    not_triggered: list[dict[str, str]] = []
    warnings: list[str] = []

    if errors:
        triggered.append(_rule("C004", "Invalid or missing input blocks analysis", "Validation", "Blocked", "; ".join(errors), "Project logic"))
        return {
            "valid": False, "errors": errors, "classification": None,
            "classification_label": "Insufficient Data", "triggered_rules": triggered,
            "not_triggered_rules": not_triggered, "warnings": warnings,
            "indicators": {}, "summary": "Analysis was not performed because one or more inputs are invalid.",
        }

    if data["age"] < 20:
        triggered.append(_rule("C003", "Age below project eligibility", "Age", "Not eligible", "This educational project is scoped to adults aged 20 years and older.", "Project scope"))
        return {
            "valid": False, "errors": ["This project supports adults aged 20 years and older."],
            "classification": None, "classification_label": "Insufficient Data",
            "triggered_rules": triggered, "not_triggered_rules": not_triggered,
            "warnings": warnings, "indicators": {},
            "summary": "Analysis was not performed because the age is outside the project's defined scope.",
        }

    # Age context
    if data["age"] >= 45:
        triggered.append(_rule("A001", "Age 45 or older", "Age", "Risk factor present", "Age 45 or older is a recognized type 2 diabetes risk factor; it does not determine the glucose category.", "CDC Diabetes Risk Factors"))
        not_triggered.append("A002 — Age below 45")
    else:
        triggered.append(_rule("A002", "Age below 45", "Age", "Context only", "The age-related risk factor at 45 years or older is not present; this does not mean there is no risk.", "Project logic"))
        not_triggered.append("A001 — Age 45 or older")

    # Family history context
    if data["family_history"]:
        triggered.append(_rule("F001", "Parent or sibling with type 2 diabetes", "Family History", "Risk factor present", "A parent or sibling with type 2 diabetes is a recognized risk factor. It does not change the glucose category.", "CDC Diabetes Risk Factors"))
        not_triggered.append("F002 — No reported family history")
    else:
        triggered.append(_rule("F002", "No reported parent or sibling with type 2 diabetes", "Family History", "Context only", "No such family history was reported. This does not rule out risk.", "Project logic"))
        not_triggered.append("F001 — Parent or sibling with type 2 diabetes")

    # BMI category
    bmi_label, bmi_rule, bmi_explanation = classify_bmi(float(data["bmi"]))
    bmi_rule_names = {
        "B001": "Underweight BMI category", "B002": "Healthy-weight BMI category",
        "B003": "Overweight BMI category", "B004": "Class 1 obesity BMI category",
        "B005": "Class 2 obesity BMI category", "B006": "Class 3 obesity BMI category",
    }
    triggered.append(_rule(bmi_rule, bmi_rule_names[bmi_rule], "BMI", bmi_label, bmi_explanation, BMI_SOURCE))
    for rid, name in bmi_rule_names.items():
        if rid != bmi_rule:
            not_triggered.append(f"{rid} — {name}")

    # Blood pressure category
    bp_label, bp_rule, bp_explanation = classify_blood_pressure(int(data["systolic_bp"]), int(data["diastolic_bp"]))
    bp_rule_names = {
        "BP001": "Normal blood pressure category", "BP002": "Elevated blood pressure category",
        "BP003": "Stage 1 hypertension range", "BP004": "Stage 2 hypertension range",
        "BP005": "Severe blood pressure range",
    }
    triggered.append(_rule(bp_rule, bp_rule_names[bp_rule], "Blood Pressure", bp_label, bp_explanation, BP_SOURCE))
    for rid, name in bp_rule_names.items():
        if rid != bp_rule:
            not_triggered.append(f"{rid} — {name}")
    if bp_rule == "BP005":
        warnings.append("Blood pressure is in a severe range. Seek prompt medical guidance; if concerning symptoms occur, seek emergency medical help.")

    # Insulin display only
    if data.get("insulin") is None:
        triggered.append(_rule("I002", "Insulin value not provided", "Insulin", "Not Provided", "Insulin is optional and is not used in the final classification.", "Project logic"))
        not_triggered.append("I001 — Insulin value provided")
    else:
        triggered.append(_rule("I001", "Insulin value provided", "Insulin", f"{data['insulin']} µIU/mL (display only)", "The value is displayed without a medical category because interpretation depends on context and laboratory methods.", "MedlinePlus Insulin Blood Test"))
        not_triggered.append("I002 — Insulin value not provided")

    # Combined logic
    if data["glucose_type"] == "Random":
        triggered.append(_rule("C001", "Random glucose disables fasting thresholds", "Combined Logic", "Fasting rules disabled", "Random glucose is not compared with fasting thresholds in this project.", "Project logic"))
        not_triggered.append("C002 — Unknown glucose type disables fasting thresholds")
        glucose_class = None
        glucose_rule = None
        glucose_message = "Random glucose is shown as context only; fasting thresholds were not applied."
    elif data["glucose_type"] == "Unknown":
        triggered.append(_rule("C002", "Unknown glucose type disables fasting thresholds", "Combined Logic", "Fasting rules disabled", "The measurement type is unknown, so fasting thresholds cannot be safely applied.", "Project logic"))
        not_triggered.append("C001 — Random glucose disables fasting thresholds")
        glucose_class = None
        glucose_rule = None
        glucose_message = "Measurement type is unknown; no fasting glucose classification was produced."
    else:
        not_triggered.extend([
            "C001 — Random glucose disables fasting thresholds",
            "C002 — Unknown glucose type disables fasting thresholds",
        ])
        glucose = float(data["glucose"])
        if glucose < 100:
            glucose_class, glucose_rule = "Low Indicator Level", "G001"
            explanation = "Fasting glucose is below 100 mg/dL, within the reference range used by this educational system."
            rule_name = "Fasting glucose below 100"
        elif glucose < 126:
            glucose_class, glucose_rule = "Moderate Indicator Level", "G002"
            explanation = "Fasting glucose is 100 to below 126 mg/dL, within the impaired fasting glucose range."
            rule_name = "Fasting glucose 100 to below 126"
        else:
            glucose_class, glucose_rule = "High Indicator Level", "G003"
            explanation = "Fasting glucose is 126 mg/dL or higher, reaching a laboratory diagnostic threshold that requires clinical confirmation. This application does not diagnose."
            rule_name = "Fasting glucose 126 or above"
        triggered.append(_rule(glucose_rule, rule_name, "Glucose", glucose_class, explanation, GLUCOSE_SOURCE))
        for rid, name in {"G001": "Fasting glucose below 100", "G002": "Fasting glucose 100 to below 126", "G003": "Fasting glucose 126 or above"}.items():
            if rid != glucose_rule:
                not_triggered.append(f"{rid} — {name}")
        glucose_message = explanation

        # Separate low-glucose safety note; it does not change the project's category.
        if glucose < 70:
            warnings.append("The entered glucose value is below 70 mg/dL. The Low Indicator label does not mean this low reading is necessarily healthy; seek qualified medical advice, especially if symptoms are present.")

    # Combined rule: trigger C006 only when systolic and diastolic components
    # reach different levels; the overall BP category remains the higher one.
    systolic_level = 4 if data["systolic_bp"] > 180 else 3 if data["systolic_bp"] >= 140 else 2 if data["systolic_bp"] >= 130 else 1 if data["systolic_bp"] >= 120 else 0
    diastolic_level = 4 if data["diastolic_bp"] > 120 else 3 if data["diastolic_bp"] >= 90 else 2 if data["diastolic_bp"] >= 80 else 0
    if systolic_level != diastolic_level:
        triggered.append(_rule("C006", "Use the higher BP category when numbers differ", "Combined Logic", f"Selected: {bp_label}", "Systolic and diastolic components reach different categories; the higher category is displayed.", "AHA/ACC category structure"))
    else:
        not_triggered.append("C006 — Use the higher BP category when numbers differ")
    # Combined rule: BMI never modifies glucose category.
    triggered.append(_rule("C007", "BMI remains independent of glucose classification", "Combined Logic", "Independent indicator", "BMI is reported separately and never adds points or changes the glucose classification.", "Project logic"))
    # Missing insulin never blocks analysis.
    if data.get("insulin") is None:
        triggered.append(_rule("C005", "Missing insulin does not block analysis", "Combined Logic", "Analysis continues", "Insulin is optional; its absence does not prevent other indicator analysis.", "Project logic"))
    else:
        not_triggered.append("C005 — Missing insulin does not block analysis")

    indicators = {
        "glucose": {"value": data["glucose"], "unit": "mg/dL", "type": data["glucose_type"], "classification": glucose_class or "Not classified", "rule_id": glucose_rule},
        "bmi": {"value": data["bmi"], "unit": "kg/m²", "classification": bmi_label, "rule_id": bmi_rule},
        "blood_pressure": {"systolic": data["systolic_bp"], "diastolic": data["diastolic_bp"], "unit": "mmHg", "classification": bp_label, "rule_id": bp_rule},
        "family_history": {"value": data["family_history"], "display": "Yes" if data["family_history"] else "No"},
        "age": {"value": data["age"], "unit": "years"},
        "insulin": {"value": data.get("insulin"), "unit": "µIU/mL", "display": "Not Provided" if data.get("insulin") is None else str(data["insulin"])},
    }

    if glucose_class is None:
        final_label = "Insufficient Data"
        summary = glucose_message
    else:
        final_label = glucose_class
        summary = f"The final classification is based only on fasting glucose ({data['glucose']} mg/dL). BMI, blood pressure, age, family history, and insulin are reported separately and do not change this classification."

    return {
        "valid": True, "errors": [], "classification": glucose_class,
        "classification_label": final_label, "triggered_rules": triggered,
        "not_triggered_rules": not_triggered, "warnings": warnings,
        "indicators": indicators, "summary": summary,
    }
