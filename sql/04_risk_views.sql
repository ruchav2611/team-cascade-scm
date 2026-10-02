USE DATABASE SCM;
USE SCHEMA ONT;

CREATE OR REPLACE VIEW V_SUPPLY_RISK AS
SELECT
    sc.ancestor         AS root_supplier_id,
    sc.descendant       AS impacted_supplier_id,
    sc.tier_depth,
    sc.path_confidence,
    p.PART_ID,
    pl.PLANT_ID,
    o.ORDER_ID,
    o.CUSTOMER_ID,
    o.PROMISED_DATE,
    DATEDIFF('day', CURRENT_DATE(), o.PROMISED_DATE) AS days_to_impact,
    sh.SHIPMENT_ID,
    sh.STATUS            AS shipment_status,
    c.CONTRACT_ID,
    c.PENALTY_PCT
FROM SCM.ONT.SUPPLIER_CLOSURE sc
JOIN SCM.RAW.PART p           ON p.SUPPLIER_ID = sc.descendant
JOIN SCM.RAW.PLANT_PART_BOM b ON b.PART_ID = p.PART_ID
JOIN SCM.RAW.PLANT pl         ON pl.PLANT_ID = b.PLANT_ID
JOIN SCM.RAW.ORDER_ o         ON o.PLANT_ID = pl.PLANT_ID
LEFT JOIN SCM.RAW.SHIPMENT sh ON sh.PART_ID = p.PART_ID AND sh.LEG_TYPE = 'INBOUND'
LEFT JOIN SCM.RAW.CONTRACT c  ON c.SUPPLIER_ID = sc.ancestor
WHERE sh.STATUS = 'DELAYED';
