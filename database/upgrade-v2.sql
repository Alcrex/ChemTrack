-- 初版数据库升级脚本：保留现有 chemicals、requests 数据，并新增生命周期模块。
SET NAMES utf8mb4;
USE chemtrack;

ALTER TABLE chemicals ADD COLUMN batch_no VARCHAR(50) NULL AFTER cas_no;
ALTER TABLE chemicals ADD COLUMN supplier VARCHAR(120) NULL AFTER category;
ALTER TABLE chemicals ADD COLUMN max_allowed_stock DECIMAL(10,2) NULL AFTER safe_threshold;
ALTER TABLE chemicals ADD COLUMN storage_requirement VARCHAR(255) NULL AFTER location;
ALTER TABLE chemicals ADD COLUMN safety_instructions TEXT NULL AFTER storage_requirement;
ALTER TABLE chemicals ADD COLUMN received_at DATE NULL AFTER safety_instructions;
ALTER TABLE chemicals ADD COLUMN qr_code VARCHAR(100) NULL AFTER expiry_date;
UPDATE chemicals SET batch_no=CONCAT('LEGACY-',LPAD(id,4,'0')), supplier='待补录', received_at=CURDATE(), qr_code=CONCAT('CHEM-',LPAD(id,4,'0')) WHERE batch_no IS NULL;
ALTER TABLE chemicals MODIFY batch_no VARCHAR(50) NOT NULL, MODIFY supplier VARCHAR(120) NOT NULL, MODIFY received_at DATE NOT NULL;
ALTER TABLE chemicals ADD UNIQUE KEY uk_chemical_batch_no (batch_no);
ALTER TABLE chemicals MODIFY status ENUM('可领用','冻结','已过期','已领用','待处置','已处置') NOT NULL DEFAULT '可领用';

ALTER TABLE requests ADD COLUMN supervisor VARCHAR(80) NOT NULL DEFAULT '待指定' AFTER applicant;
ALTER TABLE requests ADD COLUMN purpose VARCHAR(255) NULL AFTER experiment;
ALTER TABLE requests ADD COLUMN teacher_approver VARCHAR(80) NULL AFTER approver;
ALTER TABLE requests ADD COLUMN teacher_approved_at TIMESTAMP NULL AFTER teacher_approver;
ALTER TABLE requests ADD COLUMN admin_approver VARCHAR(80) NULL AFTER teacher_approved_at;
ALTER TABLE requests ADD COLUMN admin_approved_at TIMESTAMP NULL AFTER admin_approver;
ALTER TABLE requests ADD COLUMN issued_amount DECIMAL(10,2) NULL AFTER admin_approved_at;
ALTER TABLE requests ADD COLUMN issued_at TIMESTAMP NULL AFTER issued_amount;
ALTER TABLE requests ADD COLUMN actual_used DECIMAL(10,2) NULL AFTER issued_at;
ALTER TABLE requests ADD COLUMN returned_amount DECIMAL(10,2) NULL AFTER actual_used;
ALTER TABLE requests ADD COLUMN returned_at TIMESTAMP NULL AFTER returned_amount;
ALTER TABLE requests ADD COLUMN abnormal_note VARCHAR(500) NULL AFTER returned_at;
ALTER TABLE requests ADD COLUMN closed_at TIMESTAMP NULL AFTER approved_at;
ALTER TABLE requests MODIFY status ENUM('PENDING','TEACHER_APPROVED','APPROVED','REJECTED','ISSUED','RETURNED','ABNORMAL') NOT NULL DEFAULT 'PENDING';

CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(50) NOT NULL UNIQUE, display_name VARCHAR(80) NOT NULL, role ENUM('STUDENT','TEACHER','LAB_ADMIN','SAFETY_OFFICER','SYSTEM_ADMIN') NOT NULL, department VARCHAR(100), active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS procurements (id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_name VARCHAR(100) NOT NULL, cas_no VARCHAR(30), hazard_level ENUM('高','中','低') NOT NULL, requested_by VARCHAR(80) NOT NULL, quantity DECIMAL(10,2) NOT NULL, unit VARCHAR(20) NOT NULL, supplier VARCHAR(120), estimated_cost DECIMAL(12,2) DEFAULT 0, reason VARCHAR(255) NOT NULL, status ENUM('待审批','采购中','待验收','已入库','已驳回') NOT NULL DEFAULT '待审批', approver VARCHAR(80), inspection_note VARCHAR(255), requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS approval_records (id BIGINT PRIMARY KEY AUTO_INCREMENT, request_id BIGINT NOT NULL, stage ENUM('指导教师审批','管理员复核') NOT NULL, decision ENUM('批准','驳回') NOT NULL, approver VARCHAR(80) NOT NULL, comment VARCHAR(255), decided_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT fk_approval_request FOREIGN KEY (request_id) REFERENCES requests(id));
CREATE TABLE IF NOT EXISTS usage_records (id BIGINT PRIMARY KEY AUTO_INCREMENT, request_id BIGINT NOT NULL UNIQUE, chemical_id BIGINT NOT NULL, user_name VARCHAR(80) NOT NULL, experiment VARCHAR(150) NOT NULL, issued_amount DECIMAL(10,2) NOT NULL, actual_used DECIMAL(10,2), returned_amount DECIMAL(10,2), status ENUM('待使用','使用中','已归还','异常') NOT NULL DEFAULT '待使用', started_at TIMESTAMP NULL, returned_at TIMESTAMP NULL, abnormal_note VARCHAR(500), CONSTRAINT fk_usage_request FOREIGN KEY (request_id) REFERENCES requests(id), CONSTRAINT fk_usage_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id));
CREATE TABLE IF NOT EXISTS incidents (id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_id BIGINT, reporter VARCHAR(80) NOT NULL, incident_type ENUM('泄漏','包装破损','存储异常','人员暴露','数量异常','其他') NOT NULL, severity ENUM('一般','较大','重大') NOT NULL, description VARCHAR(500) NOT NULL, location VARCHAR(100), status ENUM('待处理','处理中','已关闭') NOT NULL DEFAULT '待处理', handler VARCHAR(80), handling_note VARCHAR(500), reported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, handled_at TIMESTAMP NULL, CONSTRAINT fk_incident_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id));
CREATE TABLE IF NOT EXISTS disposals (id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_id BIGINT NOT NULL, source VARCHAR(120) NOT NULL, amount DECIMAL(10,2) NOT NULL, unit VARCHAR(20) NOT NULL, waste_type VARCHAR(80) NOT NULL, temporary_location VARCHAR(100) NOT NULL, disposal_company VARCHAR(120), status ENUM('待申请','待转运','处理中','已处置') NOT NULL DEFAULT '待申请', applicant VARCHAR(80) NOT NULL, requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, completed_at TIMESTAMP NULL, certificate_no VARCHAR(100), CONSTRAINT fk_disposal_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id));
CREATE TABLE IF NOT EXISTS alerts (id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_id BIGINT, alert_type ENUM('库存不足','即将过期','已经过期','超量申请','长期未归还','频繁申请','存储异常','重大事件') NOT NULL, level ENUM('提示','警告','严重') NOT NULL, title VARCHAR(150) NOT NULL, content VARCHAR(500) NOT NULL, status ENUM('ACTIVE','RESOLVED') NOT NULL DEFAULT 'ACTIVE', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, resolved_at TIMESTAMP NULL, resolved_by VARCHAR(80), CONSTRAINT fk_alert_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id));
CREATE TABLE IF NOT EXISTS audit_logs (id BIGINT PRIMARY KEY AUTO_INCREMENT, operator_name VARCHAR(80) NOT NULL, operator_role VARCHAR(40) NOT NULL, action VARCHAR(120) NOT NULL, target_type VARCHAR(50) NOT NULL, target_id BIGINT, detail VARCHAR(500), result ENUM('SUCCESS','FAILURE') NOT NULL DEFAULT 'SUCCESS', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);
INSERT IGNORE INTO users(username, display_name, role, department) VALUES ('student.zhang','张同学','STUDENT','材料学院'),('teacher.wang','王老师','TEACHER','材料学院'),('lab.admin','实验室管理员','LAB_ADMIN','实验中心'),('safety.li','李主任','SAFETY_OFFICER','学院安全办公室'),('sys.admin','系统管理员','SYSTEM_ADMIN','信息中心');
INSERT INTO audit_logs(operator_name, operator_role, action, target_type, detail) VALUES ('系统','SYSTEM','数据库升级至 V2','SYSTEM','新增采购、双重审批、使用归还、预警、异常、处置和审计模块');
INSERT INTO procurements(chemical_name,cas_no,hazard_level,requested_by,quantity,unit,supplier,estimated_cost,reason,status) SELECT '丙酮','67-64-1','中','实验室管理员',2000,'mL','国药试剂',380,'下月有机化学实验教学使用','采购中' WHERE NOT EXISTS (SELECT 1 FROM procurements);
INSERT INTO alerts(chemical_id,alert_type,level,title,content) SELECT 3,'库存不足','严重','过氧化氢库存低于安全线','当前库存低于安全线，请安排补充。' FROM chemicals WHERE id=3 AND NOT EXISTS (SELECT 1 FROM alerts);
INSERT INTO alerts(chemical_id,alert_type,level,title,content) SELECT 2,'即将过期','警告','无水乙醇即将在 30 天内到期','请优先使用或安排处置。' FROM chemicals WHERE id=2 AND NOT EXISTS (SELECT 1 FROM alerts WHERE alert_type='即将过期');
INSERT INTO incidents(chemical_id,reporter,incident_type,severity,description,location,status) SELECT 2,'实验室管理员','存储异常','一般','巡检时发现易燃柜温度短时偏高，已加强通风。','B-02 易燃柜','处理中' FROM chemicals WHERE id=2 AND NOT EXISTS (SELECT 1 FROM incidents);
INSERT INTO disposals(chemical_id,source,amount,unit,waste_type,temporary_location,disposal_company,status,applicant) SELECT 1,'材料腐蚀性预实验',20,'mL','酸性废液','危废暂存间 W-01','城市环保处置中心','待转运','实验室管理员' FROM chemicals WHERE id=1 AND NOT EXISTS (SELECT 1 FROM disposals);
