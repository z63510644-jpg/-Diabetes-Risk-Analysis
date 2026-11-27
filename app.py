from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from analysis import analyze_data
from charts import glucose_reference_chart, indicator_bar_chart, triggered_rules_chart, synthetic_demo_chart, bmi_reference_chart
from report import build_report
from rules import RULE_COUNT, RULES
from test_cases import run_test_case_table

st.set_page_config(page_title="Diabetes Risk Analysis", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp{background:#f6f8fc} html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.block-container{max-width:1160px;padding-top:1.5rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #e8edf4}
.hero{padding:26px 30px;border:1px solid #e5ebf4;border-radius:24px;background:linear-gradient(120deg,#fff 0%,#eef5ff 100%);box-shadow:0 8px 28px rgba(30,55,90,.045);margin-bottom:18px}
.eyebrow{color:#6681a4;font-size:11px;letter-spacing:1.8px;font-weight:800;text-transform:uppercase}
.hero h1{color:#17263c;font-size:clamp(27px,4vw,38px);line-height:1.12;margin:8px 0;letter-spacing:-1.2px}
.hero p{color:#687991;margin:0;font-size:14px}
.panel,.result{background:#fff;border:1px solid #e7edf4;border-radius:19px;padding:20px 22px;margin:12px 0;box-shadow:0 5px 20px rgba(30,55,90,.025)}
.panel-title{font-size:17px;font-weight:750;color:#1c2b41;margin-bottom:4px}.muted{color:#78879b;font-size:12px}
.result-label,.metric-name{color:#718198;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.result-value{font-size:clamp(24px,3vw,32px);font-weight:800;color:#1d3555;letter-spacing:-.8px;margin:5px 0}
.metric-card{background:#f7f9fc;border:1px solid #e9eef5;border-radius:15px;padding:14px 16px;min-height:90px}
.metric-value{color:#1d2d43;font-size:21px;font-weight:800;margin:5px 0}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{background:#246fd1;border:0;border-radius:12px;min-height:46px;font-weight:700}
[data-testid="stExpander"]{border:1px solid #e7edf4;border-radius:14px;background:#fff}footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🩺 DRA")
    st.caption("Diabetes Risk Analysis")
    page = st.radio("WORKSPACE", ["Overview", "Analysis", "Rule library", "About"])
    st.divider()
    st.caption("EDUCATIONAL TOOL · 27 TRANSPARENT RULES")
    st.caption("Designed for adults aged 20+")

st.markdown('''<div class="hero"><div class="eyebrow">Educational · Rule-based health indicators</div><h1>Diabetes Risk Analysis</h1><p>A clearer view of selected indicators, with transparent rules and a concise result.</p></div>''', unsafe_allow_html=True)
st.info("Educational use only — this tool does not diagnose diabetes, estimate disease probability, or replace a healthcare professional. Final indicator level uses fasting glucose only.")

DEMO_CASES = {
    "Custom input": {"age":35,"glucose":90.0,"glucose_type":"Fasting","bmi":22.0,"systolic_bp":118,"diastolic_bp":76,"insulin":None,"family_history":False},
    "Demo — Low indicator": {"age":32,"glucose":92.0,"glucose_type":"Fasting","bmi":23.4,"systolic_bp":116,"diastolic_bp":74,"insulin":None,"family_history":False},
    "Demo — Moderate indicator": {"age":48,"glucose":110.0,"glucose_type":"Fasting","bmi":28.1,"systolic_bp":132,"diastolic_bp":84,"insulin":12.0,"family_history":True},
    "Demo — High indicator": {"age":56,"glucose":138.0,"glucose_type":"Fasting","bmi":31.2,"systolic_bp":145,"diastolic_bp":92,"insulin":None,"family_history":True},
}

if page in ("Overview", "Analysis"):
    st.markdown('<div class="panel"><div class="panel-title">Quick analysis</div><div class="muted">Enter the core reading first. Additional indicators are grouped below.</div>', unsafe_allow_html=True)
    selected = st.selectbox("Load a synthetic example (optional)", list(DEMO_CASES), key="demo_choice")
    defaults = DEMO_CASES[selected]
    with st.form("analysis_form", clear_on_submit=False):
        st.markdown("#### 1 · Core information")
        c1,c2,c3 = st.columns(3)
        with c1: age = st.number_input("Age (years)",1,120,int(defaults["age"]),1)
        with c2: glucose = st.number_input("Glucose (mg/dL)",20.0,600.0,float(defaults["glucose"]),1.0)
        with c3: glucose_type = st.selectbox("Measurement type",["Fasting","Random","Unknown"],index=["Fasting","Random","Unknown"].index(defaults["glucose_type"]))
        st.caption("Fasting means no caloric intake for at least 8 hours.")
        with st.expander("Additional indicators",expanded=False):
            x,y = st.columns(2)
            with x:
                bmi = st.number_input("BMI (kg/m²)",10.0,80.0,float(defaults["bmi"]),0.1,format="%.1f")
                systolic = st.number_input("Systolic blood pressure (mmHg)",50,300,int(defaults["systolic_bp"]),1)
                family_history = st.radio("Parent or sibling with Type 2 diabetes?",["No","Yes"],index=1 if defaults["family_history"] else 0,horizontal=True)
            with y:
                diastolic = st.number_input("Diastolic blood pressure (mmHg)",30,200,int(defaults["diastolic_bp"]),1)
                insulin_provided = st.checkbox("Add optional insulin value",value=defaults["insulin"] is not None)
                insulin = st.number_input("Insulin (µIU/mL)",0.0,1000.0,float(defaults["insulin"] or 0.0),0.1,disabled=not insulin_provided)
        submitted = st.form_submit_button("Run analysis",type="primary",use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)

    if submitted:
        patient_data = {"age":int(age),"glucose":float(glucose),"glucose_type":glucose_type,"bmi":float(bmi),"systolic_bp":int(systolic),"diastolic_bp":int(diastolic),"insulin":float(insulin) if insulin_provided else None,"family_history":family_history=="Yes"}
        st.session_state["patient_data"] = patient_data
        st.session_state["analysis_result"] = analyze_data(patient_data)

    if "analysis_result" in st.session_state:
        data = st.session_state["patient_data"]
        result = st.session_state["analysis_result"]
        report = build_report(data,result)
        st.markdown("### Analysis result")
        if not result["valid"]:
            st.error("Analysis could not be completed. Check the following:")
            for error in result["errors"]: st.write(f"- {error}")
        else:
            st.markdown('<div class="result"><div class="result-label">Fasting glucose indicator</div><div class="result-value">'+result["classification_label"]+'</div>'+result["summary"]+'</div>',unsafe_allow_html=True)
            for warning in result.get("warnings",[]): st.warning(warning)
            st.markdown("#### Other indicators")
            cols=st.columns(3)
            metrics=[("BMI",f'{data["bmi"]:.1f}',result["indicators"]["bmi"]["classification"]),("Blood pressure",f'{data["systolic_bp"]}/{data["diastolic_bp"]}',result["indicators"]["blood_pressure"]["classification"]),("Family history","Yes" if data["family_history"] else "No","Context only")]
            for col,(name,value,note) in zip(cols,metrics):
                with col: st.markdown(f'<div class="metric-card"><div class="metric-name">{name}</div><div class="metric-value">{value}</div><div class="muted">{note}</div></div>',unsafe_allow_html=True)
            st.caption("BMI, blood pressure, age, family history and insulin are independent context. They do not change the glucose classification.")
            with st.expander("Why did I get this result?"):
                st.write(report["summary"])
                for rule in report["triggered_rules"]:
                    st.markdown(f'**{rule["rule_id"]} · {rule["name"]}** — {rule["result"]}')
                    st.caption(rule["explanation"])
            with st.expander("Charts and indicator details"):
                t1,t2,t3=st.tabs(["Glucose","Blood pressure & BMI","Rule activity"])
                with t1:
                    fig=glucose_reference_chart(data["glucose"],data["glucose_type"]); st.pyplot(fig,use_container_width=True); plt.close(fig)
                with t2:
                    fig=indicator_bar_chart(data); st.pyplot(fig,use_container_width=True); plt.close(fig)
                    fig=bmi_reference_chart(data["bmi"]); st.pyplot(fig,use_container_width=True); plt.close(fig)
                with t3:
                    fig=triggered_rules_chart(result); st.pyplot(fig,use_container_width=True); plt.close(fig)
            with st.expander("Full report"):
                st.markdown("**Triggered rules**")
                st.dataframe([{"Rule ID":r["rule_id"],"Rule":r["name"],"Indicator":r["indicator"],"Result":r["result"],"Explanation":r["explanation"],"Source":r["source"]} for r in report["triggered_rules"]],use_container_width=True,hide_index=True)
                st.markdown("**Independent indicators**")
                for item in report.get("contextual_indicators",[]): st.write(f"- {item}")
                st.markdown("**General notes**")
                for item in report["recommendations"]: st.write(f"- {item}")
                st.caption(report["disclaimer"])

elif page=="Rule library":
    st.markdown("### Rule library")
    st.caption(f"{RULE_COUNT} transparent rules used by the educational analysis engine.")
    category=st.selectbox("Filter by indicator",["All"]+sorted({r["indicator"] for r in RULES}))
    st.dataframe(RULES if category=="All" else [r for r in RULES if r["indicator"]==category],use_container_width=True,hide_index=True)

elif page=="About":
    st.markdown("### About this project")
    st.markdown("""This is a transparent, rule-based educational project. It does not use machine learning, weighted scoring, or probability estimates.\n\n- Final indicator classification is based only on fasting glucose.\n- Random or unknown glucose measurements do not receive fasting classification.\n- BMI and blood pressure are displayed independently.\n- Insulin is optional and display-only.\n- The project is scoped to adults aged 20 and older.""")
    with st.expander("Synthetic demonstration dataset"):
        st.caption("Artificial demo counts only; not population prevalence or clinical evidence.")
        fig=synthetic_demo_chart(); st.pyplot(fig,use_container_width=True); plt.close(fig)
    with st.expander("Automated test cases"):
        st.caption("PASS indicates that actual output matched expected synthetic test output.")
        st.dataframe(run_test_case_table(),use_container_width=True,hide_index=True)

st.markdown('<div class="muted" style="text-align:center;padding:28px 0 8px">Diabetes Risk Analysis · Educational project · 27 transparent rules</div>',unsafe_allow_html=True)
