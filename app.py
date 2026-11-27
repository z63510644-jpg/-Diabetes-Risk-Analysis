from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from analysis import analyze_data
from charts import glucose_reference_chart, indicator_bar_chart, triggered_rules_chart, synthetic_demo_chart, bmi_reference_chart
from report import build_report
from rules import RULE_COUNT, RULES
from test_cases import run_test_case_table

st.set_page_config(page_title="Diabetes Risk Analysis", page_icon="🩺", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp{background:#080d18;color:#edf3ff} html,body,[class*="css"]{font-family:Inter,sans-serif}
.block-container{max-width:1120px;padding-top:1.4rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#101827;border-right:1px solid #26334a}
.hero{padding:27px 30px;border:1px solid #273650;border-radius:22px;background:linear-gradient(120deg,#151f32,#101a2c 65%,#132744);margin-bottom:18px}
.eyebrow{color:#83b7ff;font-size:11px;letter-spacing:2px;font-weight:800;text-transform:uppercase}
.hero h1{color:#f5f8ff;font-size:clamp(27px,4vw,39px);margin:8px 0}
.hero p{color:#aab9d0;margin:0;font-size:14px}
.panel,.result-card{background:#111b2b;border:1px solid #273650;border-radius:18px;padding:20px 22px;margin:12px 0}
.result-card{padding:25px}.result-kicker,.metric-name{color:#9aabc4;font-size:11px;font-weight:800;letter-spacing:1.5px}
.result-value{font-size:clamp(27px,4vw,38px);font-weight:800;margin:7px 0}
.result-explain{color:#d2dced;font-size:14px;line-height:1.6}
.guidance{background:#18263a;border:1px solid #2b405d;border-radius:14px;padding:16px 18px;margin-top:14px}
.metric-card{background:#172438;border:1px solid #2a3b55;border-radius:14px;padding:14px;min-height:88px}
.metric-value{color:#f3f7ff;font-size:21px;font-weight:800;margin:5px 0}
.muted{color:#9aabc4;font-size:12px}
div[data-testid="stExpander"]{background:#111b2b;border:1px solid #273650;border-radius:14px}
div.stButton>button,div.stFormSubmitButton>button{border-radius:12px;min-height:46px;font-weight:700}
div.stFormSubmitButton>button[kind="primary"]{background:#2878e5;border:0;color:white}
footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🩺 DRA")
    st.caption("Diabetes Risk Analysis")
    page = st.radio("WORKSPACE", ["Analysis", "Rule library", "About"])
    st.divider()
    st.caption("EDUCATIONAL TOOL · 27 TRANSPARENT RULES")
    st.caption("Project scope: adults aged 20+")

st.markdown('<div class="hero"><div class="eyebrow">Rule-based health indicator analysis</div><h1>Diabetes Risk Analysis</h1><p>A concise result, clear explanations, and practical next steps.</p></div>', unsafe_allow_html=True)
st.info("Educational use only. This project does not diagnose diabetes or estimate probability. Enter a fasting-glucose reading only; the measurement-type selector has been removed.")

DEMOS = {
    "Custom input": dict(age=35, glucose=90., height=170., weight=64., systolic=118, diastolic=76, insulin=None, family=False),
    "Demo — Negative": dict(age=32, glucose=92., height=168., weight=66., systolic=116, diastolic=74, insulin=None, family=False),
    "Demo — Moderate": dict(age=48, glucose=110., height=170., weight=78., systolic=132, diastolic=84, insulin=12., family=True),
    "Demo — Positive": dict(age=56, glucose=138., height=165., weight=82., systolic=145, diastolic=92, insulin=None, family=True),
}

if page == "Analysis":
    st.markdown('<div class="panel"><b>Patient data</b><div class="muted">Complete the required fields. Insulin is optional.</div>', unsafe_allow_html=True)
    selected = st.selectbox("Load a synthetic example (optional)", list(DEMOS))
    d = DEMOS[selected]
    with st.form("analysis_form"):
        st.markdown("#### 1 · Basic information")
        a,b = st.columns(2)
        age = a.number_input("Age (years) · Required", 1, 120, d["age"])
        glucose = b.number_input("Fasting glucose (mg/dL) · Required", 20., 600., d["glucose"])
        st.caption("Use a fasting reading after at least 8 hours without calories.")
        st.markdown("#### 2 · Body measurements")
        a,b = st.columns(2)
        height = a.number_input("Height (cm) · Required", 100., 230., d["height"], .5)
        weight = b.number_input("Weight (kg) · Required", 25., 300., d["weight"], .5)
        st.markdown("#### 3 · Blood pressure")
        a,b = st.columns(2)
        systolic = a.number_input("Systolic (mmHg) · Required", 50, 300, d["systolic"])
        diastolic = b.number_input("Diastolic (mmHg) · Required", 30, 200, d["diastolic"])
        family = st.radio("Parent or sibling with Type 2 diabetes? · Required", ["No","Yes"], index=int(d["family"]), horizontal=True)
        with st.expander("Optional information"):
            insulin_on = st.checkbox("Add insulin value", value=d["insulin"] is not None)
            insulin = st.number_input("Insulin (µIU/mL)", 0., 1000., float(d["insulin"] or 0.), .1, disabled=not insulin_on)
        submitted = st.form_submit_button("Analyze my data", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        bmi = weight / ((height/100.)**2)
        patient = {"age":int(age),"glucose":float(glucose),"glucose_type":"Fasting","bmi":round(bmi,2),
                   "systolic_bp":int(systolic),"diastolic_bp":int(diastolic),
                   "insulin":float(insulin) if insulin_on else None,"family_history":family=="Yes"}
        st.session_state["patient_data"] = patient
        st.session_state["analysis_result"] = analyze_data(patient)

    if "analysis_result" in st.session_state:
        data = st.session_state["patient_data"]
        result = st.session_state["analysis_result"]
        report = build_report(data,result)
        st.markdown("## Your result")
        if not result["valid"]:
            st.error("Analysis could not be completed.")
            for error in result["errors"]: st.write("- " + error)
        else:
            value = float(data["glucose"])
            if result["classification"] == "Low Indicator Level":
                label,color,explain = "NEGATIVE","#55d69a","The fasting glucose reading is below 100 mg/dL."
                tips = ["Continue balanced, varied meals and regular daily routines.",
                        "Keep up regular physical activity appropriate for your health and abilities.",
                        "Follow routine preventive checkups as advised by a healthcare professional."]
            elif result["classification"] == "Moderate Indicator Level":
                label,color,explain = "MODERATE","#f3bd58","The fasting glucose reading is between 100 and 125 mg/dL."
                tips = ["Discuss the result with a healthcare professional and ask whether repeat or additional testing is appropriate.",
                        "Choose balanced meals and limit sugar-sweetened drinks.",
                        "Build regular physical activity into your routine, as appropriate for your health."]
            elif result["classification"] == "High Indicator Level":
                label,color,explain = "POSITIVE","#ff7777","The fasting glucose reading is 126 mg/dL or higher and needs clinical confirmation."
                tips = ["Arrange a medical appointment to review the result and confirm it with appropriate laboratory testing.",
                        "Do not start or change medication based on this app result.",
                        "Ask a healthcare professional for an individual care plan."]
            else:
                label,color,explain = "INSUFFICIENT DATA","#aab9d0",result["summary"]
                tips = ["Check the entered information and discuss uncertain readings with a healthcare professional."]

            st.markdown(f'<div class="result-card"><div class="result-kicker">FASTING GLUCOSE RESULT</div><div class="result-value" style="color:{color}">{label}</div><div class="result-explain">{explain}</div><div class="muted" style="margin-top:8px">{value:g} mg/dL</div></div>', unsafe_allow_html=True)
            if value < 70:
                st.warning("Important: this reading is below 70 mg/dL. Although the project label is NEGATIVE because it is below 100, a low reading is not automatically reassuring. Seek medical advice, especially if you feel unwell.")
            for warning in result.get("warnings",[]):
                if "below 70" not in warning: st.warning(warning)
            st.markdown('<div class="guidance"><b>WHAT TO DO NEXT</b>', unsafe_allow_html=True)
            for tip in tips: st.markdown("- " + tip)
            st.markdown("</div>", unsafe_allow_html=True)
            st.caption("NEGATIVE means no high fasting-glucose indicator was detected by these project thresholds; it does not rule out diabetes. POSITIVE is an indicator requiring clinical confirmation, not a diagnosis.")

            st.markdown("### Other indicators")
            cols = st.columns(3)
            metrics = [("BMI",f'{data["bmi"]:.1f}',result["indicators"]["bmi"]["classification"]),
                       ("Blood pressure",f'{data["systolic_bp"]}/{data["diastolic_bp"]}',result["indicators"]["blood_pressure"]["classification"]),
                       ("Family history","Yes" if data["family_history"] else "No","Context only")]
            for col,(name,val,note) in zip(cols,metrics):
                with col:
                    st.markdown(f'<div class="metric-card"><div class="metric-name">{name}</div><div class="metric-value">{val}</div><div class="muted">{note}</div></div>',unsafe_allow_html=True)
            st.caption("BMI, blood pressure, age, family history, and insulin are independent context. They do not change glucose classification.")

            with st.expander("Why did I get this result?"):
                st.write(report["summary"])
                for rule in report["triggered_rules"]:
                    st.markdown(f'**{rule["rule_id"]} · {rule["name"]}** — {rule["result"]}')
                    st.caption(rule["explanation"])
            with st.expander("Charts and indicator details"):
                t1,t2,t3 = st.tabs(["Glucose","Blood pressure & BMI","Rule activity"])
                with t1:
                    fig=glucose_reference_chart(data["glucose"],"Fasting"); st.pyplot(fig,use_container_width=True); plt.close(fig)
                with t2:
                    fig=indicator_bar_chart(data); st.pyplot(fig,use_container_width=True); plt.close(fig)
                    fig=bmi_reference_chart(data["bmi"]); st.pyplot(fig,use_container_width=True); plt.close(fig)
                with t3:
                    fig=triggered_rules_chart(result); st.pyplot(fig,use_container_width=True); plt.close(fig)
            with st.expander("Full technical report · 27 rules"):
                st.dataframe([{"Rule ID":r["rule_id"],"Rule":r["name"],"Indicator":r["indicator"],"Result":r["result"],"Explanation":r["explanation"],"Source":r["source"]} for r in report["triggered_rules"]],use_container_width=True,hide_index=True)
                for item in report["recommendations"]: st.write("- " + item)
                st.caption(report["disclaimer"])

elif page == "Rule library":
    st.markdown("## Rule library")
    st.caption(f"{RULE_COUNT} transparent rules. Definitions are unchanged.")
    category=st.selectbox("Filter by indicator",["All"]+sorted({r["indicator"] for r in RULES}))
    st.dataframe(RULES if category=="All" else [r for r in RULES if r["indicator"]==category],use_container_width=True,hide_index=True)

elif page == "About":
    st.markdown("## About this project")
    st.markdown("- Rule-based educational project; no machine learning, weighted score, or probability.\n- The interface asks for fasting glucose only; measurement-type selector removed.\n- BMI is calculated from height and weight.\n- Blood pressure and family history are independent indicators.\n- Insulin is optional and display-only.\n- Project scope is adults aged 20+.")
    with st.expander("Synthetic demonstration dataset"):
        st.caption("Artificial examples only; not population prevalence or clinical evidence.")
        fig=synthetic_demo_chart(); st.pyplot(fig,use_container_width=True); plt.close(fig)
    with st.expander("Automated test cases"):
        st.dataframe(run_test_case_table(),use_container_width=True,hide_index=True)

st.markdown('<div class="muted" style="text-align:center;padding:28px 0 8px">Diabetes Risk Analysis · Educational project · 27 transparent rules</div>',unsafe_allow_html=True)
