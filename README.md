# Team Cascade — N-Tier Supply Chain Risk Intelligence

> **One-line description:** Supplier risk hides upstream. We trace it, explain it in plain English, and say how sure we are. Built on Snowflake.

## Problem & Solution
Supply chain visibility into Tier-1 suppliers is standard, but Tier-2+ risks are often invisible until customer orders are impacted. Team Cascade builds a governed, ontology-grounded intelligence layer on Snowflake that:
1. **Detects** risk propagating from any tier using recursive SQL closure tables.
2. **Explains** impact with confidence decay scoring ($0.00 - 1.00$).
3. **Alerts** stakeholders automatically via automated risk logging.

---

## Quickstart Setup
1. Execute SQL scripts sequentially: `sql/01_setup_schemas.sql` through `sql/06_semantic_layer.sql`.
2. Run automation script: `automation/scheduled_risk_task.sql`.
3. Launch Streamlit UI: `cd streamlit && streamlit run app.py`.
