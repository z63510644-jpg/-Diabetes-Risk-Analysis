from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from analysis import analyze_data
from charts import (
    glucose_reference_chart, indicator_bar_chart, triggered_rules_chart,
    synthetic_demo_chart, bmi_reference_chart,
)
from report import build_report
from rules import RULE_COUNT, RULES
from test_cases import run_test_case_table


st.set_page_config(
    page_title="GlycoSense | Diabetes Risk Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Cairo:wght@400;500;600;700;800&display=swap');
:root{color-scheme:light;--ink:#17243a;--blue:#2864dc;--line:#e7edf5;--canvas:#f4f7fb}
html,body,[data-testid="stAppViewContainer"],.stApp,[data-testid="stMain"],section.main{background:#f4f7fb!important;color:#17243a!important;color-scheme:light!important}
html,body,[class*="css"]{font-family:Inter,Cairo,sans-serif}
.block-container{max-width:1220px;padding-top:1rem;padding-bottom:3rem}
[data-testid="stSidebar"]{display:none!important}footer{visibility:hidden}
[data-testid="stHeader"]{background:rgba(244,247,251,.94)!important}
.brand{display:flex;align-items:center;gap:11px;padding:4px 0}
.brand-icon{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;color:#fff;font-size:23px;font-weight:800;background:linear-gradient(145deg,#3478f6,#2454c7);box-shadow:0 8px 18px #2864dc30}
.brand-name{font-size:18px;font-weight:850;color:#17243a}.brand-sub{font-size:10px;letter-spacing:1.2px;color:#8b98aa;font-weight:700}
.hero{padding:30px 34px;border:1px solid #e3ebf7;border-radius:24px;margin:18px 0 23px;background:linear-gradient(115deg,#fff,#f8fbff 60%,#edf4ff);box-shadow:0 12px 32px #2241700e}
.eyebrow{color:#2864dc;font-size:10px;letter-spacing:1.8px;font-weight:800}
.hero h1{color:#17243a;font-size:clamp(27px,3.4vw,39px);line-height:1.12;letter-spacing:-1.2px;margin:8px 0 10px;font-weight:800}
.hero p{color:#6d7b91;font-size:14px;margin:0;max-width:680px;line-height:1.7}
.section-head{margin:23px 0 12px}.section-head h3{margin:0;font-size:18px;color:#17243a;font-weight:800}.section-head p{margin:4px 0 0;color:#8491a4;font-size:12px}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid #e7edf5!important;border-radius:18px!important;box-shadow:0 5px 18px #233a5c09}
div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input,div[data-testid="stSelectbox"] div[data-baseweb="select"]>div{border-radius:11px!important;min-height:42px;background:#fbfcfe!important;color:#17243a!important;border-color:#dfe7f1!important}
div[data-testid="stNumberInput"] label,div[data-testid="stRadio"] label,div[data-testid="stCheckbox"] label{color:#40516b!important;font-weight:650!important;font-size:12px!important}
div[data-testid="stRadio"] div[role="radiogroup"]{display:flex;flex-wrap:wrap;gap:8px}
div[data-testid="stRadio"] div[role="radiogroup"] label{background:#f7f9fc;border:1px solid #e7edf5;border-radius:10px;padding:7px 12px}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked){background:#eaf1ff!important;border-color:#d7e5ff!important}
div.stButton>button{border-radius:12px;min-height:44px;font-weight:750;border:1px solid #dfe7f2;transition:all .18s}
div.stButton>button:hover{transform:translateY(-1px);border-color:#8eb2f5;box-shadow:0 7px 16px #2864dc1f}
div.stButton>button[kind="primary"]{background:linear-gradient(105deg,#3478f6,#2458cb);border:0;color:white}
div[data-testid="stExpander"]{background:#fff;border:1px solid #e7edf5;border-radius:14px;overflow:hidden}
div[data-testid="stAlert"]{border-radius:13px}
.bmi-preview{border:1px solid #dfeaff;border-radius:14px;padding:13px 15px;background:linear-gradient(110deg,#f5f9ff,#fff);display:flex;align-items:center;justify-content:space-between;margin:8px 0 14px}
.bmi-label{color:#77869c;font-size:10px;font-weight:800;letter-spacing:1px}.bmi-value{color:#2458cb;font-size:23px;font-weight:800}.bmi-note{color:#8391a5;font-size:11px}
.result-shell{background:#fff;border:1px solid #e5ebf3;border-radius:22px;padding:24px;box-shadow:0 9px 28px #233a5c0e;margin:12px 0 16px}
.result-top{display:flex;justify-content:space-between;align-items:center;gap:12px}.result-kicker{color:#8794a7;font-size:10px;font-weight:800;letter-spacing:1.5px}
.result-pill{display:inline-block;padding:7px 12px;border-radius:30px;font-size:10px;font-weight:800}
.result-value{font-size:clamp(28px,4vw,39px);font-weight:850;line-height:1.12;margin:13px 0 8px}
.result-explain{color:#64748b;font-size:14px;line-height:1.7}.result-number{color:#17243a;font-size:13px;font-weight:750;margin-top:12px}
.next-box{background:#f7faff;border:1px solid #e2ebfa;border-radius:17px;padding:18px 20px;margin:14px 0}
.next-title{color:#2458cb;font-size:10px;letter-spacing:1.3px;font-weight:850;margin-bottom:9px}
.next-box ul{margin:0;padding-left:19px;color:#40516b;line-height:1.85;font-size:13px}
.metric-card{background:#fff;border:1px solid #e7edf5;border-radius:16px;padding:15px 16px;min-height:104px;box-shadow:0 5px 16px #233a5c08}
.metric-name{color:#8996a8;font-size:10px;font-weight:800;letter-spacing:1px}.metric-value{color:#1c2b43;font-size:22px;font-weight:800;margin:6px 0 3px}.metric-note{color:#75849a;font-size:11px;line-height:1.45}
.footer-line{border-top:1px solid #e5ebf3;margin-top:35px;padding-top:16px;color:#9aa5b4;font-size:10px;text-align:center}
@media(max-width:720px){.block-container{padding-left:1rem;padding-right:1rem}.hero{padding:23px 20px}.hero h1{font-size:28px}.result-shell{padding:19px}}
</style>
""", unsafe_allow_html=True)


def clear_assessment():
    for key in ("patient_data", "analysis_result", "demo_mode"):
        st.session_state.pop(key, None)


def run_assessment(patient: dict, demo: bool = False):
    st.session_state["patient_data"] = patient
    st.session_state["analysis_result"] = analyze_data(patient)
    st.session_state["demo_mode"] = demo


def demo_patient(glucose_value: float) -> dict:
    return {
        "age": 35, "glucose": float(glucose_value), "glucose_type": "Fasting",
        "bmi": 23.5, "systolic_bp": 118, "diastolic_bp": 76,
        "insulin": None, "family_history": False,
    }


# Header and navigation
left, right = st.columns([1.15, 2.2], vertical_alignment="center")
with left:
    st.markdown("""
    <div class="brand"><div class="brand-icon">+</div><div>
    <div class="brand-name">GlycoSense</div><div class="brand-sub">HEALTH INTELLIGENCE</div>
    </div></div>""", unsafe_allow_html=True)
with right:
    page = st.radio("Main navigation", ["Analysis", "Rule Library", "About & Tests"],
                    horizontal=True, label_visibility="collapsed")

st.markdown("""
<div class="hero"><div class="eyebrow">HEALTH INTELLIGENCE / 01</div>
<h1>Your health, clearly understood.</h1>
<p>A transparent educational review of diabetes-related indicators.
Clear explanations, practical next steps, and no hidden scoring.</p></div>
""", unsafe_allow_html=True)


if page == "Analysis":
    st.markdown('<div class="section-head"><h3>Patient assessment</h3><p>Enter the required information, or use a synthetic example below.</p></div>', unsafe_allow_html=True)
    st.info("For glucose classification, use a fasting reading taken after at least 8 hours without calories. This educational project does not diagnose diabetes.")

    st.markdown("**Quick demo · Try the three result categories**")
    st.caption("Synthetic examples only. Select a result to run the actual analysis engine.")
    demo_cols = st.columns(3)
    for col, (label, glucose_value, key) in zip(
        demo_cols,
        [("Negative", 90.0, "demo_negative"),
         ("Moderate", 110.0, "demo_moderate"),
         ("Positive", 130.0, "demo_positive")],
    ):
        with col:
            if st.button(f"View {label} example", key=key, use_container_width=True):
                run_assessment(demo_patient(glucose_value), demo=True)
                st.rerun()

    with st.container(border=True):
        st.markdown("**01 · Personal indicators**")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age (years)", min_value=20, max_value=120, value=35, step=1,
                                  help="This project is scoped to adults aged 20 years and older.")
        with c2:
            glucose = st.number_input("Fasting glucose (mg/dL)", min_value=20.0, max_value=600.0,
                                      value=90.0, step=1.0, format="%.1f")
        st.markdown("---")
        st.markdown("**02 · Body measurements**")
        c1, c2 = st.columns(2)
        with c1:
            height = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=170.0, step=0.5)
        with c2:
            weight = st.number_input("Weight (kg)", min_value=25.0, max_value=300.0, value=65.0, step=0.5)
        bmi = weight / ((height / 100.0) ** 2)
        st.markdown(f"""
        <div class="bmi-preview"><div><div class="bmi-label">AUTOMATIC BMI CALCULATION</div>
        <div class="bmi-value">{bmi:.1f}</div><div class="bmi-note">Calculated from height and weight</div></div>
        <div style="color:#2864dc;font-size:22px;font-weight:800">↗</div></div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**03 · Clinical indicators**")
        c1, c2 = st.columns(2)
        with c1:
            systolic = st.number_input("Systolic (mmHg)", min_value=50, max_value=300, value=118, step=1)
        with c2:
            diastolic = st.number_input("Diastolic (mmHg)", min_value=30, max_value=200, value=76, step=1)
        st.markdown("---")
        st.markdown("**04 · Family history**")
        family = st.radio("Parent or sibling with Type 2 diabetes?", ["No", "Yes"], horizontal=True)
        with st.expander("＋ Optional information"):
            insulin_on = st.checkbox("Include insulin value")
            insulin = st.number_input("Insulin (µIU/mL)", min_value=0.0, max_value=1000.0,
                                      value=0.0, step=0.1, disabled=not insulin_on)
            st.caption("Insulin is displayed for context only; it does not change the glucose result.")
        b1, b2 = st.columns([3, 1])
        with b1:
            analyze_clicked = st.button("Run health assessment →", type="primary", use_container_width=True)
        with b2:
            clear_clicked = st.button("Clear result", use_container_width=True)

    if clear_clicked:
        clear_assessment()
        st.rerun()

    if analyze_clicked:
        patient = {
            "age": int(age), "glucose": float(glucose), "glucose_type": "Fasting",
            "bmi": round(bmi, 2), "systolic_bp": int(systolic),
            "diastolic_bp": int(diastolic),
            "insulin": float(insulin) if insulin_on else None,
            "family_history": family == "Yes",
        }
        run_assessment(patient, demo=False)

    if "analysis_result" in st.session_state and "patient_data" in st.session_state:
        data = st.session_state["patient_data"]
        result = st.session_state["analysis_result"]

        if st.session_state.get("demo_mode", False):
            notice, exit_col = st.columns([4, 1])
            with notice:
                st.info("Demo mode: synthetic example values, not real patient data.")
            with exit_col:
                if st.button("Exit demo", use_container_width=True):
                    clear_assessment()
                    st.rerun()

        report = build_report(data, result)
        st.markdown('<div class="section-head"><h3>Analysis overview</h3><p>Your result and the next practical step.</p></div>', unsafe_allow_html=True)

        if not result.get("valid", False):
            st.error("Analysis could not be completed.")
            for error in result.get("errors", []):
                st.write(f"• {error}")
        else:
            value = float(data["glucose"])
            classification = result.get("classification", "")
            if classification == "Low Indicator Level":
                label, color, bg = "NEGATIVE", "#16845b", "#e8f7f0"
                explain = "No high fasting-glucose indicator was detected by this project's thresholds."
                tips = [
                    "Continue balanced, varied meals and regular daily routines.",
                    "Keep up suitable regular physical activity.",
                    "Follow routine preventive checkups as advised by a healthcare professional.",
                ]
            elif classification == "Moderate Indicator Level":
                label, color, bg = "MODERATE", "#a66a08", "#fff5df"
                explain = "The fasting glucose reading is in the 100–125 mg/dL range."
                tips = [
                    "Discuss the result with a healthcare professional; ask whether repeat or additional testing is appropriate.",
                    "Choose balanced meals and limit sugar-sweetened drinks.",
                    "Build regular physical activity into your routine, as appropriate for your health.",
                ]
            elif classification == "High Indicator Level":
                label, color, bg = "POSITIVE", "#c23f48", "#fff0f0"
                explain = "The fasting glucose reading is 126 mg/dL or higher and needs clinical confirmation."
                tips = [
                    "Arrange a medical appointment to review the result and confirm it with appropriate laboratory testing.",
                    "Do not start or change medication based on this app result.",
                    "Ask a healthcare professional for an individual care plan.",
                ]
            else:
                label, color, bg = "INSUFFICIENT DATA", "#63748b", "#eef2f7"
                explain = str(result.get("summary", "The available information was insufficient for classification."))
                tips = ["Review the entered information and discuss uncertain readings with a healthcare professional."]

            st.markdown(f"""
            <div class="result-shell"><div class="result-top">
            <div class="result-kicker">FASTING GLUCOSE CLASSIFICATION</div>
            <div class="result-pill" style="background:{bg};color:{color}">{label}</div></div>
            <div class="result-value" style="color:{color}">{label.title()}</div>
            <div class="result-explain">{explain}</div>
            <div class="result-number">{value:g} <span style="color:#8491a4;font-weight:500">mg/dL fasting glucose</span></div>
            </div>""", unsafe_allow_html=True)

            if value < 70:
                st.warning("Important: this reading is below 70 mg/dL. The project's below-100 category should not be interpreted as reassuring for a low reading. Seek medical advice, especially if you feel unwell.")
            for warning in result.get("warnings", []):
                if "below 70" not in str(warning).lower():
                    st.warning(warning)

            st.markdown('<div class="next-box"><div class="next-title">YOUR NEXT STEPS</div><ul>' +
                        "".join(f"<li>{tip}</li>" for tip in tips) + "</ul></div>",
                        unsafe_allow_html=True)
            st.caption("NEGATIVE does not rule out diabetes. POSITIVE is an indicator needing clinical confirmation, not a diagnosis.")

            st.markdown('<div class="section-head"><h3>Other health indicators</h3><p>Shown separately — these do not change the glucose classification.</p></div>', unsafe_allow_html=True)
            indicators = result.get("indicators", {})
            bmi_info = indicators.get("bmi", {})
            bp_info = indicators.get("blood_pressure", {})
            metrics = [
                ("BODY MASS INDEX", f'{data["bmi"]:.1f}', bmi_info.get("classification", "Context only")),
                ("BLOOD PRESSURE", f'{data["systolic_bp"]}/{data["diastolic_bp"]}', bp_info.get("classification", "Context only")),
                ("FAMILY HISTORY", "Yes" if data["family_history"] else "No", "Context only"),
            ]
            cols = st.columns(3)
            for col, (name, val, note) in zip(cols, metrics):
                with col:
                    st.markdown(f'<div class="metric-card"><div class="metric-name">{name}</div><div class="metric-value">{val}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

            with st.expander("View detailed analysis · Why this result appeared"):
                st.write(report.get("summary", result.get("summary", "")))
                for rule in report.get("triggered_rules", []):
                    st.markdown(f'**{rule.get("rule_id", "Rule")} · {rule.get("name", "")}** — {rule.get("result", "")}')
                    if rule.get("explanation"):
                        st.caption(rule["explanation"])

            with st.expander("Explore visual indicators and charts"):
                tab1, tab2, tab3 = st.tabs(["Glucose range", "Other indicators", "Rule activity"])
                with tab1:
                    fig = glucose_reference_chart(data["glucose"], "Fasting")
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
                with tab2:
                    fig = indicator_bar_chart(data)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
                    fig = bmi_reference_chart(data["bmi"])
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
                with tab3:
                    fig = triggered_rules_chart(result)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)

            with st.expander("Technical report · applicable rules and recommendations"):
                triggered = report.get("triggered_rules", [])
                if triggered:
                    st.dataframe([{
                        "Rule ID": r.get("rule_id", ""), "Rule": r.get("name", ""),
                        "Indicator": r.get("indicator", ""), "Result": r.get("result", ""),
                        "Explanation": r.get("explanation", ""), "Source": r.get("source", ""),
                    } for r in triggered], use_container_width=True, hide_index=True)
                else:
                    st.caption("No triggered rules were returned for this assessment.")
                st.markdown("**General recommendations**")
                for item in report.get("recommendations", []):
                    if isinstance(item, dict):
                        st.write(f'• {item.get("text", item.get("recommendation", str(item)))}')
                    else:
                        st.write(f"• {item}")
                st.caption(report.get("disclaimer", "Educational project only; not a medical diagnosis."))
    else:
        st.markdown("""
        <div class="metric-card" style="margin-top:15px">
        <div class="metric-name">READY TO ANALYZE</div>
        <div style="font-size:17px;font-weight:800;color:#26364e;margin:7px 0">Your assessment will appear here</div>
        <div class="metric-note">Complete the fields above, or choose one of the three demo examples.</div>
        </div>""", unsafe_allow_html=True)


elif page == "Rule Library":
    st.markdown('<div class="section-head"><h3>Rule library</h3><p>Explore the logic behind the analysis.</p></div>', unsafe_allow_html=True)
    st.info(f"This project declares {RULE_COUNT} rules. The dashboard does not modify their definitions or thresholds.")
    categories = ["All"] + sorted({r["indicator"] for r in RULES})
    category = st.selectbox("Filter rules by indicator", categories)
    visible_rules = RULES if category == "All" else [r for r in RULES if r["indicator"] == category]
    st.dataframe(visible_rules, use_container_width=True, hide_index=True)


elif page == "About & Tests":
    st.markdown('<div class="section-head"><h3>About GlycoSense</h3><p>Scope, methodology, and quality checks.</p></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**How it works**")
        st.write(
            "- Rule-based educational analysis; no machine learning, weighted score, or probability.\n"
            "- Fasting glucose is the only value used for the final glucose classification.\\n"
            "- BMI is calculated from height and weight and reported independently.\n"
            "- Blood pressure, age, and family history are contextual indicators.\n"
            "- Insulin is optional and display-only.\n"
            "- The project is scoped to adults aged 20 years and older."
        )
    with st.expander("Synthetic demonstration data"):
        st.caption("Artificial examples only — not population prevalence or clinical evidence.")
        fig = synthetic_demo_chart()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with st.expander("Automated test cases"):
        rows = run_test_case_table()
        st.dataframe(rows, use_container_width=True, hide_index=True)
        passed = sum(1 for row in rows if row["Status"] == "PASS")
        st.metric("Test cases passed", f"{passed} / {len(rows)}")


st.markdown('<div class="footer-line">DIABETES RISK ANALYSIS · EDUCATIONAL PROJECT · TRANSPARENT RULE-BASED ENGINE</div>', unsafe_allow_html=True)
