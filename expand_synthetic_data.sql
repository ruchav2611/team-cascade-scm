-- 1. Ensure all RAW tables exist
CREATE TABLE IF NOT EXISTS SCM.RAW.SUPPLIER (
    SUPPLIER_ID         VARCHAR(36) PRIMARY KEY,
    SUPPLIER_NAME       VARCHAR(200),
    PARENT_SUPPLIER_ID  VARCHAR(36),
    REGION              VARCHAR(100),
    IS_ACTIVE           BOOLEAN DEFAULT TRUE,
    SOURCE_TYPE         VARCHAR(30),
    SOURCE_LAST_UPDATED DATE,
    CONFIDENCE_SCORE    NUMBER(3,2)
);

CREATE TABLE IF NOT EXISTS SCM.RAW.CONTRACT (
    CONTRACT_ID          VARCHAR(36) PRIMARY KEY,
    SUPPLIER_ID          VARCHAR(36),
    PENALTY_CLAUSE_TEXT  VARCHAR(2000),
    PENALTY_PCT          NUMBER(5,2),
    SLA_DAYS             INTEGER
);

CREATE TABLE IF NOT EXISTS SCM.RAW.PART (
    PART_ID           VARCHAR(36) PRIMARY KEY,
    PART_NAME         VARCHAR(200),
    SUPPLIER_ID       VARCHAR(36),
    UNIT_COST         NUMBER(12,2)
);

CREATE TABLE IF NOT EXISTS SCM.RAW.PLANT (
    PLANT_ID          VARCHAR(36) PRIMARY KEY,
    PLANT_NAME        VARCHAR(200),
    REGION            VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS SCM.RAW.PLANT_PART_BOM (
    PLANT_ID          VARCHAR(36),
    PART_ID           VARCHAR(36),
    QTY_PER_UNIT      NUMBER(10,2),
    PRIMARY KEY (PLANT_ID, PART_ID)
);

CREATE TABLE IF NOT EXISTS SCM.RAW.CUSTOMER (
    CUSTOMER_ID       VARCHAR(36) PRIMARY KEY,
    CUSTOMER_NAME     VARCHAR(200),
    REGION            VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS SCM.RAW.ORDER_ (
    ORDER_ID          VARCHAR(36) PRIMARY KEY,
    CUSTOMER_ID       VARCHAR(36),
    PLANT_ID          VARCHAR(36),
    ORDER_DATE        DATE,
    PROMISED_DATE     DATE,
    QTY_ORDERED       NUMBER(12,2),
    QTY_FULFILLED     NUMBER(12,2) DEFAULT 0,
    STATUS            VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS SCM.RAW.SHIPMENT (
    SHIPMENT_ID       VARCHAR(36) PRIMARY KEY,
    ORIGIN_ID         VARCHAR(36),
    DESTINATION_ID    VARCHAR(36),
    LEG_TYPE          VARCHAR(20),
    PART_ID           VARCHAR(36),
    ORDER_ID          VARCHAR(36),
    ROUTE_ID          VARCHAR(36),
    QTY_SHIPPED       NUMBER(12,2),
    DISPATCH_DATE     DATE,
    EXPECTED_DATE     DATE,
    ACTUAL_DATE       DATE,
    STATUS            VARCHAR(20)
);

-- 2. Clear old data
TRUNCATE TABLE SCM.RAW.SHIPMENT;
TRUNCATE TABLE SCM.RAW.ORDER_;
TRUNCATE TABLE SCM.RAW.PLANT_PART_BOM;
TRUNCATE TABLE SCM.RAW.CUSTOMER;
TRUNCATE TABLE SCM.RAW.PLANT;
TRUNCATE TABLE SCM.RAW.PART;
TRUNCATE TABLE SCM.RAW.CONTRACT;
TRUNCATE TABLE SCM.RAW.SUPPLIER;
TRUNCATE TABLE SCM.ONT.SUPPLIER_CLOSURE;
TRUNCATE TABLE SCM.ONT.DETECTED_RISK_ALERTS;

-- 3. Seed 20 Suppliers (8 Tier-1, 7 Tier-2, 5 Tier-3)
INSERT INTO SCM.RAW.SUPPLIER (SUPPLIER_ID, SUPPLIER_NAME, PARENT_SUPPLIER_ID, REGION, SOURCE_TYPE, SOURCE_LAST_UPDATED) VALUES
('SUP-001', 'Apex Components', NULL, 'North America', 'TRADE_DATA_VERIFIED', CURRENT_DATE()),
('SUP-002', 'Global Tech Parts', NULL, 'Asia-Pacific', 'TRADE_DATA_VERIFIED', CURRENT_DATE()),
('SUP-003', 'Nordic Logistics & Hardware', NULL, 'Europe', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 10),
('SUP-004', 'Pacific rim Electronics', NULL, 'Asia-Pacific', 'SELF_DISCLOSED', CURRENT_DATE() - 40),
('SUP-005', 'Atlantic Foundry Corp', NULL, 'North America', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 5),
('SUP-006', 'Precision Motion Systems', NULL, 'Europe', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 12),
('SUP-007', 'Titanium Alloys Ltd', NULL, 'North America', 'SELF_DISCLOSED', CURRENT_DATE() - 100),
('SUP-008', 'Vanguard Sensing Solutions', NULL, 'Asia-Pacific', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 2),

('SUP-101', 'Sub-Tier Silicon Co', 'SUP-001', 'Asia-Pacific', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 30),
('SUP-102', 'MicroLogix Chips', 'SUP-001', 'Europe', 'SELF_DISCLOSED', CURRENT_DATE() - 200),
('SUP-103', 'Optics & Photonics Fab', 'SUP-002', 'Asia-Pacific', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 15),
('SUP-104', 'Solder & Chemical Works', 'SUP-003', 'Europe', 'SELF_DISCLOSED', CURRENT_DATE() - 600),
('SUP-105', 'Kobe Stamping Tech', 'SUP-005', 'Asia-Pacific', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 25),
('SUP-106', 'AeroHydraulics Gasket Co', 'SUP-006', 'Europe', 'THIRD_PARTY_INTEL', CURRENT_DATE() - 90),
('SUP-107', 'Unmapped Subcontractor X', 'SUP-004', 'Asia-Pacific', 'UNKNOWN', CURRENT_DATE() - 365),

('SUP-201', 'Raw Quartz Mining', 'SUP-101', 'South America', 'THIRD_PARTY_INTEL', CURRENT_DATE() - 60),
('SUP-202', 'Global Copper Smelting', 'SUP-102', 'Africa', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 10),
('SUP-203', 'Rare Earth Refining SA', 'SUP-103', 'Asia-Pacific', 'TRADE_DATA_VERIFIED', CURRENT_DATE() - 45),
('SUP-204', 'Polymer Resin Base Inc', 'SUP-104', 'North America', 'SELF_DISCLOSED', CURRENT_DATE() - 180),
('SUP-205', 'Unknown Upstream Mining', 'SUP-107', 'Asia-Pacific', 'UNKNOWN', CURRENT_DATE() - 400);

-- 4. Seed 8 Contracts
INSERT INTO SCM.RAW.CONTRACT (CONTRACT_ID, SUPPLIER_ID, PENALTY_CLAUSE_TEXT, PENALTY_PCT, SLA_DAYS) VALUES
('CT-001', 'SUP-001', 'Late delivery beyond 5 days incurs a 10% penalty on total order value.', 10.00, 5),
('CT-002', 'SUP-002', 'Late delivery beyond 3 days incurs a 5% penalty clause.', 5.00, 3),
('CT-003', 'SUP-003', 'Standard SLA delivery within 7 days. Penalty rate set at 2.5% per week delayed.', 2.50, 7),
('CT-004', 'SUP-004', 'Vendor guarantee on component dispatch. Delay beyond SLA incurs 8% penalty.', 8.00, 4),
('CT-005', 'SUP-005', 'Structural castings agreement. SLA is 10 days with a 12% breach penalty clause.', 12.00, 10),
('CT-006', 'SUP-006', 'Precision actuator supply SLA 5 days, 4% delay penalty clause.', 4.00, 5),
('CT-007', 'SUP-007', 'Raw alloy sheet supply SLA 14 days, no monetary penalty enforced.', 0.00, 14),
('CT-008', 'SUP-008', 'Sensor array agreement SLA 3 days, 15% liquidated damages clause.', 15.00, 3);

-- 5. Seed 25 Parts
INSERT INTO SCM.RAW.PART (PART_ID, PART_NAME, SUPPLIER_ID, UNIT_COST) VALUES
('PRT-A1', 'Microcontroller Unit A1', 'SUP-001', 45.00),
('PRT-A2', 'Power Regulator Board', 'SUP-001', 30.00),
('PRT-A3', 'FPGA Processing Chip', 'SUP-001', 110.00),
('PRT-B1', 'Power Converter Module', 'SUP-002', 120.00),
('PRT-B2', 'Optical Transceiver Assembly', 'SUP-002', 210.00),
('PRT-B3', 'Display Driver IC', 'SUP-002', 18.50),
('PRT-C1', 'Stainless Fastener Set', 'SUP-003', 5.00),
('PRT-C2', 'Aluminum Chassis Enclosure', 'SUP-003', 85.00),
('PRT-D1', 'Capacitor Array Module', 'SUP-004', 12.00),
('PRT-D2', 'RF Receiver Module', 'SUP-004', 65.00),
('PRT-E1', 'Heavy Duty Casting Frame', 'SUP-005', 450.00),
('PRT-E2', 'Forged Steel Hub', 'SUP-005', 310.00),
('PRT-F1', 'Servo Motor Controller', 'SUP-006', 175.00),
('PRT-F2', 'Linear Actuator Shaft', 'SUP-006', 95.00),
('PRT-G1', 'Titanium Plate Grade 5', 'SUP-007', 520.00),
('PRT-H1', 'LIDAR Distance Sensor', 'SUP-008', 340.00),
('PRT-H2', 'CMOS Imaging Sensor', 'SUP-008', 190.00),
('PRT-H3', 'Ultrasonic Transducer', 'SUP-008', 42.00),
('PRT-C3', 'Thermal Interface Pad', 'SUP-003', 8.00),
('PRT-D3', 'Flex PCB Connector', 'SUP-004', 14.00),
('PRT-E3', 'Hydraulic Fitting Ring', 'SUP-005', 22.00),
('PRT-F3', 'Precision Ball Bearing Unit', 'SUP-006', 68.00),
('PRT-G2', 'Structural Rail Extrusion', 'SUP-007', 180.00),
('PRT-A4', 'Voltage Regulator IC', 'SUP-001', 9.50),
('PRT-B4', 'Signal Isolation Transformer', 'SUP-002', 34.00);

-- 6. Seed 3 Assembly Plants
INSERT INTO SCM.RAW.PLANT (PLANT_ID, PLANT_NAME, REGION) VALUES
('PLT-01', 'Austin Assembly Plant', 'Texas, USA'),
('PLT-02', 'Munich Tech Works', 'Germany'),
('PLT-03', 'Yokohama Advanced Robotics Plant', 'Japan');

-- 7. Seed Plant BOM Mapping
INSERT INTO SCM.RAW.PLANT_PART_BOM (PLANT_ID, PART_ID, QTY_PER_UNIT)
SELECT 'PLT-01', PART_ID, 2.0 FROM SCM.RAW.PART WHERE PART_ID IN ('PRT-A1', 'PRT-A2', 'PRT-A3', 'PRT-B1', 'PRT-C1', 'PRT-C2', 'PRT-D1', 'PRT-E1', 'PRT-F1', 'PRT-H1');

INSERT INTO SCM.RAW.PLANT_PART_BOM (PLANT_ID, PART_ID, QTY_PER_UNIT)
SELECT 'PLT-02', PART_ID, 1.0 FROM SCM.RAW.PART WHERE PART_ID IN ('PRT-B2', 'PRT-B3', 'PRT-C3', 'PRT-D2', 'PRT-E2', 'PRT-F2', 'PRT-G1', 'PRT-H2', 'PRT-A4', 'PRT-B4');

INSERT INTO SCM.RAW.PLANT_PART_BOM (PLANT_ID, PART_ID, QTY_PER_UNIT)
SELECT 'PLT-03', PART_ID, 3.0 FROM SCM.RAW.PART WHERE PART_ID IN ('PRT-D3', 'PRT-E3', 'PRT-F3', 'PRT-G2', 'PRT-H3', 'PRT-A1', 'PRT-B1', 'PRT-C1', 'PRT-E1', 'PRT-H1');

-- 8. Seed 12 Customers
INSERT INTO SCM.RAW.CUSTOMER (CUSTOMER_ID, CUSTOMER_NAME, REGION) VALUES
('CUST-801', 'Tesla Motors', 'North America'),
('CUST-802', 'Siemens AG', 'Europe'),
('CUST-803', 'Toyota Industry Corp', 'Asia-Pacific'),
('CUST-804', 'Apple Inc', 'North America'),
('CUST-805', 'Bosch Automation', 'Europe'),
('CUST-806', 'Lockheed Martin', 'North America'),
('CUST-807', 'Sony Corp', 'Asia-Pacific'),
('CUST-808', 'General Electric', 'North America'),
('CUST-809', 'ABB Robotics', 'Europe'),
('CUST-810', 'Samsung Electronics', 'Asia-Pacific'),
('CUST-811', 'Ford Motor Co', 'North America'),
('CUST-812', 'Schneider Electric', 'Europe');

-- 9. Seed 100 Orders
INSERT INTO SCM.RAW.ORDER_ (ORDER_ID, CUSTOMER_ID, PLANT_ID, ORDER_DATE, PROMISED_DATE, QTY_ORDERED, QTY_FULFILLED, STATUS)
SELECT 
    CONCAT('ORD-', 9000 + SEQ4()),
    CONCAT('CUST-8', LPAD(MOD(SEQ4(), 12) + 1, 0, '2')),
    CASE MOD(SEQ4(), 3) WHEN 0 THEN 'PLT-01' WHEN 1 THEN 'PLT-02' ELSE 'PLT-03' END,
    CURRENT_DATE() - UNIFORM(1, 30, RANDOM()),
    CURRENT_DATE() + UNIFORM(2, 20, RANDOM()),
    UNIFORM(100, 1000, RANDOM()),
    0,
    CASE WHEN MOD(SEQ4(), 7) = 0 THEN 'AT_RISK' ELSE 'OPEN' END
FROM TABLE(GENERATOR(ROWCOUNT => 100));

-- 10. Seed Delayed Inbound Shipments
INSERT INTO SCM.RAW.SHIPMENT (SHIPMENT_ID, ORIGIN_ID, DESTINATION_ID, LEG_TYPE, PART_ID, ORDER_ID, ROUTE_ID, QTY_SHIPPED, DISPATCH_DATE, EXPECTED_DATE, ACTUAL_DATE, STATUS)
VALUES
('SHP-501', 'SUP-001', 'PLT-01', 'INBOUND', 'PRT-A1', 'ORD-9000', 'RT-10', 1000, CURRENT_DATE() - 8, CURRENT_DATE() - 2, NULL, 'DELAYED'),
('SHP-502', 'SUP-002', 'PLT-02', 'INBOUND', 'PRT-B2', 'ORD-9001', 'RT-12', 200, CURRENT_DATE() - 3, CURRENT_DATE() + 2, NULL, 'DELAYED'),
('SHP-503', 'SUP-005', 'PLT-01', 'INBOUND', 'PRT-E1', 'ORD-9003', 'RT-15', 150, CURRENT_DATE() - 10, CURRENT_DATE() - 4, NULL, 'DELAYED'),
('SHP-504', 'SUP-008', 'PLT-03', 'INBOUND', 'PRT-H1', 'ORD-9005', 'RT-18', 500, CURRENT_DATE() - 5, CURRENT_DATE() - 1, NULL, 'DELAYED');

-- 11. Seed Baseline Delivered Shipments
INSERT INTO SCM.RAW.SHIPMENT (SHIPMENT_ID, ORIGIN_ID, DESTINATION_ID, LEG_TYPE, PART_ID, ORDER_ID, ROUTE_ID, QTY_SHIPPED, DISPATCH_DATE, EXPECTED_DATE, ACTUAL_DATE, STATUS)
SELECT 
    CONCAT('SHP-', 600 + SEQ4()),
    CONCAT('SUP-00', LPAD(MOD(SEQ4(), 8) + 1, 0, '1')),
    CASE MOD(SEQ4(), 3) WHEN 0 THEN 'PLT-01' WHEN 1 THEN 'PLT-02' ELSE 'PLT-03' END,
    'INBOUND',
    CONCAT('PRT-A', LPAD(MOD(SEQ4(), 3) + 1, 0, '1')),
    CONCAT('ORD-', 9000 + MOD(SEQ4(), 100)),
    CONCAT('RT-', LPAD(MOD(SEQ4(), 8) + 1, 0, '2')),
    UNIFORM(200, 2000, RANDOM()),
    CURRENT_DATE() - UNIFORM(5, 15, RANDOM()),
    CURRENT_DATE() + UNIFORM(1, 10, RANDOM()),
    CURRENT_DATE() + UNIFORM(1, 10, RANDOM()),
    'DELIVERED'
FROM TABLE(GENERATOR(ROWCOUNT => 146));

-- 12. Re-build Supplier Closure Table
TRUNCATE TABLE SCM.ONT.SUPPLIER_CLOSURE;

INSERT INTO SCM.ONT.SUPPLIER_CLOSURE (DESCENDANT, ANCESTOR, TIER_DEPTH, PATH_CONFIDENCE)
WITH RECURSIVE CHAIN (DESCENDANT, ANCESTOR, TIER_DEPTH, PATH_CONFIDENCE) AS (
    SELECT
        SUPPLIER_ID AS DESCENDANT,
        SUPPLIER_ID AS ANCESTOR,
        0 AS TIER_DEPTH,
        1.0::FLOAT AS PATH_CONFIDENCE
    FROM SCM.RAW.SUPPLIER

    UNION ALL

    SELECT
        C.DESCENDANT,
        S.SUPPLIER_ID AS ANCESTOR,
        C.TIER_DEPTH + 1 AS TIER_DEPTH,
        (C.PATH_CONFIDENCE * COALESCE(VC.CONFIDENCE_SCORE, 0.80))::FLOAT AS PATH_CONFIDENCE
    FROM CHAIN C
    JOIN SCM.RAW.SUPPLIER S ON S.PARENT_SUPPLIER_ID = C.ANCESTOR
    LEFT JOIN SCM.ONT.V_SUPPLIER_CONFIDENCE VC ON VC.SUPPLIER_ID = S.SUPPLIER_ID
)
SELECT DESCENDANT, ANCESTOR, TIER_DEPTH, PATH_CONFIDENCE FROM CHAIN;

-- 13. Populate Automated Alerts Table
TRUNCATE TABLE SCM.ONT.DETECTED_RISK_ALERTS;

INSERT INTO SCM.ONT.DETECTED_RISK_ALERTS (
    ALERT_ID,
    SUPPLIER_ID,
    SEVERITY,
    RISK_TYPE,
    DESCRIPTION,
    DETECTED_AT
)
SELECT 
    UUID_STRING() AS ALERT_ID,
    ROOT_SUPPLIER_ID AS SUPPLIER_ID,
    CASE 
        WHEN ROW_RISK_SCORE >= 25 THEN 'CRITICAL'
        WHEN ROW_RISK_SCORE >= 15 THEN 'HIGH'
        ELSE 'MEDIUM'
    END AS SEVERITY,
    'SUPPLY_CASCADE' AS RISK_TYPE,
    CONCAT('Tier-', TIER_DEPTH, ' disruption: Supplier ', ROOT_SUPPLIER_NAME, ' threatens Order ', ORDER_ID, ' (Part: ', PART_NAME, ') in ', DAYS_TO_IMPACT, ' days.') AS DESCRIPTION,
    CURRENT_TIMESTAMP() AS DETECTED_AT
FROM SCM.ONT.SV_SUPPLY_CHAIN
WHERE ROW_RISK_SCORE > 10.0;
