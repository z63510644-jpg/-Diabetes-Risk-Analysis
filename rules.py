"""Complete, auditable metadata for all 27 project rules.

Medical reference ranges are educational references, not diagnostic decisions
made by this application. Logic rules are explicitly identified as project logic.
"""
from __future__ import annotations

RULES = [
    # A. Individual rules — Glucose (3)
    {"id":"G001", "name":"Fasting glucose below 100", "condition":"glucose_type == 'Fasting' and glucose < 100", "indicator":"Glucose", "outcome":"Low Indicator Level", "explanation":"Fasting glucose is below 100 mg/dL, within the reference range used by this educational system.", "source":"ADA Standards of Care in Diabetes—2026"},
    {"id":"G002", "name":"Fasting glucose 100 to below 126", "condition":"glucose_type == 'Fasting' and 100 <= glucose < 126", "indicator":"Glucose", "outcome":"Moderate Indicator Level", "explanation":"Fasting glucose is within the impaired fasting glucose range of 100–125 mg/dL.", "source":"ADA Standards of Care in Diabetes—2026"},
    {"id":"G003", "name":"Fasting glucose 126 or above", "condition":"glucose_type == 'Fasting' and glucose >= 126", "indicator":"Glucose", "outcome":"High Indicator Level", "explanation":"Fasting glucose has reached a clinical diagnostic threshold; confirmation is required and this application does not diagnose.", "source":"ADA Standards of Care in Diabetes—2026"},
    # BMI (6)
    {"id":"B001", "name":"Underweight BMI category", "condition":"bmi < 18.5", "indicator":"BMI", "outcome":"Underweight", "explanation":"Adult BMI is below 18.5 kg/m²; BMI is a screening measure, not a diagnosis.", "source":"CDC Adult BMI Categories"},
    {"id":"B002", "name":"Healthy-weight BMI category", "condition":"18.5 <= bmi < 25", "indicator":"BMI", "outcome":"Healthy Weight", "explanation":"Adult BMI is from 18.5 to below 25 kg/m²; BMI is a screening measure, not a diagnosis.", "source":"CDC Adult BMI Categories"},
    {"id":"B003", "name":"Overweight BMI category", "condition":"25 <= bmi < 30", "indicator":"BMI", "outcome":"Overweight", "explanation":"Adult BMI is from 25 to below 30 kg/m²; BMI is a screening measure, not a diagnosis.", "source":"CDC Adult BMI Categories"},
    {"id":"B004", "name":"Class 1 obesity BMI category", "condition":"30 <= bmi < 35", "indicator":"BMI", "outcome":"Class 1 Obesity", "explanation":"Adult BMI is from 30 to below 35 kg/m²; BMI is a screening measure, not a diagnosis.", "source":"CDC Adult BMI Categories"},
    {"id":"B005", "name":"Class 2 obesity BMI category", "condition":"35 <= bmi < 40", "indicator":"BMI", "outcome":"Class 2 Obesity", "explanation":"Adult BMI is from 35 to below 40 kg/m²; BMI is a screening measure, not a diagnosis.", "source":"CDC Adult BMI Categories"},
    {"id":"B006", "name":"Class 3 obesity BMI category", "condition":"bmi >= 40", "indicator":"BMI", "outcome":"Class 3 Obesity", "explanation":"Adult BMI is 40 kg/m² or higher; BMI is a screening measure, not a diagnosis.", "source":"CDC Adult BMI Categories"},
    # Blood pressure (5)
    {"id":"BP001", "name":"Normal blood pressure category", "condition":"systolic < 120 and diastolic < 80, with no higher category met", "indicator":"Blood Pressure", "outcome":"Normal Range", "explanation":"Both values are below 120/80 mmHg.", "source":"2025 AHA/ACC Blood Pressure Guideline"},
    {"id":"BP002", "name":"Elevated blood pressure category", "condition":"120 <= systolic <= 129 and diastolic < 80, with no higher category met", "indicator":"Blood Pressure", "outcome":"Elevated Range", "explanation":"Systolic pressure is 120–129 mmHg and diastolic pressure is below 80 mmHg.", "source":"2025 AHA/ACC Blood Pressure Guideline"},
    {"id":"BP003", "name":"Stage 1 hypertension range", "condition":"130 <= systolic <= 139 or 80 <= diastolic <= 89, unless a higher category is met", "indicator":"Blood Pressure", "outcome":"Stage 1 Range", "explanation":"At least one value is in the Stage 1 range; a single reading does not establish a diagnosis.", "source":"2025 AHA/ACC Blood Pressure Guideline"},
    {"id":"BP004", "name":"Stage 2 hypertension range", "condition":"systolic >= 140 or diastolic >= 90, unless severe range is met", "indicator":"Blood Pressure", "outcome":"Stage 2 Range", "explanation":"At least one value is in the Stage 2 range; a single reading does not establish a diagnosis.", "source":"2025 AHA/ACC Blood Pressure Guideline"},
    {"id":"BP005", "name":"Severe blood pressure range", "condition":"systolic > 180 or diastolic > 120", "indicator":"Blood Pressure", "outcome":"Severe Range alert", "explanation":"The entered value is above the severe-range threshold; seek prompt medical guidance, and seek emergency help if concerning symptoms occur.", "source":"American Heart Association blood pressure guidance"},
    # Family history (2)
    {"id":"F001", "name":"Parent or sibling with type 2 diabetes", "condition":"family_history is True", "indicator":"Family History", "outcome":"Risk factor present", "explanation":"A parent or sibling with type 2 diabetes is a recognized risk factor; it does not change glucose classification.", "source":"CDC Diabetes Risk Factors"},
    {"id":"F002", "name":"No reported parent or sibling with type 2 diabetes", "condition":"family_history is False", "indicator":"Family History", "outcome":"No reported family history", "explanation":"No such family history was reported; this does not rule out risk.", "source":"Project logic; question scoped to CDC risk-factor wording"},
    # Age (2)
    {"id":"A001", "name":"Age 45 or older", "condition":"age >= 45", "indicator":"Age", "outcome":"Age-related risk factor present", "explanation":"Age 45 or older is a recognized type 2 diabetes risk factor; it does not determine glucose classification.", "source":"CDC Diabetes Risk Factors"},
    {"id":"A002", "name":"Age below 45", "condition":"20 <= age < 45", "indicator":"Age", "outcome":"Age-related risk factor not present", "explanation":"The age-related factor at 45 or older is not present; this does not mean there is no risk.", "source":"Project logic"},
    # Insulin (2)
    {"id":"I001", "name":"Insulin value provided", "condition":"insulin is not None", "indicator":"Insulin", "outcome":"Display entered value only", "explanation":"Insulin is displayed without a category because interpretation depends on clinical context and laboratory methods.", "source":"MedlinePlus Insulin in Blood Test"},
    {"id":"I002", "name":"Insulin value not provided", "condition":"insulin is None", "indicator":"Insulin", "outcome":"Not Provided", "explanation":"Insulin is optional and its absence does not block other analysis.", "source":"Project logic"},
    # Combined logic (7)
    {"id":"C001", "name":"Random glucose disables fasting thresholds", "condition":"glucose_type == 'Random'", "indicator":"Combined Logic", "outcome":"Do not apply G001–G003", "explanation":"Random glucose is shown as context only; fasting thresholds are not applied.", "source":"Project logic; ADA test criteria distinguish random from fasting"},
    {"id":"C002", "name":"Unknown glucose type disables fasting thresholds", "condition":"glucose_type == 'Unknown'", "indicator":"Combined Logic", "outcome":"Insufficient Data for glucose classification", "explanation":"The measurement type is unknown, so fasting thresholds cannot be applied.", "source":"Project logic"},
    {"id":"C003", "name":"Age below project eligibility", "condition":"age < 20", "indicator":"Eligibility", "outcome":"Stop analysis", "explanation":"The project is scoped to adults aged 20 years and older.", "source":"Project scope; CDC adult BMI categories apply from age 20"},
    {"id":"C004", "name":"Invalid or missing input blocks analysis", "condition":"one or more required values are missing or any value fails validation", "indicator":"Validation", "outcome":"Stop analysis", "explanation":"Do not produce an analysis report from invalid or incomplete required inputs.", "source":"Project logic"},
    {"id":"C005", "name":"Missing insulin does not block analysis", "condition":"insulin is None and all required fields are valid", "indicator":"Combined Logic", "outcome":"Continue analysis", "explanation":"Insulin is optional and is not required for the other indicator analyses.", "source":"Project logic"},
    {"id":"C006", "name":"Use the higher BP category when numbers differ", "condition":"systolic and diastolic values reach different categories", "indicator":"Combined Logic", "outcome":"Display the higher category", "explanation":"The more severe category reached by either systolic or diastolic pressure is displayed.", "source":"AHA/ACC category structure"},
    {"id":"C007", "name":"BMI remains independent of glucose classification", "condition":"BMI has a valid adult category", "indicator":"Combined Logic", "outcome":"Do not change glucose classification", "explanation":"BMI is reported separately and never adds points or changes the glucose classification.", "source":"Project logic"},
]

RULE_COUNT = len(RULES)
