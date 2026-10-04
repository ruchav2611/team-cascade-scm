import streamlit as st
import pandas as pd
import json
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Team Cascade Supply Chain Risk Control", layout="wide")

# Custom Enterprise CSS (Forced Blue Palette & Layout Polish)
st.markdown("""
<style>
    /* 1. Remove Top Padding */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 98% !important;
    }
    
    /* 2. Header Typography */
    .app-header-title {
        color: #0F2C59;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-bottom: 2px !important;
        line-height: 1.2 !important;
    }
    .app-header-sub {
        color: #64748B;
        font-size: 13px !important;
        margin-bottom: 0px !important;
    }
    
    /* 3. Force Primary Buttons to Brand Blue (Override Streamlit Red) */
    button[kind="primary"], .stButton>button[kind="primary"] {
        background-color: #008DDA !important;
        border-color: #008DDA !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 4px !important;
    }
    button[kind="primary"]:hover, .stButton>button[kind="primary"]:hover {
        background-color: #006DAA !important;
        border-color: #006DAA !important;
        color: #FFFFFF !important;
    }
    
    /* 4. Subtle Light-Blue Background for Persona Selector */
    div[data-testid="stSelectbox"] {
        background-color: #EBF5FB;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #D4E6F1;
    }
    
    /* 5. Aligned, Low-Profile Sign Out Button */
    .user-profile-box {
        text-align: right;
    }
    .signout-btn button {
        background-color: transparent !important;
        color: #64748B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 4px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 2px 10px !important;
        margin-top: 4px !important;
        float: right !important;
    }
    .signout-btn button:hover {
        background-color: #F1F5F9 !important;
        color: #0F2C59 !important;
        border-color: #94A3B8 !important;
    }
    
    /* 6. Sub Tabs Blue Highlight Line */
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        padding-bottom: 8px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #008DDA !important;
        border-bottom-color: #008DDA !important;
        border-bottom-width: 3px !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #008DDA !important;
    }

    /* Metric Card Polish */
    div[data-testid="stMetricValue"] {
        color: #0F2C59;
        font-size: 24px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for backward-compatible rerun in Streamlit-in-Snowflake
def trigger_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "persona" not in st.session_state:
    st.session_state.persona = "Procurement"

# ---------------------------------------------------------
# 1. ENTERPRISE LOGIN SCREEN
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("<div class='app-header-title'>Team Cascade Supply Chain Risk Control</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-header-sub'>Enterprise Risk Detection and Multi-Tier Impact Analysis</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.subheader("System Authentication")
        st.write("Enter authorized organizational credentials to access the portal.")
        
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="password123")
        
        login_btn = st.button("Sign In", type="primary", use_container_width=True)
        
        if login_btn:
            if username == "admin" and password == "password123":
                st.session_state.authenticated = True
                trigger_rerun()
            else:
                st.error("Authentication failed. Invalid username or password.")
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("""
        **Default Evaluation Credentials**
        * **Username:** admin
        * **Password:** password123
        """)
    st.stop()

# ---------------------------------------------------------
# 2. AUTHENTICATED TOP HEADER BAR
# ---------------------------------------------------------
@st.cache_resource
def init_session():
    return get_active_session()

session = init_session()

# Compact Top Header Layout with Vertically Stacked Profile
top_col1, top_col2, top_col3 = st.columns([2.5, 1.2, 0.8])

with top_col1:
    st.markdown("<div class='app-header-title'>Team Cascade Supply Chain Risk Control</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-header-sub'>Multi-Tier Risk Visibility and Intelligence Platform</div>", unsafe_allow_html=True)

with top_col2:
    st.session_state.persona = st.selectbox(
        "Operating Persona",
        ["Procurement", "Planning", "Logistics"],
        index=["Procurement", "Planning", "Logistics"].index(st.session_state.persona)
    )

with top_col3:
    st.markdown("<div class='user-profile-box'>User: <b>System Admin</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='signout-btn'>", unsafe_allow_html=True)
    if st.button("Sign Out"):
        st.session_state.authenticated = False
        trigger_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 8px 0px 16px 0px; border-color: #E2E8F0;'>", unsafe_allow_html=True)

# Reordered Main Navigation Tabs
tab_alerts, tab_analytics, tab_qa = st.tabs([
    "System Risk Alerts",
    "Risk Heatmap and Risk Analytics", 
    "Contract Analysis and Assistant"
])

# ---------------------------------------------------------
# TAB A: Automated Risk Alerts
# ---------------------------------------------------------
with tab_alerts:
    st.subheader("Automated Risk Detections")
    st.caption("Active risk feed from automated system monitoring tasks.")
    
    alerts_df = session.sql("SELECT ALERT_ID, SEVERITY, RISK_TYPE, DESCRIPTION, DETECTED_AT FROM SCM.ONT.DETECTED_RISK_ALERTS ORDER BY DETECTED_AT DESC").to_pandas()
    
    if not alerts_df.empty:
        for idx, row in alerts_df.iterrows():
            severity = row["SEVERITY"]
            if severity == "CRITICAL":
                st.error(f"**[{severity}]** {row['DESCRIPTION']} (Detected: {row['DETECTED_AT']})")
            elif severity == "HIGH":
                st.warning(f"**[{severity}]** {row['DESCRIPTION']} (Detected: {row['DETECTED_AT']})")
            else:
                st.info(f"**[{severity}]** {row['DESCRIPTION']} (Detected: {row['DETECTED_AT']})")
        
        st.markdown("---")
        st.dataframe(alerts_df, use_container_width=True)
    else:
        st.success("No critical risk alerts currently flagged.")

# ---------------------------------------------------------
# TAB B: Risk Analytics & Impact Heatmap
# ---------------------------------------------------------
with tab_analytics:
    st.subheader("Multi-Tier Cascade Impact Analysis")
    
    df_raw = session.sql("SELECT * FROM SCM.ONT.SV_SUPPLY_CHAIN ORDER BY ROW_RISK_SCORE DESC").to_pandas()
    
    if not df_raw.empty:
        persona = st.session_state.persona
        if persona == "Procurement":
            st.markdown("#### Focus: Supplier Exposure and Contract Terms")
            display_cols = ["ROOT_SUPPLIER_NAME", "TIER_DEPTH", "ROW_RISK_SCORE", "PENALTY_PCT", "CONTRACT_ID", "PART_NAME"]
        elif persona == "Planning":
            st.markdown("#### Focus: Order Disruption and Schedule Impact")
            display_cols = ["ORDER_ID", "PLANT_NAME", "DAYS_TO_IMPACT", "ROW_RISK_SCORE", "ROOT_SUPPLIER_NAME", "TIER_DEPTH"]
        else:
            st.markdown("#### Focus: Inbound Shipment Status and Delivery Performance")
            display_cols = ["SHIPMENT_ID", "SHIPMENT_STATUS", "IS_ON_TIME", "PLANT_NAME", "ROOT_SUPPLIER_NAME", "ROW_RISK_SCORE"]
            
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Maximum Risk Score", f"{df_raw['ROW_RISK_SCORE'].max():.1f}")
        col2.metric("Orders Affected", len(df_raw['ORDER_ID'].unique()))
        col3.metric("Maximum Tier Depth", f"Tier {int(df_raw['TIER_DEPTH'].max())}")
        col4.metric("Average Days to Impact", f"{df_raw['DAYS_TO_IMPACT'].mean():.1f} Days")
        
        st.markdown("---")
        st.markdown("### Supplier Risk Exposure")
        
        chart_data = df_raw.set_index("ROOT_SUPPLIER_NAME")[["ROW_RISK_SCORE"]]
        st.bar_chart(chart_data)
        
        st.markdown(f"### Detailed Data ({persona} View)")
        st.dataframe(df_raw[display_cols], use_container_width=True)
    else:
        st.info("No active risk records available.")

# ---------------------------------------------------------
# TAB C: Contract Analysis & RAG Assistant
# ---------------------------------------------------------
with tab_qa:
    st.subheader("Contract Penalty Search and Clause Analysis")
    query_text = st.text_input(
        "Search contract clauses or query vendor obligations:", 
        placeholder="e.g. What are the penalty clauses for delays exceeding 5 days?"
    )
    
    if query_text:
        st.info(f"Analyzing contracts for {st.session_state.persona} persona...")
        try:
            search_sql = f"""
                SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    'SCM.ONT.CONTRACT_SEARCH_INDEX',
                    '{{"query": "{query_text}", "columns": ["SUPPLIER_NAME", "PENALTY_PCT", "SLA_DAYS", "PENALTY_CLAUSE_TEXT"], "limit": 3}}'
                ) AS SEARCH_RESULTS;
            """
            raw_res = session.sql(search_sql).collect()[0]["SEARCH_RESULTS"]
            res_json = json.loads(raw_res)
            results_list = res_json.get("results", [])
            
            if results_list:
                context_str = ""
                for idx, r in enumerate(results_list, 1):
                    context_str += f"[{idx}] Supplier: {r.get('SUPPLIER_NAME')} | SLA: {r.get('SLA_DAYS')} days | Penalty: {r.get('PENALTY_PCT')}% | Clause: {r.get('PENALTY_CLAUSE_TEXT')}\n"
                
                prompt = f"""
                You are a enterprise supply chain risk expert assisting a {st.session_state.persona} Manager.
                Answer the query accurately using ONLY the contract context provided below.

                Context:
                {context_str}

                Query: {query_text}

                Provide a clear executive summary followed by key contract details.
                """

                clean_prompt = prompt.replace("'", "''")
                llm_sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large3', '{clean_prompt}') AS LLM_RESPONSE;"
                llm_response = session.sql(llm_sql).collect()[0]["LLM_RESPONSE"]
                
                st.markdown("### Executive Summary")
                st.write(llm_response)
                
                with st.expander("Retrieved Contract Evidence"):
                    res_df = pd.DataFrame(results_list)
                    if "@scores" in res_df.columns:
                        res_df = res_df.drop(columns=["@scores"])
                    st.dataframe(res_df, use_container_width=True)
            else:
                st.warning("No matching contract clauses found for the specified query.")
        except Exception as e:
            st.error(f"Search Execution Error: {e}")
