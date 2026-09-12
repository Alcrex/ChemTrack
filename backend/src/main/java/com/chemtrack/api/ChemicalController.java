package com.chemtrack.api;

import jakarta.validation.Valid;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class ChemicalController {
    private final JdbcTemplate jdbc;

    public ChemicalController(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @GetMapping("/health")
    public Map<String, Object> health() { return Map.of("status", "UP", "service", "chemtrack-backend", "version", "2.0"); }

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() {
        int total = count("SELECT COUNT(*) FROM chemicals");
        int low = count("SELECT COUNT(*) FROM chemicals WHERE quantity <= safe_threshold AND status = '可领用'");
        int expiring = count("SELECT COUNT(*) FROM chemicals WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) AND status NOT IN ('已处置')");
        int pending = count("SELECT COUNT(*) FROM requests WHERE status IN ('PENDING','TEACHER_APPROVED')");
        int incidents = count("SELECT COUNT(*) FROM incidents WHERE status <> '已关闭'");
        int activeAlerts = count("SELECT COUNT(*) FROM alerts WHERE status='ACTIVE'");
        int usage = count("SELECT COUNT(*) FROM usage_records WHERE status IN ('待使用','使用中','异常')");
        int disposal = count("SELECT COUNT(*) FROM disposals WHERE status <> '已处置'");
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("chemicalKinds", total); data.put("lowStock", low); data.put("expiringSoon", expiring);
        data.put("pendingRequests", pending); data.put("openIncidents", incidents); data.put("activeAlerts", activeAlerts);
        data.put("activeUsage", usage); data.put("pendingDisposals", disposal); return data;
    }

    @GetMapping("/chemicals")
    public List<Map<String, Object>> chemicals(@RequestParam(required = false) String keyword) {
        String q = keyword == null ? "" : keyword.trim();
        return jdbc.queryForList("""
                SELECT id, name, cas_no, batch_no, hazard_level, category, supplier, quantity, unit,
                       safe_threshold, max_allowed_stock, location, storage_requirement, safety_instructions,
                       received_at, expiry_date, qr_code, status
                FROM chemicals WHERE name LIKE ? OR cas_no LIKE ? OR category LIKE ? OR batch_no LIKE ?
                ORDER BY FIELD(hazard_level,'高','中','低'), expiry_date ASC
                """, "%" + q + "%", "%" + q + "%", "%" + q + "%", "%" + q + "%");
    }

    @PostMapping("/chemicals")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> createChemical(@Valid @RequestBody CreateChemical c) {
        jdbc.update("""
                INSERT INTO chemicals(name,cas_no,batch_no,hazard_level,category,supplier,quantity,unit,safe_threshold,max_allowed_stock,
                location,storage_requirement,safety_instructions,received_at,expiry_date,qr_code,status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'可领用')
                """, c.name(), c.casNo(), c.batchNo(), c.hazardLevel(), c.category(), c.supplier(), c.quantity(), c.unit(),
                c.safeThreshold(), c.maxAllowedStock(), c.location(), c.storageRequirement(), c.safetyInstructions(), c.receivedAt(), c.expiryDate(), c.qrCode());
        audit("实验室管理员", "LAB_ADMIN", "新增危化品档案", "CHEMICAL", null, c.name() + " / " + c.batchNo());
        return Map.of("message", "危化品档案已建立");
    }

    @GetMapping("/procurements")
    public List<Map<String, Object>> procurements() { return jdbc.queryForList("SELECT * FROM procurements ORDER BY requested_at DESC"); }

    @PostMapping("/procurements")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> createProcurement(@Valid @RequestBody CreateProcurement p) {
        jdbc.update("INSERT INTO procurements(chemical_name,cas_no,hazard_level,requested_by,quantity,unit,supplier,estimated_cost,reason) VALUES(?,?,?,?,?,?,?,?,?)",
                p.chemicalName(), p.casNo(), p.hazardLevel(), p.requestedBy(), p.quantity(), p.unit(), p.supplier(), p.estimatedCost(), p.reason());
        audit(p.requestedBy(), "LAB_ADMIN", "提交采购申请", "PROCUREMENT", null, p.chemicalName() + " " + p.quantity() + p.unit());
        return Map.of("message", "采购申请已提交");
    }

    @PatchMapping("/procurements/{id}/advance")
    public Map<String, Object> advanceProcurement(@PathVariable long id, @RequestParam String status,
                                                   @RequestParam(defaultValue = "实验室管理员") String operator,
                                                   @RequestParam(required = false) String note) {
        if (!List.of("待审批", "采购中", "待验收", "已入库", "已驳回").contains(status)) throw bad("非法采购状态");
        int changed = jdbc.update("UPDATE procurements SET status=?, approver=?, inspection_note=? WHERE id=?", status, operator, note, id);
        if (changed == 0) throw notFound("采购申请不存在");
        audit(operator, "LAB_ADMIN", "更新采购流程", "PROCUREMENT", id, "状态=" + status + (note == null ? "" : "; " + note));
        return Map.of("message", "采购流程已更新", "status", status);
    }

    @GetMapping("/requests")
    public List<Map<String, Object>> requests() {
        return jdbc.queryForList("""
                SELECT r.*, c.name AS chemical_name, c.batch_no, c.hazard_level, c.unit, c.quantity AS stock_quantity
                FROM requests r JOIN chemicals c ON c.id=r.chemical_id ORDER BY r.created_at DESC
                """);
    }

    @PostMapping("/requests")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> createRequest(@Valid @RequestBody CreateRequest request) {
        BigDecimal available = quantity(request.chemicalId());
        if (request.amount().compareTo(available) > 0) throw conflict("申请数量超过当前库存");
        jdbc.update("INSERT INTO requests(chemical_id,applicant,supervisor,experiment,purpose,amount) VALUES(?,?,?,?,?,?)",
                request.chemicalId(), request.applicant(), request.supervisor(), request.experiment(), request.purpose(), request.amount());
        audit(request.applicant(), "STUDENT", "提交领用申请", "REQUEST", null, request.experiment() + " / " + request.amount());
        return Map.of("message", "申请已提交，系统将按风险等级匹配审批流程");
    }

    @PatchMapping("/requests/{id}/approve")
    @Transactional
    public Map<String, Object> approve(@PathVariable long id, @RequestParam(defaultValue = "teacher") String stage,
                                       @RequestParam(defaultValue = "王老师") String approver,
                                       @RequestParam(required = false) String comment) {
        Map<String, Object> request = request(id);
        String current = String.valueOf(request.get("status"));
        String hazard = String.valueOf(request.get("hazard_level"));
        String next;
        String stageName;
        if ("admin".equalsIgnoreCase(stage)) {
            if (!"TEACHER_APPROVED".equals(current)) throw conflict("该申请尚未完成指导教师审批");
            next = "APPROVED"; stageName = "管理员复核";
            jdbc.update("UPDATE requests SET status='APPROVED', admin_approver=?, admin_approved_at=NOW(), approver=?, approved_at=NOW() WHERE id=?", approver, approver, id);
        } else {
            if (!"PENDING".equals(current)) throw conflict("申请已处理或正在等待管理员复核");
            next = "高".equals(hazard) ? "TEACHER_APPROVED" : "APPROVED"; stageName = "指导教师审批";
            jdbc.update("UPDATE requests SET status=?, teacher_approver=?, teacher_approved_at=NOW(), approver=?, approved_at=NOW() WHERE id=?", next, approver, approver, id);
        }
        jdbc.update("INSERT INTO approval_records(request_id,stage,decision,approver,comment) VALUES(?,?,?,?,?)", id, stageName, "批准", approver, comment);
        audit(approver, "admin".equalsIgnoreCase(stage) ? "LAB_ADMIN" : "TEACHER", "批准领用申请", "REQUEST", id, stageName + "，下一状态=" + next);
        return Map.of("message", "审批已记录", "status", next, "nextStep", "高".equals(hazard) && "TEACHER_APPROVED".equals(next) ? "管理员复核" : "管理员发放");
    }

    @PatchMapping("/requests/{id}/reject")
    public Map<String, Object> reject(@PathVariable long id, @RequestParam(defaultValue = "王老师") String approver,
                                      @RequestParam(defaultValue = "不符合实验室安全要求") String comment) {
        int changed = jdbc.update("UPDATE requests SET status='REJECTED', approver=?, approved_at=NOW(), abnormal_note=? WHERE id=? AND status IN ('PENDING','TEACHER_APPROVED')", approver, comment, id);
        if (changed == 0) throw conflict("申请不存在或已处理");
        jdbc.update("INSERT INTO approval_records(request_id,stage,decision,approver,comment) VALUES(?,?,?,?,?)", id, "指导教师审批", "驳回", approver, comment);
        audit(approver, "TEACHER", "驳回领用申请", "REQUEST", id, comment); return Map.of("message", "申请已驳回");
    }

    @PatchMapping("/requests/{id}/issue")
    @Transactional
    public Map<String, Object> issue(@PathVariable long id, @RequestParam(required = false) BigDecimal amount,
                                     @RequestParam(defaultValue = "实验室管理员") String operator) {
        Map<String, Object> r = request(id); if (!"APPROVED".equals(String.valueOf(r.get("status")))) throw conflict("只有已批准申请才能发放");
        BigDecimal issued = amount == null ? (BigDecimal) r.get("amount") : amount;
        if (issued.signum() <= 0) throw bad("发放数量必须大于 0");
        BigDecimal stock = quantity((Long) r.get("chemical_id")); if (issued.compareTo(stock) > 0) throw conflict("发放数量超过实时库存");
        int changed = jdbc.update("UPDATE chemicals SET quantity=quantity-? WHERE id=? AND quantity>=?", issued, r.get("chemical_id"), issued);
        if (changed == 0) throw conflict("库存不足，发放失败");
        jdbc.update("UPDATE requests SET status='ISSUED', issued_amount=?, issued_at=NOW() WHERE id=?", issued, id);
        jdbc.update("INSERT INTO usage_records(request_id,chemical_id,user_name,experiment,issued_amount,status,started_at) VALUES(?,?,?,?,?,'待使用',NOW())", id, r.get("chemical_id"), r.get("applicant"), r.get("experiment"), issued);
        audit(operator, "LAB_ADMIN", "发放危化品", "REQUEST", id, "发放 " + issued); return Map.of("message", "已完成出库，使用记录已建立");
    }

    @GetMapping("/usages")
    public List<Map<String, Object>> usages() { return jdbc.queryForList("SELECT u.*, c.name AS chemical_name, c.batch_no FROM usage_records u JOIN chemicals c ON c.id=u.chemical_id ORDER BY u.started_at DESC"); }

    @PatchMapping("/usages/{id}/return")
    @Transactional
    public Map<String, Object> returnUsage(@PathVariable long id, @RequestBody ReturnUsage body) {
        Map<String, Object> u = usage(id); BigDecimal issued = (BigDecimal) u.get("issued_amount");
        if (body.actualUsed().add(body.returnedAmount()).compareTo(issued) > 0) throw conflict("实际使用量与归还量之和不能超过发放量");
        jdbc.update("UPDATE usage_records SET actual_used=?, returned_amount=?, status=?, returned_at=NOW(), abnormal_note=? WHERE id=?",
                body.actualUsed(), body.returnedAmount(), body.abnormalNote() == null || body.abnormalNote().isBlank() ? "已归还" : "异常", body.abnormalNote(), id);
        jdbc.update("UPDATE requests SET status=?, actual_used=?, returned_amount=?, returned_at=NOW(), abnormal_note=?, closed_at=NOW() WHERE id=?",
                body.abnormalNote() == null || body.abnormalNote().isBlank() ? "RETURNED" : "ABNORMAL", body.actualUsed(), body.returnedAmount(), body.abnormalNote(), u.get("request_id"));
        if (body.returnedAmount().signum() > 0) jdbc.update("UPDATE chemicals SET quantity=quantity+? WHERE id=?", body.returnedAmount(), u.get("chemical_id"));
        audit(body.operator(), "STUDENT", "登记使用归还", "USAGE", id, "使用=" + body.actualUsed() + "; 归还=" + body.returnedAmount());
        return Map.of("message", "使用与归还记录已保存");
    }

    @GetMapping("/alerts")
    public List<Map<String, Object>> alerts(@RequestParam(defaultValue = "ACTIVE") String status) { return jdbc.queryForList("SELECT a.*, c.name AS chemical_name, c.batch_no FROM alerts a LEFT JOIN chemicals c ON c.id=a.chemical_id WHERE a.status=? ORDER BY FIELD(a.level,'严重','警告','提示'), a.created_at DESC", status); }

    @PostMapping("/alerts/refresh")
    @Transactional
    public Map<String, Object> refreshAlerts() {
        int created = 0; List<Map<String, Object>> rows = jdbc.queryForList("SELECT id,name,quantity,unit,safe_threshold,expiry_date FROM chemicals WHERE status <> '已处置'");
        for (Map<String, Object> c : rows) {
            long id = ((Number)c.get("id")).longValue();
            if (((BigDecimal)c.get("quantity")).compareTo((BigDecimal)c.get("safe_threshold")) <= 0) created += addAlert(id, "库存不足", "严重", c.get("name") + "库存低于安全线", "当前库存 " + c.get("quantity") + c.get("unit") + "，安全线为 " + c.get("safe_threshold") + c.get("unit"));
            LocalDate expiry = ((java.sql.Date)c.get("expiry_date")).toLocalDate(); long days = java.time.temporal.ChronoUnit.DAYS.between(LocalDate.now(), expiry);
            if (days < 0) created += addAlert(id, "已经过期", "严重", c.get("name") + "已过期", "有效期为 " + expiry + "，请立即冻结并安排处置");
            else if (days <= 30) created += addAlert(id, "即将过期", "警告", c.get("name") + "将在 30 天内到期", "有效期为 " + expiry + "，剩余 " + days + " 天");
        }
        return Map.of("message", "预警扫描完成", "created", created);
    }

    @PatchMapping("/alerts/{id}/resolve")
    public Map<String, Object> resolveAlert(@PathVariable long id, @RequestParam(defaultValue = "实验室管理员") String operator) {
        int changed = jdbc.update("UPDATE alerts SET status='RESOLVED', resolved_at=NOW(), resolved_by=? WHERE id=? AND status='ACTIVE'", operator, id);
        if (changed == 0) throw conflict("预警不存在或已处理"); audit(operator, "LAB_ADMIN", "关闭库存预警", "ALERT", id, "人工确认已处理"); return Map.of("message", "预警已关闭");
    }

    @GetMapping("/incidents")
    public List<Map<String, Object>> incidents() { return jdbc.queryForList("SELECT i.*, c.name AS chemical_name FROM incidents i LEFT JOIN chemicals c ON c.id=i.chemical_id ORDER BY i.reported_at DESC"); }

    @PostMapping("/incidents")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> createIncident(@Valid @RequestBody CreateIncident i) {
        jdbc.update("INSERT INTO incidents(chemical_id,reporter,incident_type,severity,description,location) VALUES(?,?,?,?,?,?)", i.chemicalId(), i.reporter(), i.incidentType(), i.severity(), i.description(), i.location());
        audit(i.reporter(), "STUDENT", "上报实验室异常", "INCIDENT", null, i.description()); return Map.of("message", "异常已上报，安全负责人将收到提醒");
    }

    @PatchMapping("/incidents/{id}/handle")
    public Map<String, Object> handleIncident(@PathVariable long id, @RequestParam(defaultValue = "处理中") String status,
                                               @RequestParam(defaultValue = "安全负责人") String handler, @RequestParam(defaultValue = "") String note) {
        int changed = jdbc.update("UPDATE incidents SET status=?, handler=?, handling_note=?, handled_at=CASE WHEN ?='已关闭' THEN NOW() ELSE handled_at END WHERE id=?", status, handler, note, status, id);
        if (changed == 0) throw notFound("异常记录不存在"); audit(handler, "SAFETY_OFFICER", "处理实验室异常", "INCIDENT", id, status + " / " + note); return Map.of("message", "异常状态已更新");
    }

    @GetMapping("/disposals")
    public List<Map<String, Object>> disposals() { return jdbc.queryForList("SELECT d.*, c.name AS chemical_name, c.batch_no FROM disposals d JOIN chemicals c ON c.id=d.chemical_id ORDER BY d.requested_at DESC"); }

    @PostMapping("/disposals")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> createDisposal(@Valid @RequestBody CreateDisposal d) {
        if (d.amount().signum() <= 0) throw bad("处置数量必须大于 0");
        jdbc.update("INSERT INTO disposals(chemical_id,source,amount,unit,waste_type,temporary_location,disposal_company,applicant) VALUES(?,?,?,?,?,?,?,?)", d.chemicalId(), d.source(), d.amount(), d.unit(), d.wasteType(), d.temporaryLocation(), d.disposalCompany(), d.applicant());
        audit(d.applicant(), "LAB_ADMIN", "提交废弃物处置申请", "DISPOSAL", null, d.wasteType() + " " + d.amount()); return Map.of("message", "处置申请已登记");
    }

    @PatchMapping("/disposals/{id}/advance")
    public Map<String, Object> advanceDisposal(@PathVariable long id, @RequestParam String status,
                                                @RequestParam(defaultValue = "安全负责人") String operator, @RequestParam(required = false) String certificateNo) {
        int changed = jdbc.update("UPDATE disposals SET status=?, certificate_no=?, completed_at=CASE WHEN ?='已处置' THEN NOW() ELSE completed_at END WHERE id=?", status, certificateNo, status, id);
        if (changed == 0) throw notFound("处置记录不存在"); audit(operator, "SAFETY_OFFICER", "更新废弃物处置流程", "DISPOSAL", id, status); return Map.of("message", "处置流程已更新");
    }

    @GetMapping("/audit")
    public List<Map<String, Object>> audit() { return jdbc.queryForList("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 200"); }

    @GetMapping("/users")
    public List<Map<String, Object>> users() { return jdbc.queryForList("SELECT id,username,display_name,role,department,active FROM users WHERE active=TRUE ORDER BY role,display_name"); }

    @GetMapping("/reports/summary")
    public Map<String, Object> reportSummary() {
        Map<String, Object> result = new LinkedHashMap<>(dashboard());
        result.put("totalStock", jdbc.queryForObject("SELECT COALESCE(SUM(quantity),0) FROM chemicals", BigDecimal.class));
        result.put("totalIssued", jdbc.queryForObject("SELECT COALESCE(SUM(issued_amount),0) FROM usage_records", BigDecimal.class));
        result.put("totalDisposed", jdbc.queryForObject("SELECT COALESCE(SUM(amount),0) FROM disposals WHERE status='已处置'", BigDecimal.class));
        result.put("incidentClosedRate", jdbc.queryForObject("SELECT COALESCE(ROUND(SUM(status='已关闭')/COUNT(*)*100,1),0) FROM incidents", BigDecimal.class)); return result;
    }

    private int count(String sql) { Integer n = jdbc.queryForObject(sql, Integer.class); return n == null ? 0 : n; }
    private BigDecimal quantity(long id) { BigDecimal n = jdbc.queryForObject("SELECT quantity FROM chemicals WHERE id=?", BigDecimal.class, id); if (n == null) throw notFound("危化品不存在"); return n; }
    private Map<String, Object> request(long id) { try { return jdbc.queryForMap("SELECT r.*, c.name AS chemical_name, c.hazard_level, c.unit, c.quantity AS stock_quantity FROM requests r JOIN chemicals c ON c.id=r.chemical_id WHERE r.id=?", id); } catch (Exception e) { throw notFound("领用申请不存在"); } }
    private Map<String, Object> usage(long id) { try { return jdbc.queryForMap("SELECT * FROM usage_records WHERE id=?", id); } catch (Exception e) { throw notFound("使用记录不存在"); } }
    private int addAlert(long chemicalId, String type, String level, String title, String content) { Integer n=jdbc.queryForObject("SELECT COUNT(*) FROM alerts WHERE chemical_id=? AND alert_type=? AND status='ACTIVE'", Integer.class, chemicalId, type); if (n != null && n > 0) return 0; jdbc.update("INSERT INTO alerts(chemical_id,alert_type,level,title,content) VALUES(?,?,?,?,?)", chemicalId,type,level,title,content); return 1; }
    private void audit(String name, String role, String action, String type, Long id, String detail) { jdbc.update("INSERT INTO audit_logs(operator_name,operator_role,action,target_type,target_id,detail) VALUES(?,?,?,?,?,?)", name,role,action,type,id,detail); }
    private ResponseStatusException bad(String s) { return new ResponseStatusException(HttpStatus.BAD_REQUEST, s); }
    private ResponseStatusException notFound(String s) { return new ResponseStatusException(HttpStatus.NOT_FOUND, s); }
    private ResponseStatusException conflict(String s) { return new ResponseStatusException(HttpStatus.CONFLICT, s); }

    public record CreateChemical(@NotBlank String name, @NotBlank String casNo, @NotBlank String batchNo, @NotBlank String hazardLevel, @NotBlank String category, @NotBlank String supplier, @NotNull @DecimalMin("0") BigDecimal quantity, @NotBlank String unit, @NotNull @DecimalMin("0") BigDecimal safeThreshold, BigDecimal maxAllowedStock, @NotBlank String location, String storageRequirement, String safetyInstructions, @NotNull LocalDate receivedAt, @NotNull LocalDate expiryDate, String qrCode) {}
    public record CreateProcurement(@NotBlank String chemicalName, String casNo, @NotBlank String hazardLevel, @NotBlank String requestedBy, @NotNull @DecimalMin("0.01") BigDecimal quantity, @NotBlank String unit, String supplier, BigDecimal estimatedCost, @NotBlank String reason) {}
    public record CreateRequest(@NotNull Long chemicalId, @NotBlank String applicant, String supervisor, @NotBlank String experiment, String purpose, @NotNull @DecimalMin("0.01") BigDecimal amount) {}
    public record ReturnUsage(@NotNull @DecimalMin("0") BigDecimal actualUsed, @NotNull @DecimalMin("0") BigDecimal returnedAmount, String abnormalNote, @NotBlank String operator) {}
    public record CreateIncident(Long chemicalId, @NotBlank String reporter, @NotBlank String incidentType, @NotBlank String severity, @NotBlank String description, String location) {}
    public record CreateDisposal(@NotNull Long chemicalId, @NotBlank String source, @NotNull @DecimalMin("0.01") BigDecimal amount, @NotBlank String unit, @NotBlank String wasteType, @NotBlank String temporaryLocation, String disposalCompany, @NotBlank String applicant) {}
}
