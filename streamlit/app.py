import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Team Cascade — Supply Chain Risk", layout="wide")
session = get_active_session()

st.title("Team Cascade — N-Tier Risk Intelligence")

tab1, tab2 = st.tabs(["Q&A Agent", "Automated Alerts"])

with tab1:
    st.subheader("Ask Supply Chain Questions")
    persona = st.selectbox("Select Persona", ["Procurement", "Planning", "Logistics"])
    query = st.text_input("Enter query:", "What is my supply risk this week?")
    
    if st.button("Run Query"):
        df = session.sql("SELECT * FROM SCM.ONT.SV_SUPPLY_CHAIN").to_pandas()
        st.write(f"**Framing for {persona}:**")
        if persona == "Procurement":
            st.dataframe(df[["ROOT_SUPPLIER_NAME", "CONTRACT_ID", "PENALTY_PCT", "ROW_RISK_SCORE"]])
        elif persona == "Planning":
            st.dataframe(df[["ORDER_ID", "PART_NAME", "PLANT_NAME", "DAYS_TO_IMPACT"]])
        else:
            st.dataframe(df[["SHIPMENT_ID", "SHIPMENT_STATUS", "IS_ON_TIME"]])

with tab2:
    st.subheader("Automated Risk Alerts")
    alerts_df = session.sql("SELECT * FROM SCM.ONT.DETECTED_RISK_ALERTS ORDER BY DETECTED_AT DESC").to_pandas()
    st.dataframe(alerts_df)
