import streamlit as st
import pandas as pd
import json
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Team Cascade — SCM Risk Portal", layout="wide")

@st.cache_resource
def init_session():
    return get_active_session()

session = init_session()

st.title("🛡️ Team Cascade — N-Tier Supply Chain Risk Control")
st.caption("Governed, ontology-grounded risk detection & multi-tier cascade impact analytics.")

persona = st.sidebar.selectbox(
    "Select Operating Persona",
    ["Procurement", "Planning", "Logistics"],
    help="Filters emphasis and metrics based on persona objectives."
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Active Persona:** `{persona}`")

tab_qa, tab_analytics, tab_alerts = st.tabs([
    "💬 Semantic Assistant & Contract Search", 
    "📊 Risk Heatmap & Cascade Analytics", 
    "🚨 Live Risk Alerts"
])

# ---------------------------------------------------------
# TAB 1: Semantic Q&A & Cortex Search
# ---------------------------------------------------------
with tab_qa:
    st.subheader("Cortex Semantic Contract Search")
    query_text = st.text_input(
        "Ask a supply chain question or search contract penalty terms:", 
        placeholder="e.g. penalty for late delivery beyond 5 days"
    )
    
    if query_text:
        st.info(f"Executing Cortex Hybrid Search for **{persona}** persona...")
        try:
            # Execute Cortex Search Service Query
            search_sql = f"""
                SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    'SCM.ONT.CONTRACT_SEARCH_INDEX',
                    '{{"query": "{query_text}", "columns": ["SUPPLIER_NAME", "PENALTY_PCT", "SLA_DAYS", "PENALTY_CLAUSE_TEXT"], "limit": 5}}'
                ) AS SEARCH_RESULTS;
            """
            raw_res = session.sql(search_sql).collect()[0]["SEARCH_RESULTS"]
            res_json = json.loads(raw_res)
            
            results_list = res_json.get("results", [])
            if results_list:
                st.write(f"### Matched Contract Clauses ({len(results_list)})")
                res_df = pd.DataFrame(results_list)
                # Clean up score columns display
                if "@scores" in res_df.columns:
                    res_df["Match Score"] = res_df["@scores"].apply(lambda x: round(x.get("reranker_score", 0), 2) if isinstance(x, dict) else 0)
                    res_df = res_df.drop(columns=["@scores"])
                
                st.dataframe(res_df, use_container_width=True)
            else:
                st.warning("No matching contract terms found.")
        except Exception as e:
            st.error(f"Cortex Search Execution Error: {e}")

# ---------------------------------------------------------
# TAB 2: Risk Heatmap & Analytics
# ---------------------------------------------------------
with tab_analytics:
    st.subheader("Multi-Tier Cascade Impact & Risk Heatmap")
    
    df_raw = session.sql("SELECT * FROM SCM.ONT.SV_SUPPLY_CHAIN ORDER BY ROW_RISK_SCORE DESC").to_pandas()
    
    if not df_raw.empty:
        if persona == "Procurement":
            st.markdown("##### Persona Focus: *Supplier Exposure & Contract Penalties*")
            display_cols = ["ROOT_SUPPLIER_NAME", "TIER_DEPTH", "ROW_RISK_SCORE", "PENALTY_PCT", "CONTRACT_ID", "PART_NAME"]
        elif persona == "Planning":
            st.markdown("##### Persona Focus: *Order Disruption & Days to Impact*")
            display_cols = ["ORDER_ID", "PLANT_NAME", "DAYS_TO_IMPACT", "ROW_RISK_SCORE", "ROOT_SUPPLIER_NAME", "TIER_DEPTH"]
        else:
            st.markdown("##### Persona Focus: *Inbound Shipment Status & Delivery Performance*")
            display_cols = ["SHIPMENT_ID", "SHIPMENT_STATUS", "IS_ON_TIME", "PLANT_NAME", "ROOT_SUPPLIER_NAME", "ROW_RISK_SCORE"]
            
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Max Risk Score", f"{df_raw['ROW_RISK_SCORE'].max():.1f}")
        col2.metric("At-Risk Orders", len(df_raw['ORDER_ID'].unique()))
        col3.metric("Deepest Tier Depth", f"Tier-{int(df_raw['TIER_DEPTH'].max())}")
        col4.metric("Avg Days to Impact", f"{df_raw['DAYS_TO_IMPACT'].mean():.1f} Days")
        
        st.markdown("---")
        st.markdown("### Supplier Risk Exposure Ranking")
        st.bar_chart(data=df_raw, x="ROOT_SUPPLIER_NAME", y="ROW_RISK_SCORE", color="TIER_DEPTH")
        
        st.markdown(f"### {persona} Data Framing")
        st.dataframe(
            df_raw[display_cols].style.background_gradient(subset=["ROW_RISK_SCORE"], cmap="YlOrRd"), 
            use_container_width=True
        )
    else:
        st.info("No risk cascade data available in SCM.ONT.SV_SUPPLY_CHAIN.")

# ---------------------------------------------------------
# TAB 3: Automated Risk Alerts Table
# ---------------------------------------------------------
with tab_alerts:
    st.subheader("Automated Background Risk Detections")
    st.caption("Live feed populated automatically by scheduled CoCo risk detection tasks.")
    
    alerts_df = session.sql("SELECT ALERT_ID, SEVERITY, RISK_TYPE, DESCRIPTION, DETECTED_AT FROM SCM.ONT.DETECTED_RISK_ALERTS ORDER BY DETECTED_AT DESC").to_pandas()
    
    if not alerts_df.empty:
        for idx, row in alerts_df.iterrows():
            severity = row["SEVERITY"]
            if severity == "CRITICAL":
                st.error(f"**[{severity}]** {row['DESCRIPTION']} *(Detected: {row['DETECTED_AT']})*")
            elif severity == "HIGH":
                st.warning(f"**[{severity}]** {row['DESCRIPTION']} *(Detected: {row['DETECTED_AT']})*")
            else:
                st.info(f"**[{severity}]** {row['DESCRIPTION']} *(Detected: {row['DETECTED_AT']})*")
        
        st.markdown("---")
        st.dataframe(alerts_df, use_container_width=True)
    else:
        st.success("No active critical risk alerts detected.")
