--CREATE DATABASE
/*
CREATE DATABASE MarineAI;
GO

USE MarineAI;
GO

--SHIP DETAILS
CREATE TABLE vessels(
	   vessel_id VARCHAR(20) PRIMARY KEY,
	   vessel_name VARCHAR(100),
	   ship_type VARCHAR(50)
);
--SENSOR DATA
CREATE TABLE vessel_metrics(
	   metric_id INT IDENTITY PRIMARY KEY,
	   vessel_id VARCHAR(20),
	   engineTemp FLOAT, --exhaust_temp_c
	   rpm FLOAT, 
	   fuelRate FLOAT,   --fuel_consumption_t_day
	   speed FLOAT,      --avg_speed_knots
	   vibration FLOAT,  
	   loadWeight FLOAT, --cargo_utilization_pct
	   timestamp DATETIME DEFAULT GETDATE(),
	   FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
);
--AKHAND OPTIMIZIED RESULT ************
CREATE TABLE fuel_predictions(
	   prediction_id INT IDENTITY PRIMARY KEY,
	   vessel_id VARCHAR(20),
	   currentRPM FLOAT,
	   recommendedRPM FLOAT,
	   estimatedSaving FLOAT,
	   confidence FLOAT,
	   created_at DATETIME DEFAULT GETDATE(),
	   FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
);
--RISK MANAGEMNET FROM ML ************
CREATE TABLE safety_predictions(
	   prediction_id INT IDENTITY PRIMARY KEY,
	   vessel_id VARCHAR(20),
	   riskScore INT,
	   riskLevel VARCHAR(10),
	   possibleCause VARCHAR(250),
	   created_at DATETIME DEFAULT GETDATE(),
	   FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
);
--ALERT VARIATIONS 
CREATE TABLE alert_types(
	   type_id INT IDENTITY PRIMARY KEY,
	   type_name VARCHAR(50)
);
--AVOID REPETATION
INSERT INTO alert_types 
VALUES ('vibrations'),
	   ('overheating'),
	   ('fuel spike');
--ALERTING
CREATE TABLE alerts(
	   alert_id INT IDENTITY PRIMARY KEY,
	   vessel_id VARCHAR(20),
	   type_id INT,
	   severity VARCHAR(10),
	   message VARCHAR(250),
	   time DATETIME DEFAULT GETDATE(),
	   FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id),
	   FOREIGN KEY (type_id) REFERENCES alert_types(type_id)
);
--APPLICATION LOGS
CREATE TABLE system_logs(
	   log_id INT IDENTITY PRIMARY KEY,
	   event VARCHAR(250),
	   level VARCHAR(10),
	   time DATETIME DEFAULT GETDATE()
);
--SYSTEM STATUS
CREATE TABLE system_status(
	   vessel_id VARCHAR(20) PRIMARY KEY,
	   systemHealth VARCHAR(20),
	   connectivity VARCHAR(20),
	   FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id)
);
--CONFIGURATION SETTINGS
CREATE TABLE settings(
	   setting_id INT IDENTITY PRIMARY KEY,
	   refreshInterval INT,
	   aiMode VARCHAR(50),
	   apiEndpoint VARCHAR(250),
	   update_at DATETIME DEFAULT GETDATE()
);

SELECT TOP 10 *
FROM master_dataset;

--SHIP DATA
INSERT INTO vessels(vessel_id, vessel_name, ship_type)
SELECT DISTINCT vessel_id, vessel_id, ship_type
FROM master_dataset;

--SENSOR DATA
INSERT INTO vessel_metrics (
	   vessel_id, engineTemp, rpm, fuelRate, speed, vibration, loadWeight )
SELECT
       vessel_id, exhaust_temp_c, rpm, fuel_consumption_t_day, avg_speed_knots,
	   0, cargo_utilization_pct
FROM master_dataset;

--ML PREDICTION
INSERT INTO fuel_predictions (vessel_id, currentRPM, recommendedRPM, estimatedSaving, confidence)
SELECT 
      vessel_id, rpm, rpm - 100, 5, 0.9
FROM master_dataset;

SELECT TOP 10 * FROM vessels;
SELECT TOP 10 * FROM vessel_metrics;
SELECT TOP 10 * FROM fuel_predictions;

DROP TABLE master_dataset;


--ALTER TABLE vessel_metrics ADD co2_emission FLOAT;
UPDATE vessel_metrics
SET co2_emission = fuelRate * 3.114;
--PREVENT NULL EMISSION
ALTER TABLE vessel_metrics
ADD CONSTRAINT df_co2 DEFAULT 0 FOR co2_emission;

SELECT TOP 10 vessel_id, fuelRate, co2_emission
FROM vessel_metrics;

SELECT COUNT(*) FROM vessels;
SELECT COUNT(*) FROM vessel_metrics;
SELECT COUNT(*) FROM fuel_predictions;
SELECT COUNT(*) FROM safety_predictions;
SELECT COUNT(*) FROM alerts;

--EMMISSION ANALYSIS

SELECT vessel_id,
       AVG(co2_emission) AS avg_co2,
       AVG(fuelRate) AS avg_fuel
FROM vessel_metrics
GROUP BY vessel_id;

--FOR DASHBOARD
SELECT TOP 5
vessel_id,
rpm,
fuelRate,
co2_emission,
engineTemp
FROM vessel_metrics
ORDER BY timestamp DESC;

--QUEING MULTIPLE TABLES
CREATE VIEW vessel_operational_view AS
SELECT
    v.vessel_id,
    v.ship_type,
    vm.engineTemp,
    vm.rpm,
    vm.fuelRate,
    vm.speed,
    vm.loadWeight,
    vm.co2_emission,
    vm.timestamp
FROM vessels v
JOIN vessel_metrics vm
ON v.vessel_id = vm.vessel_id;

INSERT INTO alerts (vessel_id, type_id, severity, message)
VALUES
('IMO9000000', 1, 'HIGH', 'Excessive vibrations detected in engine room'),
('IMO9000001', 2, 'MEDIUM', 'Engine overheating beyond safe threshold'),
('IMO9000002', 3, 'LOW', 'Fuel consumption spike observed during cruise'),
('IMO9000003', 1, 'MEDIUM', 'Hull vibrations above normal during storm'),
('IMO9000004', 2, 'HIGH', 'Critical overheating in auxiliary engine'),
('IMO9000005', 3, 'MEDIUM', 'Unexpected fuel spike during docking'),
('IMO9000006', 1, 'LOW', 'Minor vibration anomaly logged'),
('IMO9000007', 2, 'HIGH', 'Main engine temperature exceeded 95°C'),
('IMO9000008', 3, 'HIGH', 'Fuel consumption doubled compared to baseline'),
('IMO9000009', 1, 'MEDIUM', 'Persistent vibration detected in propeller shaft');

INSERT INTO system_logs (event, level)
VALUES
('Data ingestion from master_dataset completed', 'INFO'),
('Fuel prediction model executed successfully', 'INFO'),
('Safety prediction flagged high risk for V002', 'WARN'),
('Database backup completed', 'INFO'),
('Connectivity issue detected for V003', 'ERROR'),
('Alert triggered for overheating on V005', 'WARN'),
('System health check completed for all vessels', 'INFO'),
('AI mode switched to predictive optimization', 'INFO'),
('Critical error in sensor feed for V008', 'ERROR'),
('Scheduled maintenance log updated for V010', 'INFO');

INSERT INTO system_status (vessel_id, systemHealth, connectivity)
VALUES
('IMO9000000', 'Healthy', 'Online'),
('IMO9000001', 'Degraded', 'Online'),
('IMO9000002', 'Critical', 'Offline'),
('IMO9000003', 'Healthy', 'Online'),
('IMO9000004', 'Critical', 'Online'),
('IMO9000005', 'Healthy', 'Online'),
('IMO9000006', 'Degraded', 'Offline'),
('IMO9000007', 'Critical', 'Offline'),
('IMO9000008', 'Healthy', 'Online'),
('IMO9000009', 'Degraded', 'Online');
*/