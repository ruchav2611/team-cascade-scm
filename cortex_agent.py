import json
from snowflake.snowpark.context import get_active_session

GUARDRAIL_SYSTEM_PROMPT = """
You are the Cortex Agent for Team Cascade Supply Chain Risk Control.
Follow these mandatory operating guardrails at all times:
1. For any sub-tier entities beyond Tier 1 (Tier 2+), you MUST explicitly state the path confidence score and the source origin type.
2. If any path confidence score is below 0.40, explicitly flag that link as an "unverified lead" rather than a confirmed supplier relationship.
3. REFUSE to guess, speculate, or extrapolate on unknown supplier branches or missing data in the ontology graph.
4. Align all responses to the user's operational persona context.
"""

def execute_supplier_cascade(session, root_supplier_name: str):
    sql = f"""
        SELECT 
            ANCESTOR_SUPPLIER_NAME,
            DESCENDANT_SUPPLIER_NAME,
            TIER_DEPTH,
            PATH_CONFIDENCE,
            HOP_PATH
        FROM SCM.ONT.SUPPLIER_CLOSURE
        WHERE UPPER(ANCESTOR_SUPPLIER_NAME) LIKE '%{root_supplier_name.upper()}%'
        ORDER BY TIER_DEPTH, PATH_CONFIDENCE DESC;
    """
    return session.sql(sql).to_pandas()

def execute_contract_exposure(session, query_text: str):
    sql = f"""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            'SCM.ONT.CONTRACT_SEARCH_INDEX',
            '{{"query": "{query_text}", "columns": ["SUPPLIER_NAME", "PENALTY_PCT", "SLA_DAYS", "PENALTY_CLAUSE_TEXT"], "limit": 3}}'
        ) AS SEARCH_RESULTS;
    """
    raw = session.sql(sql).collect()[0]["SEARCH_RESULTS"]
    return json.loads(raw).get("results", [])

def execute_persona_summary(session, persona: str):
    sql = """
        SELECT 
            COUNT(DISTINCT ROOT_SUPPLIER_ID) AS TOTAL_ROOT_SUPPLIERS,
            AVG(ROW_RISK_SCORE) AS AVG_RISK_SCORE,
            AVG(PATH_CONFIDENCE) AS AVG_CONFIDENCE,
            MIN(DAYS_TO_IMPACT) AS MIN_DAYS_TO_IMPACT
        FROM SCM.ONT.SV_SUPPLY_CHAIN;
    """
    return session.sql(sql).to_pandas()

def run_agent_query(session, user_query: str, persona: str = "Procurement"):
    clean_query = user_query.lower()
    if "contract" in clean_query or "penalty" in clean_query or "sla" in clean_query:
        tool_results = execute_contract_exposure(session, user_query)
        tool_name = "contract_exposure"
    elif "cascade" in clean_query or "tier" in clean_query or "supplier" in clean_query:
        tool_results = execute_supplier_cascade(session, "")
        tool_name = "supplier_cascade"
    else:
        tool_results = execute_persona_summary(session, persona)
        tool_name = "persona_summary"

    prompt = f"""
    {GUARDRAIL_SYSTEM_PROMPT}

    User Persona: {persona}
    Executed Tool: {tool_name}
    Tool Data Output: {json.dumps(str(tool_results))}

    User Query: {user_query}

    Provide a concise, grounded response following all guardrails.
    """

    escaped_prompt = prompt.replace("'", "''")
    llm_sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large3', '{escaped_prompt}') AS RESPONSE;"
    response = session.sql(llm_sql).collect()[0]["RESPONSE"]
    return response, tool_name, tool_results
