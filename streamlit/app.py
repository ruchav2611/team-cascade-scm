import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Team Cascade — N-Tier Risk Intelligence", layout="wide")
session = get_active_session()

st.title("Team Cascade — N-Tier Risk Intelligence")

tab1, tab2, tab3 = st.tabs(["💬 Persona Q&A Agent", "🔍 Cortex Search & Vector AI", "⚡ Automated Risk Alerts"])

with tab1:
    st.subheader("Query Supply Chain Risk")
    col1, col2 = st.columns([1, 3])
    with col1:
        persona = st.radio("Select Persona View", ["Procurement", "Planning", "Logistics"])
        st.info(f"**Persona View:** {persona}")
    with col2:
        query_type = st.selectbox(
            "Quick Scenarios",
            ["All Impacted Supply Chains", "High Risk Scores (> 4.0)", "Tier-2+ Deep Cascades", "Delayed Shipments"]
        )
        if query_type == "High Risk Scores (> 4.0)":
            sql_query = "SELECT * FROM SCM.ONT.SV_SUPPLY_CHAIN WHERE ROW_RISK_SCORE > 4.00"
        elif query_type == "Tier-2+ Deep Cascades":
            sql_query = "SELECT * FROM SCM.ONT.SV_SUPPLY_CHAIN WHERE TIER_DEPTH >= 1"
        elif query_type == "Delayed Shipments":
            sql_query = "SELECT * FROM SCM.ONT.SV_SUPPLY_CHAIN WHERE SHIPMENT_STATUS = 'DELAYED'"
        else:
            sql_query = "SELECT * FROM SCM.ONT.SV_SUPPLY_CHAIN"

        if st.button("Execute Query", type="primary"):
            df = session.sql(sql_query).to_pandas()
            if persona == "Procurement":
                cols = ["ROOT_SUPPLIER_NAME", "TIER_DEPTH", "CONTRACT_ID", "PENALTY_PCT", "ROW_RISK_SCORE"]
            elif persona == "Planning":
                cols = ["ROOT_SUPPLIER_NAME", "ORDER_ID", "PART_NAME", "PLANT_NAME", "DAYS_TO_IMPACT", "ROW_RISK_SCORE"]
            else:
                cols = ["ROOT_SUPPLIER_NAME", "SHIPMENT_ID", "SHIPMENT_STATUS", "IS_ON_TIME", "DAYS_TO_IMPACT"]
            st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True)

with tab2:
    st.subheader("Cortex Vector Search & LLM Analysis")
    search_query = st.text_input("Semantic Search over Contract Terms:", "penalty clauses and force majeure")
    
    if st.button("Search Contracts with Cortex Vector Embeddings"):
        with st.spinner("Searching vectors via Cortex..."):
            # Vector Similarity Search using Arctic Embeddings
            results = session.sql(f"""
                SELECT 
                    CONTRACT_ID,
                    SUPPLIER_ID,
                    PENALTY_CLAUSE_TEXT,
                    PENALTY_PCT,
                    VECTOR_COSINE_SIMILARITY(
                        SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{search_query}'),
                        SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', PENALTY_CLAUSE_TEXT)
                    ) AS SIMILARITY_SCORE
                FROM SCM.ONT.CONTRACT_SEARCH_BASE
                ORDER BY SIMILARITY_SCORE DESC
                LIMIT 5
            """).to_pandas()
            
            st.dataframe(results, use_container_width=True)
            
            if not results.empty:
                top_clause = results["PENALTY_CLAUSE_TEXT"].iloc[0]
                with st.spinner("Analyzing top result with Cortex LLM..."):
                    summary = session.sql(f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'mistral-large2',
                            'You are Team Cascade risk analyst. Summarize key financial risks from this clause in 2 bullet points: {top_clause}'
                        ) AS SUMMARY
                    """).collect()[0]["SUMMARY"]
                    st.success(f"**Cortex LLM Summary:**\n\n{summary}")

with tab3:
    st.subheader("Automated Detected Alerts")
    if st.button("Refresh Alerts"):
        st.rerun()
    alerts_df = session.sql("SELECT * FROM SCM.ONT.DETECTED_RISK_ALERTS ORDER BY DETECTED_AT DESC").to_pandas()
    st.dataframe(alerts_df, use_container_width=True)
