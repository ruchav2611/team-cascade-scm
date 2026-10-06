---
name: ontology-authoring
description: Reusable skill for constructing and validating recursive supply chain graph ontologies with confidence scoring and risk views in Snowflake.
---

# Ontology Authoring Skill

This skill provides standard workflows for building N-tier supply chain closure graphs and ontology views.

## Core Capabilities
1. **Closure Graph Construction**: Recursive traversal of supplier parent-child hierarchies ().
2. **Confidence Decay Calculation**: Multiplies source reliability weights (\_DATA\_VERIFIED$, \_DISCLOSED$, etc.) across hops.
3. **Ontology View Assembly**: Joins supplier nodes $ightarrow$ parts $ightarrow$ plants $ightarrow$ orders $ightarrow$ contracts ().

## Execution Workflow
Refer to `guidelines.md` for exact SQL generation patterns and confidence calculation formulas.
