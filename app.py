from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from analysis import analyze_data
from charts import (
    glucose_reference_chart,
    indicator_bar_chart,
    triggered_rules_chart,
    synthetic_demo_chart,
    bmi_reference_chart,
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

# ---------------------------------------------------------------------
# Premium light UI — presentation only. The 27-rule analysis engine
# and all clinical/project thresholds remain in their original modules.
# ---------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Cairo:wght@400;500;600;700;800&display=swap');

:root {
  color-scheme: light !important;
  --ink: #17243a;
  --muted: #718096;
  --blue: #2864dc;
  --blue-dark: #1e4fb5;
  --line: #e7edf5;
  --surface: #ffffff;
  --canvas: #f4f7fb;
}

html, body, [data-testid="stAppViewContainer"], .stApp,
[data-testid="stHeader"], [data-testid="stMain"], section.main {
  color-scheme: light !important;
  background: #f4f7fb !important;
  color: #17243a !important;
}
.stApp { background: var(--canvas) !important; color: var(--ink) !important; }
[data-testid="stWidgetLabel"] p, label, p, span, div {
  color-scheme: light;
}

html, body, [class*="css"] { font-family: Inter, Cairo, sans-serif; }
.block-container { max-width: 1220px; padding-top: 1.0rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { display:none !important; }
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { font-weight: 600; }
header[data-testid="stHeader"] { background: rgba(244,247,251,.88); }

footer { visibility: hidden; }
@media (max-width: 720px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .hero { padding:22px 20px; border-radius:19px; }
  .top-nav-wrap { align-items:flex-start; flex-direction:column; }
  .result-shell { padding:19px; }
  div[data-testid="stRadio"] div[role="radiogroup"] { justify-content:flex-start; }
}


.brand-mark {
  display: flex; align-items: center; gap: 11px;
  padding: 5px 0 22px 0;
}
.brand-icon {
  width: 42px; height: 42px; border-radius: 14px;
  display: grid; place-items: center;
  color: white; font-size: 22px; font-weight: 800;
  background: linear-gradient(145deg,#3478f6,#2454c7);
  box-shadow: 0 8px 18px rgba(40,100,220,.22);
}
.brand-name { font-size: 18px; font-weight: 850; color: #17243a; line-height: 1.2; letter-spacing:-.45px; }
.brand-sub { font-size: 10px; letter-spacing: 1.25px; color: #8b98aa; font-weight: 700; margin-top: 4px; }

.topline {
  display:flex; align-items:center; justify-content:space-between;
  gap:16px; margin: 2px 0 18px 0;
}
.eyebrow {
  color:#2864dc; font-size:10px; letter-spacing:1.8px;
  font-weight:800; text-transform:uppercase;
}
.hero {
  position:relative; overflow:hidden;
  padding:32px 34px; border:1px solid #e3ebf7;
  border-radius:25px; margin-bottom:23px;
  background:linear-gradient(115deg,#ffffff 0%,#f8fbff 60%,#edf4ff 100%);
  box-shadow:0 12px 32px rgba(34,65,112,.055);
}
.hero:after {
  content:""; position:absolute; width:210px; height:210px;
  border-radius:50%; right:-65px; top:-100px;
  background:rgba(66,129,239,.07);
}
.hero h1 {
  color:#17243a; font-size:clamp(27px,3.4vw,39px);
  line-height:1.12; letter-spacing:-1.2px;
  margin:8px 0 10px 0; font-weight:800;
}
.hero p { color:#6d7b91; font-size:14px; margin:0; max-width:680px; line-height:1.7; }
.hero-tag {
  display:inline-flex; align-items:center; gap:7px;
  background:#edf4ff; color:#285ec3; border:1px solid #dce9ff;
  border-radius:30px; padding:7px 11px; font-size:10px;
  font-weight:800; letter-spacing:.6px;
}


.top-nav-wrap {
  display:flex; align-items:center; justify-content:space-between;
  gap:18px; padding:13px 18px; background:#fff;
  border:1px solid #e7edf5; border-radius:17px;
  box-shadow:0 5px 18px rgba(35,58,92,.035); margin-bottom:18px;
}
.top-nav-brand { color:#17243a; font-size:15px; font-weight:850; letter-spacing:-.3px; }
.top-nav-caption { color:#8996a8; font-size:9px; letter-spacing:1.4px; font-weight:800; margin-top:3px; }
div[data-testid="stRadio"] div[role="radiogroup"] {
  display:flex; flex-wrap:wrap; gap:7px; justify-content:flex-end;
}
div[data-testid="stRadio"] div[role="radiogroup"] label {
  background:#f5f7fb !important; color:#53647b !important;
  border:1px solid #e8edf4 !important; border-radius:10px !important;
  padding:7px 13px !important; min-height:34px;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
  background:#eaf1ff !important; color:#2458cb !important;
  border-color:#d7e5ff !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label p {
  color:inherit !important; font-weight:750 !important; font-size:11px !important;
}
.section-head { margin: 23px 0 12px; }

.section-head h3 { margin:0; font-size:18px; color:#17243a; font-weight:800; }
.section-head p { margin:4px 0 0; color:#8491a4; font-size:12px; }

div[data-testid="stVerticalBlockBorderWrapper"] {
  background:#fff; border:1px solid #e7edf5 !important;
  border-radius:18px !important; box-shadow:0 5px 18px rgba(35,58,92,.035);
}
div[data-testid="stForm"] {
  background:#fff; border:1px solid #e7edf5;
  border-radius:18px; padding:18px 20px;
}
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label {
  color:#40516b !important; font-weight:650 !important; font-size:12px !important;
}

div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stDateInput"] input,
div[data-testid="stTextArea"] textarea {
  border-radius:11px !important; min-height:42px;
  background:#fbfcfe !important; color:#17243a !important;
  border-color:#dfe7f1 !important;
  -webkit-text-fill-color:#17243a !important;
}
div[data-testid="stNumberInput"] button {
  background:#f1f5fb !important; color:#2864dc !important;
  border-color:#dfe7f1 !important;
}

div[data-testid="stNumberInput"] button {
  border-radius:9px !important; color:#2864dc !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] { gap:10px; }
div[data-testid="stRadio"] div[role="radiogroup"] label {
  background:#f7f9fc; border:1px solid #e7edf5;
  border-radius:10px; padding:7px 12px;
}
div.stButton > button, div.stFormSubmitButton > button {
  border-radius:12px; min-height:46px; font-weight:750;
  transition:all .18s ease; border:1px solid #dfe7f2;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
  transform:translateY(-1px); border-color:#8eb2f5;
  box-shadow:0 7px 16px rgba(40,100,220,.12);
}
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
  background:linear-gradient(105deg,#3478f6,#2458cb);
  border:0; color:#fff;
}
div[data-testid="stExpander"] {
  background:#fff; border:1px solid #e7edf5;
  border-radius:14px; overflow:hidden;
}
div[data-testid="stTabs"] button { font-weight:700; }
div[data-testid="stAlert"] { border-radius:13px; }
div[data-testid="stDataFrame"] { border:1px solid #e7edf5; border-radius:12px; overflow:hidden; }

.bmi-preview {
  border:1px solid #dfeaff; border-radius:14px; padding:13px 15px;
  background:linear-gradient(110deg,#f5f9ff,#fff);
  display:flex; align-items:center; justify-content:space-between; gap:12px;
  margin:8px 0 14px;
}
.bmi-label { color:#77869c; font-size:10px; font-weight:800; letter-spacing:1px; }
.bmi-value { color:#2458cb; font-size:23px; font-weight:800; margin-top:2px; }
.bmi-note { color:#8391a5; font-size:11px; }

.result-shell {
  background:#fff; border:1px solid #e5ebf3; border-radius:22px;
  padding:24px; box-shadow:0 9px 28px rgba(35,58,92,.055);
  margin:12px 0 16px;
}
.result-top { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.result-kicker { color:#8794a7; font-size:10px; font-weight:800; letter-spacing:1.5px; }
.result-pill {
  display:inline-block; padding:7px 12px; border-radius:30px;
  font-size:10px; font-weight:800; letter-spacing:.7px;
}
.result-value { font-size:clamp(28px,4vw,39px); font-weight:850; line-height:1.12; margin:13px 0 8px; }
.result-explain { color:#64748b; font-size:14px; line-height:1.7; }
.result-number { color:#17243a; font-size:13px; font-weight:750; margin-top:12px; }
.next-box {
  background:#f7faff; border:1px solid #e2ebfa;
  border-radius:17px; padding:18px 20px; margin:14px 0;
}
.next-title { color:#2458cb; font-size:10px; letter-spacing:1.3px; font-weight:850; margin-bottom:9px; }
.next-box ul { margin:0; padding-left:19px; color:#40516b; line-height:1.85; font-size:13px; }
.metric-card {
  background:#fff; border:1px solid #e7edf5; border-radius:16px;
  padding:15px 16px; min-height:104px;
  box-shadow:0 5px 16px rgba(35,58,92,.03);
}
.metric-name { color:#8996a8; font-size:10px; font-weight:800; letter-spacing:1px; }
.metric-value { color:#1c2b43; font-size:22px; font-weight:800; margin:6px 0 3px; }
.metric-note { color:#75849a; font-size:11px; line-height:1.45; }
.small-note { color:#8a97a9; font-size:11px; line-height:1.6; }
.footer-line { border-top:1px solid #e5ebf3; margin-top:35px; padding-top:16px; color:#9aa5b4; font-size:10px; text-align:center; }

/* GlycoSense refinements */
[data-testid="stAppViewContainer"] * { color-scheme: light; }
[data-testid="stHeader"] { background:rgba(244,247,251,.94) !important; }
[data-testid="stToolbar"] { right:1rem; }
[data-testid="stMainBlockContainer"] { padding-top:1rem; }
div[data-testid="stRadio"] div[role="radiogroup"] label {
  transition:background .16s ease, border-color .16s ease, color .16s ease;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
  border-color:#b9cdf2 !important; background:#f0f5ff !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
  border-color:#7da7f4 !important;
  box-shadow:0 0 0 2px rgba(40,100,220,.10) !important;
}
div[data-testid="stExpander"] summary {
  color:#263b59 !important; font-weight:700 !important;
}
div[data-testid="stMetric"] {
  background:#fff; border:1px solid #e7edf5; border-radius:14px;
  padding:12px 14px;
}
div[data-testid="stMetric"] label { color:#8491a4 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#17243a !important; }
@media (max-width: 720px) {
  .brand-mark { padding-bottom:12px; }
  .hero { padding:23px 20px; }
  .hero h1 { font-size:28px; }
  .hero p { font-size:13px; }
  div[data-testid="stRadio"] div[role="radiogroup"] label { padding:6px 9px !important; }
}

</style>
""",
    unsafe_allow_html=True,
)

# Top navigation — no sidebar.
nav_left, nav_right = st.columns([1.25, 2.2], vertical_alignment="center")
with nav_left:
    st.markdown(
        """
        <div class="brand-mark" style="padding:4px 0 4px 0">
          <div class="brand-icon">+</div>
          <div><div class="brand-name">GlycoSense</div>
          <div class="brand-sub">HEALTH INTELLIGENCE</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with nav_right:
    page = st.radio(
        "Main navigation",
        ["Analysis", "Rule Library", "About & Tests"],
        horizontal=True,
        label_visibility="collapsed",
    )

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">HEALTH INTELLIGENCE / 01</div>
      <h1>Your health, clearly understood.</h1>
      <p>A simple, transparent assessment of diabetes-related health indicators. Clear results, practical next steps, and no hidden scoring.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Analysis":
    st.markdown(
        '<div class="section-head"><h3>Patient assessment</h3>'
        '<p>Enter the required information. Your BMI is calculated automatically.</p></div>',
        unsafe_allow_html=True,
    )
    st.info(
        "Enter a fasting glucose reading taken after at least "
        "8 hours without calories. The app does not diagnose diabetes."
    )

    with st.container(border=True):
        st.markdown("**01  ·  Personal indicators**")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=35, step=1)
        with c2:
            glucose = st.number_input(
                "Fasting glucose (mg/dL)", min_value=20.0, max_value=600.0,
                value=90.0, step=1.0, format="%.1f",
            )

        st.markdown("---")
        st.markdown("**02  ·  Body measurements**")
        c1, c2 = st.columns(2)
        with c1:
            height = st.number_input(
                "Height (cm)", min_value=100.0, max_value=230.0,
                value=170.0, step=0.5,
            )
        with c2:
            weight = st.number_input(
                "Weight (kg)", min_value=25.0, max_value=300.0,
                value=65.0, step=0.5,
            )
        bmi = weight / ((height / 100.0) ** 2)
        st.markdown(
            f"""
            <div class="bmi-preview">
              <div><div class="bmi-label">AUTOMATIC BMI CALCULATION</div>
              <div class="bmi-value">{bmi:.1f}</div>
              <div class="bmi-note">Calculated from height and weight</div></div>
              <div style="color:#2864dc;font-size:22px;font-weight:800">↗</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("**03  ·  Clinical indicators**")
        c1, c2 = st.columns(2)
        with c1:
            systolic = st.number_input(
                "Systolic (mmHg)", min_value=50, max_value=300, value=118, step=1
            )
        with c2:
            diastolic = st.number_input(
                "Diastolic (mmHg)", min_value=30, max_value=200, value=76, step=1
            )

        st.markdown("---")
        st.markdown("**04  ·  Family history**")
        family = st.radio(
            "Parent or sibling with Type 2 diabetes?",
            ["No", "Yes"],
            horizontal=True,
        )

        with st.expander("＋  Optional information"):
            insulin_on = st.checkbox("Include insulin value")
            insulin = st.number_input(
                "Insulin (µIU/mL)", min_value=0.0, max_value=1000.0,
                value=0.0, step=0.1, disabled=not insulin_on,
            )
            st.caption("Insulin is displayed for context only; it does not change the result.")

        b1, b2 = st.columns([3, 1])
        with b1:
            analyze_clicked = st.button(
                "Run Health Assessment  →", type="primary", use_container_width=True
            )
        with b2:
            clear_clicked = st.button("Clear result", use_container_width=True)

    if clear_clicked:
        for key in ("patient_data", "analysis_result"):
            st.session_state.pop(key, None)
        st.rerun()

    if analyze_clicked:
        patient = {
            "age": int(age),
            "glucose": float(glucose),
            "glucose_type": "Fasting",
            "bmi": round(bmi, 2),
            "systolic_bp": int(systolic),
            "diastolic_bp": int(diastolic),
            "insulin": float(insulin) if insulin_on else None,
            "family_history": family == "Yes",
        }
        st.session_state["patient_data"] = patient
        st.session_state["analysis_result"] = analyze_data(patient)

    if "analysis_result" in st.session_state:
        data = st.session_state["patient_data"]
        result = st.session_state["analysis_result"]
        report = build_report(data, result)

        st.markdown(
            '<div class="section-head"><h3>Analysis overview</h3>'
            '<p>Your result and the next practical step.</p></div>',
            unsafe_allow_html=True,
        )

        if not result["valid"]:
            st.error("Analysis could not be completed.")
            for error in result["errors"]:
                st.write(f"• {error}")
        else:
            value = float(data["glucose"])
            if result["classification"] == "Low Indicator Level":
                label, color, bg, explain = (
                    "NEGATIVE", "#16845b", "#e8f7f0",
                    "No high fasting-glucose indicator was detected by this project's thresholds.",
                )
                tips = [
                    "Continue balanced, varied meals and regular daily routines.",
                    "Keep up suitable regular physical activity.",
                    "Follow routine preventive checkups as advised by a healthcare professional.",
                ]
            elif result["classification"] == "Moderate Indicator Level":
                label, color, bg, explain = (
                    "MODERATE", "#a66a08", "#fff5df",
                    "The fasting glucose reading is in the 100–125 mg/dL range.",
                )
                tips = [
                    "Discuss the result with a healthcare professional; ask whether repeat or additional testing is appropriate.",
                    "Choose balanced meals and limit sugar-sweetened drinks.",
                    "Build regular physical activity into your routine, as appropriate for your health.",
                ]
            elif result["classification"] == "High Indicator Level":
                label, color, bg, explain = (
                    "POSITIVE", "#c23f48", "#fff0f0",
                    "The fasting glucose reading is 126 mg/dL or higher and needs clinical confirmation.",
                )
                tips = [
                    "Arrange a medical appointment to review the result and confirm it with appropriate laboratory testing.",
                    "Do not start or change medication based on this app result.",
                    "Ask a healthcare professional for an individual care plan.",
                ]
            else:
                label, color, bg, explain = (
                    "INSUFFICIENT DATA", "#63748b", "#eef2f7", result["summary"]
                )
                tips = [
                    "Review the entered information and discuss uncertain readings with a healthcare professional."
                ]

            st.markdown(
                f"""
                <div class="result-shell">
                  <div class="result-top">
                    <div class="result-kicker">FASTING GLUCOSE CLASSIFICATION</div>
                    <div class="result-pill" style="background:{bg};color:{color}">{label}</div>
                  </div>
                  <div class="result-value" style="color:{color}">{label.title()}</div>
                  <div class="result-explain">{explain}</div>
                  <div class="result-number">{value:g} <span style="color:#8491a4;font-weight:500">mg/dL fasting glucose</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if value < 70:
                st.warning(
                    "Important: this reading is below 70 mg/dL. The project's "
                    "below-100 label should not be interpreted as reassuring for "
                    "a low reading. Seek medical advice, especially if you feel unwell."
                )
            for warning in result.get("warnings", []):
                if "below 70" not in warning:
                    st.warning(warning)

            st.markdown(
                '<div class="next-box"><div class="next-title">YOUR NEXT STEPS</div><ul>'
                + "".join(f"<li>{tip}</li>" for tip in tips)
                + "</ul></div>",
                unsafe_allow_html=True,
            )
            st.caption(
                "Important: NEGATIVE does not rule out diabetes. POSITIVE is an "
                "indicator that needs clinical confirmation, not a diagnosis."
            )

            st.markdown(
                '<div class="section-head"><h3>Other health indicators</h3>'
                '<p>Shown separately — these do not change the glucose classification.</p></div>',
                unsafe_allow_html=True,
            )
            metrics = [
                ("BODY MASS INDEX", f'{data["bmi"]:.1f}', result["indicators"]["bmi"]["classification"]),
                (
                    "BLOOD PRESSURE",
                    f'{data["systolic_bp"]}/{data["diastolic_bp"]}',
                    result["indicators"]["blood_pressure"]["classification"],
                ),
                (
                    "FAMILY HISTORY",
                    "Yes" if data["family_history"] else "No",
                    "Context only",
                ),
            ]
            cols = st.columns(3)
            for col, (name, val, note) in zip(cols, metrics):
                with col:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-name">{name}</div>'
                        f'<div class="metric-value">{val}</div>'
                        f'<div class="metric-note">{note}</div></div>',
                        unsafe_allow_html=True,
                    )

            with st.expander("View detailed analysis · Why this result appeared"):
                st.write(report["summary"])
                for rule in report["triggered_rules"]:
                    st.markdown(f'**{rule["rule_id"]} · {rule["name"]}** — {rule["result"]}')
                    st.caption(rule["explanation"])

            with st.expander("Explore visual indicators and charts"):
                tab1, tab2, tab3 = st.tabs(
                    ["Glucose range", "Other indicators", "Rule activity"]
                )
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
                st.dataframe(
                    [
                        {
                            "Rule ID": r["rule_id"],
                            "Rule": r["name"],
                            "Indicator": r["indicator"],
                            "Result": r["result"],
                            "Explanation": r["explanation"],
                            "Source": r["source"],
                        }
                        for r in report["triggered_rules"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
                st.markdown("**General recommendations**")
                for item in report["recommendations"]:
                    st.write(f"• {item}")
                st.caption(report["disclaimer"])

    else:
        st.markdown(
            """
            <div class="metric-card" style="margin-top:15px">
              <div class="metric-name">READY TO ANALYZE</div>
              <div style="font-size:17px;font-weight:800;color:#26364e;margin:7px 0">
                Your assessment will appear here
              </div>
              <div class="metric-note">Complete the fields above, then select Analyze patient data.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif page == "Rule Library":
    st.markdown(
        '<div class="section-head"><h3>Rule library</h3>'
        '<p>Explore the logic behind the analysis.</p></div>',
        unsafe_allow_html=True,
    )
    st.info(f"This project uses exactly {RULE_COUNT} rules. Their definitions are not changed by the dashboard redesign.")
    categories = ["All"] + sorted({r["indicator"] for r in RULES})
    category = st.selectbox("Filter rules by indicator", categories)
    visible_rules = RULES if category == "All" else [r for r in RULES if r["indicator"] == category]
    st.dataframe(visible_rules, use_container_width=True, hide_index=True)

elif page == "About & Tests":
    st.markdown(
        '<div class="section-head"><h3>About GlycoSense</h3>'
        '<p>Scope, methodology, and quality checks.</p></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown("**How it works**")
        st.write(
            "- Rule-based educational analysis; no machine learning, weighted score, or probability.\n"
            "- Fasting glucose is the only value used for the final glucose classification.\n"
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

st.markdown(
    '<div class="footer-line">DIABETES RISK ANALYSIS · EDUCATIONAL PROJECT · 27 TRANSPARENT RULES</div>',
    unsafe_allow_html=True,
)
