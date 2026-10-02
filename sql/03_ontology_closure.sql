USE DATABASE SCM;
USE SCHEMA ONT;

CREATE OR REPLACE TABLE ONT_CLASS (
    CLASS_NAME    VARCHAR(100) PRIMARY KEY,
    PARENT_CLASS  VARCHAR(100),
    IS_ABSTRACT   BOOLEAN,
    DESCRIPTION   VARCHAR(500)
);

INSERT INTO ONT_CLASS VALUES
    ('SupplyChainParty', NULL, TRUE,  'Abstract grouping for any node in the chain'),
    ('Supplier',         'SupplyChainParty', FALSE, 'Any tier of supplier, self-referencing'),
    ('Customer',         'SupplyChainParty', FALSE, 'End recipient of an Order'),
    ('Plant',            'SupplyChainParty', FALSE, 'Manufacturing/assembly facility'),
    ('Part',             NULL, FALSE, 'A component sourced from a Supplier'),
    ('Order',            NULL, FALSE, 'Customer demand fulfilled by a Plant'),
    ('Shipment',         NULL, FALSE, 'Movement of a Part or finished good'),
    ('Contract',         NULL, FALSE, 'Governs terms of a Tier-1 Supplier relationship');

CREATE OR REPLACE VIEW V_SUPPLIER_CONFIDENCE AS
SELECT
    SUPPLIER_ID,
    PARENT_SUPPLIER_ID,
    SOURCE_TYPE,
    DATEDIFF('day', SOURCE_LAST_UPDATED, CURRENT_DATE()) AS days_stale,
    CASE SOURCE_TYPE
        WHEN 'TRADE_DATA_VERIFIED' THEN 0.90
        WHEN 'THIRD_PARTY_INTEL'   THEN 0.80
        WHEN 'SELF_DISCLOSED'      THEN 0.60
        ELSE 0.00
    END
    * CASE
        WHEN DATEDIFF('day', SOURCE_LAST_UPDATED, CURRENT_DATE()) > 540 THEN 0.5
        WHEN DATEDIFF('day', SOURCE_LAST_UPDATED, CURRENT_DATE()) > 180 THEN 0.8
        ELSE 1.0
      END AS confidence_score
FROM SCM.RAW.SUPPLIER
WHERE PARENT_SUPPLIER_ID IS NOT NULL;

CREATE OR REPLACE TABLE SUPPLIER_CLOSURE AS
WITH RECURSIVE chain AS (
    SELECT
        SUPPLIER_ID AS descendant,
        SUPPLIER_ID AS ancestor,
        0 AS tier_depth,
        1.0 AS path_confidence
    FROM SCM.RAW.SUPPLIER

    UNION ALL

    SELECT
        c.descendant AS descendant,
        s.PARENT_SUPPLIER_ID AS ancestor,
        c.tier_depth + 1 AS tier_depth,
        c.path_confidence * COALESCE(vc.confidence_score, 0.6) AS path_confidence
    FROM chain c
    JOIN SCM.RAW.SUPPLIER s ON s.SUPPLIER_ID = c.ancestor
    LEFT JOIN SCM.ONT.V_SUPPLIER_CONFIDENCE vc ON vc.SUPPLIER_ID = s.PARENT_SUPPLIER_ID
    WHERE s.PARENT_SUPPLIER_ID IS NOT NULL
)
SELECT descendant, ancestor, tier_depth, path_confidence FROM chain;
