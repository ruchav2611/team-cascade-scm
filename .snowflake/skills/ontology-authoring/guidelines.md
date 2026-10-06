# Ontology Authoring Guidelines

## Confidence Score Rules
- **Source Type Multipliers**:
  - `TRADE_DATA_VERIFIED`: 0.95
  - `SELF_DISCLOSED`: 0.75
  - `THIRD_PARTY_INTEL`: 0.60
  - `UNKNOWN`: 0.30
- **Recency Decay**:
  - Apply 0.90 penalty multiplier if `LAST_UPDATED_DATE` is > 12 months old.

## Multi-Hop Path Multiplication
Path confidence is calculated recursively:
29766Confidence_{path} = \prod_{i=1}^{N} HopConfidence_i29766

## View Schema Requirements
The resulting ontology view (`SV_SUPPLY_CHAIN`) must expose:
- `ROOT_SUPPLIER_ID` & `ROOT_SUPPLIER_NAME`
- `TIER_DEPTH` & `PATH_CONFIDENCE`
- `ROW_RISK_SCORE`
- `DAYS_TO_IMPACT`
