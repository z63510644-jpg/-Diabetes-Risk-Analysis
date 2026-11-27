# Diabetes Risk Analysis

An educational, adult-only (20+) Python + Streamlit application that demonstrates a transparent rule-based analysis of selected health indicators. It does **not** diagnose diabetes, predict disease, or calculate a probability.

## Features

- Required inputs: age, glucose, glucose measurement type, BMI, systolic/diastolic blood pressure, and family history.
- Optional insulin value (display only; not used in classification).
- 27 documented rules: glucose (3), BMI (6), blood pressure (5), family history (2), age (2), insulin (2), combined logic (7).
- Final Low / Moderate / High Indicator Level is based only on fasting glucose. Random/Unknown glucose measurements are not compared with fasting thresholds.
- Independent BMI and blood-pressure classifications.
- Detailed report, charts, input validation, and synthetic demonstration data.
- Automated tests using Python's built-in `unittest`.

## Project files

- `app.py`: Streamlit interface.
- `validation.py`: input validation and technical guardrails.
- `rules.py`: metadata for the 27 rules.
- `analysis.py`: rule engine and classification logic.
- `report.py`: detailed report builder.
- `charts.py`: Matplotlib charts.
- `test_cases.py`: automated tests and synthetic test cases.
- `requirements.txt`: dependencies.
- `.streamlit/config.toml`: light theme and server settings.
- `.replit`: Replit run configuration.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 5000
```

## Run on Replit

1. Create a Python Repl.
2. Upload the complete project folder contents, including `.replit` and `.streamlit/config.toml`.
3. Install `streamlit` and `matplotlib` from Replit's Dependencies tool, or run `upm add streamlit matplotlib` in the Shell. If the Repl is configured for pip, `python -m pip install -r requirements.txt` also works.
4. Run the Repl. The configured command starts Streamlit on `0.0.0.0:5000`.
5. For deployment, the `.replit` file includes a Cloud Run target and maps local port 5000 to external port 80. Review the current deployment prompts before publishing.

## Run tests

```bash
python -m unittest -v test_cases.py
```

The tests use artificial inputs only. A passing software test verifies the code's expected behavior; it does not validate a medical diagnosis or prove clinical accuracy.

## Rule summary

### Fasting glucose (ADA 2026)
- Below 100 mg/dL: Low Indicator Level.
- 100 to below 126 mg/dL: Moderate Indicator Level.
- 126 mg/dL or above: High Indicator Level.

The 126 mg/dL threshold is a diagnostic threshold in clinical criteria, not a diagnosis made by this application. In the absence of unequivocal hyperglycemia, clinical diagnosis requires confirmation. Fasting means no caloric intake for at least 8 hours.

A separate safety notice is displayed for glucose below 70 mg/dL; the project's Low label must not be interpreted as meaning that every low numerical reading is healthy. ADA 2026 describes glucose below 70 mg/dL as clinically important in hypoglycemia assessment: https://doi.org/10.2337/dc26-s006

### BMI (CDC adult categories)
- Below 18.5: Underweight.
- 18.5 to below 25: Healthy Weight.
- 25 to below 30: Overweight.
- 30 to below 35: Class 1 Obesity.
- 35 to below 40: Class 2 Obesity.
- 40 or above: Class 3 Obesity.

BMI is a screening measure, not a diagnosis.

### Blood pressure (2025 AHA/ACC categories)
- Normal: systolic below 120 AND diastolic below 80.
- Elevated: systolic 120–129 AND diastolic below 80.
- Stage 1: systolic 130–139 OR diastolic 80–89.
- Stage 2: systolic 140 or above OR diastolic 90 or above.
- Severe-range safety notice: systolic above 180 OR diastolic above 120.

A single reading does not establish a diagnosis. The application reports the higher category reached by either number.

## Sources

1. American Diabetes Association, *Standards of Care in Diabetes—2026, Section 2: Diagnosis and Classification of Diabetes*: https://diabetesjournals.org/care/article/49/Supplement_1/S27/163926/2-Diagnosis-and-Classification-of-Diabetes
2. CDC, *Adult BMI Categories*: https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html
3. American Heart Association / American College of Cardiology, *2025 High Blood Pressure Guideline*: https://professional.heart.org/en/science-news/2025-high-blood-pressure-guideline/top-things-to-know
4. CDC, *Diabetes Risk Factors*: https://www.cdc.gov/diabetes/risk-factors/
5. MedlinePlus, *Insulin in Blood Test*: https://medlineplus.gov/lab-tests/insulin-in-blood/
6. American Diabetes Association, *Standards of Care in Diabetes—2026, Section 6: Glycemic Goals, Hypoglycemia, and Hyperglycemic Crises*: https://doi.org/10.2337/dc26-s006
7. Streamlit, *Command-line interface*: https://docs.streamlit.io/develop/api-reference/cli
8. Streamlit, *Configuration options*: https://docs.streamlit.io/develop/concepts/configuration/options
9. Replit, *Project configuration*: https://docs.replit.com/references/project-setup/configuration
10. Replit, *Ports*: https://docs.replit.com/references/project-setup/ports

Sources reviewed: 27 November 2026.

## Important limitations

- No machine learning, weighted score, probability, or diagnostic conclusion is used.
- Random glucose is shown without fasting classification because this application does not collect symptoms or perform confirmatory clinical testing.
- Insulin is optional and displayed only; its interpretation depends on clinical context and laboratory methods.
- Technical input ranges are software guardrails only, not medical reference ranges.
- The synthetic demo chart is an artificial illustration, not epidemiological data.
