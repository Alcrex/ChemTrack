SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS chemtrack DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE chemtrack;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS approval_records;
DROP TABLE IF EXISTS usage_records;
DROP TABLE IF EXISTS disposals;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS procurements;
DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS chemicals;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(80) NOT NULL,
    role ENUM('STUDENT','TEACHER','LAB_ADMIN','SAFETY_OFFICER','SYSTEM_ADMIN') NOT NULL,
    department VARCHAR(100), active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chemicals (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL, cas_no VARCHAR(30) NOT NULL,
    batch_no VARCHAR(50) NOT NULL UNIQUE,
    hazard_level ENUM('高','中','低') NOT NULL, category VARCHAR(50) NOT NULL,
    supplier VARCHAR(120) NOT NULL, quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL DEFAULT 'g', safe_threshold DECIMAL(10,2) NOT NULL DEFAULT 0,
    max_allowed_stock DECIMAL(10,2), location VARCHAR(100) NOT NULL,
    storage_requirement VARCHAR(255), safety_instructions TEXT,
    received_at DATE NOT NULL, expiry_date DATE NOT NULL, qr_code VARCHAR(100),
    status ENUM('可领用','冻结','已过期','已领用','待处置','已处置') NOT NULL DEFAULT '可领用',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (quantity >= 0), INDEX idx_chemical_expiry (expiry_date), INDEX idx_chemical_status (status)
);

CREATE TABLE procurements (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_name VARCHAR(100) NOT NULL, cas_no VARCHAR(30),
    hazard_level ENUM('高','中','低') NOT NULL, requested_by VARCHAR(80) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL, unit VARCHAR(20) NOT NULL, supplier VARCHAR(120),
    estimated_cost DECIMAL(12,2) DEFAULT 0, reason VARCHAR(255) NOT NULL,
    status ENUM('待审批','采购中','待验收','已入库','已驳回') NOT NULL DEFAULT '待审批',
    approver VARCHAR(80), inspection_note VARCHAR(255),
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE requests (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_id BIGINT NOT NULL,
    applicant VARCHAR(80) NOT NULL, supervisor VARCHAR(80) NOT NULL DEFAULT '待指定',
    experiment VARCHAR(150) NOT NULL, purpose VARCHAR(255), amount DECIMAL(10,2) NOT NULL,
    status ENUM('PENDING','TEACHER_APPROVED','APPROVED','REJECTED','ISSUED','RETURNED','ABNORMAL') NOT NULL DEFAULT 'PENDING',
    approver VARCHAR(80), teacher_approver VARCHAR(80), teacher_approved_at TIMESTAMP NULL,
    admin_approver VARCHAR(80), admin_approved_at TIMESTAMP NULL, issued_amount DECIMAL(10,2),
    issued_at TIMESTAMP NULL, actual_used DECIMAL(10,2), returned_amount DECIMAL(10,2),
    returned_at TIMESTAMP NULL, abnormal_note VARCHAR(500), created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL, closed_at TIMESTAMP NULL,
    CONSTRAINT fk_requests_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id), INDEX idx_request_status (status)
);

CREATE TABLE approval_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, request_id BIGINT NOT NULL,
    stage ENUM('指导教师审批','管理员复核') NOT NULL, decision ENUM('批准','驳回') NOT NULL,
    approver VARCHAR(80) NOT NULL, comment VARCHAR(255), decided_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_approval_request FOREIGN KEY (request_id) REFERENCES requests(id)
);

CREATE TABLE usage_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, request_id BIGINT NOT NULL UNIQUE, chemical_id BIGINT NOT NULL,
    user_name VARCHAR(80) NOT NULL, experiment VARCHAR(150) NOT NULL, issued_amount DECIMAL(10,2) NOT NULL,
    actual_used DECIMAL(10,2), returned_amount DECIMAL(10,2), status ENUM('待使用','使用中','已归还','异常') NOT NULL DEFAULT '待使用',
    started_at TIMESTAMP NULL, returned_at TIMESTAMP NULL, abnormal_note VARCHAR(500),
    CONSTRAINT fk_usage_request FOREIGN KEY (request_id) REFERENCES requests(id), CONSTRAINT fk_usage_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id)
);

CREATE TABLE incidents (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_id BIGINT, reporter VARCHAR(80) NOT NULL,
    incident_type ENUM('泄漏','包装破损','存储异常','人员暴露','数量异常','其他') NOT NULL,
    severity ENUM('一般','较大','重大') NOT NULL, description VARCHAR(500) NOT NULL, location VARCHAR(100),
    status ENUM('待处理','处理中','已关闭') NOT NULL DEFAULT '待处理', handler VARCHAR(80), handling_note VARCHAR(500),
    reported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, handled_at TIMESTAMP NULL,
    CONSTRAINT fk_incident_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id)
);

CREATE TABLE disposals (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_id BIGINT NOT NULL, source VARCHAR(120) NOT NULL,
    amount DECIMAL(10,2) NOT NULL, unit VARCHAR(20) NOT NULL, waste_type VARCHAR(80) NOT NULL,
    temporary_location VARCHAR(100) NOT NULL, disposal_company VARCHAR(120),
    status ENUM('待申请','待转运','处理中','已处置') NOT NULL DEFAULT '待申请', applicant VARCHAR(80) NOT NULL,
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, completed_at TIMESTAMP NULL, certificate_no VARCHAR(100),
    CONSTRAINT fk_disposal_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id)
);

CREATE TABLE alerts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, chemical_id BIGINT, alert_type ENUM('库存不足','即将过期','已经过期','超量申请','长期未归还','频繁申请','存储异常','重大事件') NOT NULL,
    level ENUM('提示','警告','严重') NOT NULL, title VARCHAR(150) NOT NULL, content VARCHAR(500) NOT NULL,
    status ENUM('ACTIVE','RESOLVED') NOT NULL DEFAULT 'ACTIVE', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL, resolved_by VARCHAR(80), CONSTRAINT fk_alert_chemical FOREIGN KEY (chemical_id) REFERENCES chemicals(id), INDEX idx_alert_status (status)
);

CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT, operator_name VARCHAR(80) NOT NULL, operator_role VARCHAR(40) NOT NULL,
    action VARCHAR(120) NOT NULL, target_type VARCHAR(50) NOT NULL, target_id BIGINT, detail VARCHAR(500),
    result ENUM('SUCCESS','FAILURE') NOT NULL DEFAULT 'SUCCESS', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX idx_audit_created (created_at)
);

INSERT INTO users(username, display_name, role, department) VALUES
('student.zhang', '张同学', 'STUDENT', '材料学院'), ('teacher.wang', '王老师', 'TEACHER', '材料学院'),
('lab.admin', '实验室管理员', 'LAB_ADMIN', '实验中心'), ('safety.li', '李主任', 'SAFETY_OFFICER', '学院安全办公室'), ('sys.admin', '系统管理员', 'SYSTEM_ADMIN', '信息中心');

INSERT INTO chemicals(name, cas_no, batch_no, hazard_level, category, supplier, quantity, unit, safe_threshold, max_allowed_stock, location, storage_requirement, safety_instructions, received_at, expiry_date, qr_code, status) VALUES
('浓硫酸', '7664-93-9', 'CT-20260820-01', '高', '腐蚀品', '国药试剂', 820, 'mL', 300, 2000, 'A-01 防腐柜', '阴凉、通风，与碱类分开存放', '佩戴耐酸手套和护目镜，在通风橱内操作', '2026-08-20', '2027-06-30', 'CHEM-0001', '可领用'),
('无水乙醇', '64-17-5', 'CT-20260901-02', '中', '易燃液体', '阿拉丁试剂', 1250, 'mL', 500, 3000, 'B-02 易燃柜', '远离火种和热源，保持容器密闭', '禁止明火，保持良好通风', '2026-09-01', '2026-10-18', 'CHEM-0002', '可领用'),
('过氧化氢', '7722-84-1', 'CT-20260715-03', '高', '氧化剂', '麦克林试剂', 160, 'mL', 200, 1000, 'A-03 氧化剂柜', '避光、低温，与还原剂分开存放', '避免接触皮肤，使用洁净器具取用', '2026-07-15', '2026-10-02', 'CHEM-0003', '可领用'),
('硫酸铜', '7758-98-7', 'CT-20260512-04', '低', '一般化学品', '西陇科学', 2300, 'g', 500, 5000, 'C-04 普通试剂架', '干燥密封保存', '避免粉尘吸入，操作后洗手', '2026-05-12', '2028-01-12', 'CHEM-0004', '可领用');

INSERT INTO procurements(chemical_name, cas_no, hazard_level, requested_by, quantity, unit, supplier, estimated_cost, reason, status, approver, inspection_note) VALUES
('丙酮', '67-64-1', '中', '实验室管理员', 2000, 'mL', '国药试剂', 380, '下月有机化学实验教学使用', '采购中', '李主任', NULL),
('硝酸银', '7761-88-8', '高', '王老师', 500, 'g', '麦克林试剂', 860, '分析化学课程库存补充', '待验收', '李主任', '到货包装完整，待质量确认');

INSERT INTO requests(chemical_id, applicant, supervisor, experiment, purpose, amount, status, teacher_approver, teacher_approved_at, approver, approved_at) VALUES
(1, '张同学', '王老师', '材料腐蚀性测试', '测试不同材料耐酸性能', 50, 'PENDING', NULL, NULL, NULL, NULL),
(3, '李同学', '王老师', '氧化还原反应实验', '测定催化剂对反应速率的影响', 30, 'TEACHER_APPROVED', '王老师', NOW(), '王老师', NOW());
INSERT INTO approval_records(request_id, stage, decision, approver, comment) VALUES (2, '指导教师审批', '批准', '王老师', '实验方案和防护措施符合要求');
INSERT INTO alerts(chemical_id, alert_type, level, title, content) VALUES
(3, '库存不足', '严重', '过氧化氢库存低于安全线', '当前库存 160 mL，安全库存线为 200 mL，请安排补充。'),
(2, '即将过期', '警告', '无水乙醇即将在 30 天内到期', '批次 CT-20260901-02 将于 2026-10-18 到期，请优先使用或安排处置。');
INSERT INTO incidents(chemical_id, reporter, incident_type, severity, description, location, status) VALUES (2, '实验室管理员', '存储异常', '一般', '巡检时发现易燃柜温度短时偏高，已加强通风。', 'B-02 易燃柜', '处理中');
INSERT INTO disposals(chemical_id, source, amount, unit, waste_type, temporary_location, disposal_company, status, applicant) VALUES (1, '材料腐蚀性预实验', 20, 'mL', '酸性废液', '危废暂存间 W-01', '城市环保处置中心', '待转运', '实验室管理员');
INSERT INTO audit_logs(operator_name, operator_role, action, target_type, detail) VALUES
('系统', 'SYSTEM', '初始化演示数据', 'SYSTEM', '创建完整生命周期演示数据'), ('王老师', 'TEACHER', '批准领用申请', 'REQUEST', '过氧化氢 30 mL，等待管理员复核'), ('实验室管理员', 'LAB_ADMIN', '完成入库验收', 'CHEMICAL', '无水乙醇批次 CT-20260901-02');
