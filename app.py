from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from analysis import analyze_data
from charts import glucose_reference_chart, indicator_bar_chart, triggered_rules_chart, synthetic_demo_chart, bmi_reference_chart
from report import build_report
from rules import RULE_COUNT, RULES
from test_cases import run_test_case_table

st.set_page_config(
    page_title="Diabetes Risk Analysis",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.stApp { background: #f5f7fb; }
.block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
.hero { background: linear-gradient(135deg,#ffffff 0%,#f1f6ff 100%); border: 1px solid #e7edf5; border-radius: 24px; padding: 30px 32px; margin-bottom: 22px; box-shadow: 0 8px 28px rgba(31,55,88,.055); }
.eyebrow { color:#6481a6; font-size:11px; font-weight:700; letter-spacing:2px; text-transform:uppercase; }
.hero h1 { color:#152238; font-size:34px; letter-spacing:-1.3px; margin:8px 0 7px 0; }
.hero p { color:#64748b; margin:0; font-size:14px; }
.section-card { background:#fff; border:1px solid #e8edf4; border-radius:20px; padding:22px 24px; box-shadow:0 5px 20px rgba(31,55,88,.035); margin-bottom:18px; }
.section-title { color:#17253b; font-weight:700; font-size:18px; margin-bottom:4px; }
.section-subtitle { color:#8492a6; font-size:12px; margin-bottom:18px; }
.result-card { background:#fff; border:1px solid #e7edf5; border-radius:20px; padding:22px; box-shadow:0 6px 22px rgba(31,55,88,.045); }
.small-muted { color:#718096; font-size:12px; }
.disclaimer { background:#f0f5fb; border:1px solid #dce7f3; border-radius:14px; padding:14px 16px; color:#52657e; font-size:12px; }
div.stButton > button[kind="primary"] { background:#246fd1; border:0; border-radius:12px; min-height:46px; font-weight:650; }
[data-testid="stMetric"] { background:#f8fafc; border:1px solid #e8edf4; padding:14px; border-radius:14px; }
[data-testid="stExpander"] { background:#fff; border:1px solid #e8edf4; border-radius:14px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Educational Rule-Based Analysis System</div>
  <h1>Diabetes Risk Analysis</h1>
  <p>Understand selected health indicators through transparent rules and clear explanations.</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Educational use only. This application does not diagnose diabetes, predict disease, "
    "or calculate a probability of developing diabetes. It is designed for adults aged 20+."
)

DEMO_CASES = {
    "Custom input": {"age": 35, "glucose": 90.0, "glucose_type": "Fasting", "bmi": 22.0, "systolic_bp": 118, "diastolic_bp": 76, "insulin": None, "family_history": False},
    "Synthetic example — Low": {"age": 32, "glucose": 92.0, "glucose_type": "Fasting", "bmi": 23.4, "systolic_bp": 116, "diastolic_bp": 74, "insulin": None, "family_history": False},
    "Synthetic example — Moderate": {"age": 48, "glucose": 110.0, "glucose_type": "Fasting", "bmi": 28.1, "systolic_bp": 132, "diastolic_bp": 84, "insulin": 12.0, "family_history": True},
    "Synthetic example — High": {"age": 56, "glucose": 138.0, "glucose_type": "Fasting", "bmi": 31.2, "systolic_bp": 145, "diastolic_bp": 92, "insulin": None, "family_history": True},
}

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">01 · Input Health Indicators</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Enter the requested values. Technical input limits are validation guardrails, not medical thresholds.</div>', unsafe_allow_html=True)
example_choice = st.selectbox("Optional synthetic example", list(DEMO_CASES.keys()), help="Examples are artificial and are provided only to demonstrate the interface.")
defaults = DEMO_CASES[example_choice]

with st.form("analysis_form", clear_on_submit=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age (years)", min_value=1, max_value=120, value=int(defaults["age"]), step=1)
        glucose = st.number_input("Glucose (mg/dL)", min_value=0.0, max_value=600.0, value=float(defaults["glucose"]), step=1.0)
        glucose_type = st.selectbox("Glucose measurement type", ["Fasting", "Random", "Unknown"], index=["Fasting", "Random", "Unknown"].index(defaults["glucose_type"]), help="Fasting means no caloric intake for at least 8 hours.")
    with c2:
        bmi = st.number_input("BMI (kg/m²)", min_value=0.0, max_value=80.0, value=float(defaults["bmi"]), step=0.1, format="%.1f")
        systolic = st.number_input("Systolic blood pressure (mmHg)", min_value=0, max_value=300, value=int(defaults["systolic_bp"]), step=1)
        diastolic = st.number_input("Diastolic blood pressure (mmHg)", min_value=0, max_value=200, value=int(defaults["diastolic_bp"]), step=1)
    with c3:
        insulin_provided = st.checkbox("Enter an insulin value", value=defaults["insulin"] is not None)
        insulin = st.number_input("Insulin (µIU/mL)", min_value=0.0, max_value=1000.0, value=float(defaults["insulin"] if defaults["insulin"] is not None else 0.0), step=0.1, disabled=not insulin_provided, help="Optional. Displayed only; not used in the final classification.")
        family_history = st.radio("Parent or sibling with Type 2 Diabetes?", ["No", "Yes"], index=1 if defaults["family_history"] else 0, horizontal=True)
    submitted = st.form_submit_button("Analyze Indicators", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if submitted:
    patient_data = {
        "age": int(age), "glucose": float(glucose), "glucose_type": glucose_type,
        "bmi": float(bmi), "systolic_bp": int(systolic), "diastolic_bp": int(diastolic),
        "insulin": float(insulin) if insulin_provided else None,
        "family_history": family_history == "Yes",
    }
    st.session_state["patient_data"] = patient_data
    st.session_state["analysis_result"] = analyze_data(patient_data)

if "analysis_result" in st.session_state:
    data = st.session_state["patient_data"]
    result = st.session_state["analysis_result"]
    report = build_report(data, result)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">02 · Analysis Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The classification below is based on the fasting glucose rule only.</div>', unsafe_allow_html=True)
    if not result["valid"]:
        st.error("Analysis could not be completed.")
        for error in result["errors"]:
            st.write(f"• {error}")
    else:
        label = result["classification_label"]
        if label == "Low Indicator Level":
            st.success(label)
        elif label == "Moderate Indicator Level":
            st.warning(label)
        elif label == "High Indicator Level":
            st.error(label)
        else:
            st.info(label)
        st.write(result["summary"])
        for warning in result["warnings"]:
            st.warning(warning)
        m1, m2, m3 = st.columns(3)
        m1.metric("Glucose", f"{data['glucose']:g} mg/dL", data["glucose_type"])
        m2.metric("BMI", f"{data['bmi']:.1f}", result["indicators"]["bmi"]["classification"])
        m3.metric("Blood Pressure", f"{data['systolic_bp']}/{data['diastolic_bp']}", result["indicators"]["blood_pressure"]["classification"])
    st.markdown('</div>', unsafe_allow_html=True)

    if result["valid"]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">03 · Charts & Indicator Overview</div>', unsafe_allow_html=True)
        left, right = st.columns(2)
        with left:
            st.markdown("**Glucose reference bands**")
            fig = glucose_reference_chart(data["glucose"], data["glucose_type"])
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with right:
            st.markdown("**Blood pressure values**")
            fig = indicator_bar_chart(data)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        st.markdown("**BMI adult reference bands**")
        fig = bmi_reference_chart(data["bmi"])
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.markdown("**Triggered rules by indicator**")
        fig = triggered_rules_chart(result)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">04 · Detailed Report</div>', unsafe_allow_html=True)
        st.markdown("**Final Classification**")
        st.write(report["classification"])
        st.markdown("**Analysis Summary**")
        st.write(report["summary"])

        st.markdown("**Triggered Rules**")
        if report["triggered_rules"]:
            st.dataframe([
                {"Rule ID": r["rule_id"], "Rule Name": r["name"], "Indicator": r["indicator"], "Result": r["result"], "Explanation": r["explanation"], "Source": r["source"]}
                for r in report["triggered_rules"]
            ], use_container_width=True, hide_index=True)
        else:
            st.write("No rules were triggered.")

        st.markdown("**Contributing Indicators**")
        for item in report["contributing_indicators"]:
            st.write(f"• {item}")

        st.markdown("**Independent Contextual Indicators**")
        for item in report.get("contextual_indicators", []):
            st.write(f"• {item}")

        st.markdown("**Indicators / Rules With No Triggered Rule**")
        for item in report["indicators_without_triggered_rules"]:
            st.write(f"• {item}")

        st.markdown("**Input Data Summary**")
        st.json(data)

        st.markdown("**General Educational Recommendations**")
        for item in report["recommendations"]:
            st.write(f"• {item}")

        st.markdown("**Scientific Disclaimer**")
        st.markdown(f'<div class="disclaimer">{report["disclaimer"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander(f"Complete rule reference ({RULE_COUNT} rules)"):
            st.caption("Each rule lists its ID, condition, indicator, outcome, explanation, and source. Project-logic rules are not medical thresholds.")
            st.dataframe(RULES, use_container_width=True, hide_index=True)

        with st.expander("Synthetic demo dataset statistics"):
            st.caption("These are fixed artificial demonstration counts (30 records), not real-world prevalence, clinical evidence, or population statistics.")
            fig = synthetic_demo_chart()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with st.expander("Automated test-case results"):
            st.caption("This table is generated by executing the project's synthetic test cases. PASS means the actual software output matched the expected software output.")
            st.dataframe(run_test_case_table(), use_container_width=True, hide_index=True)

st.markdown('<div class="small-muted" style="text-align:center;padding:22px 0 6px 0;">Diabetes Risk Analysis · Educational project · 27 transparent rules</div>', unsafe_allow_html=True)
