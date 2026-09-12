# ChemTrack 校园实验室危化品全生命周期管理系统

课程作业的可运行 MVP，覆盖危化品档案、库存预警、领用申请、审批和审计展示。

## 技术栈

- 后端：Spring Boot 3.4、Java 17、JDBC、MySQL 8
- 前端：Vue 3、Vite、原生 CSS
- 工具：IntelliJ IDEA、DataGrip、Apifox、draw.io、Git

## 启动步骤

### 1. 初始化数据库

首次安装时，在 DataGrip 中打开 `database/schema.sql` 并执行。数据库账号默认是 `root`；密码必须通过环境变量提供。如果是从旧版 ChemTrack 升级，先备份 `chemtrack` 数据库，再执行 `database/upgrade-v2.sql`；该脚本保留原有档案和申请记录。

如果你的 MySQL 密码不同，在启动后端前设置环境变量：

```powershell
$env:CHEMTRACK_DB_PASSWORD="你的MySQL密码"
```

### 2. 启动后端

```powershell
cd D:\Software_Engineering\ChemTrack\backend
mvn spring-boot:run
```

后端地址：`http://localhost:8080`，健康检查：`http://localhost:8080/api/health`。

### 3. 启动前端

```powershell
cd D:\Software_Engineering\ChemTrack\frontend
npm install
npm run dev
```

浏览器访问：`http://localhost:5173`。

后端未启动时，前端会自动进入演示数据模式，方便课堂展示页面；后端启动后会自动切换为 MySQL 实时数据。

## 已实现的业务闭环

- 危化品批次档案：供应商、批次号、有效期、存放要求、二维码标识。
- 采购入库：申请、审批、采购中、待验收、入库状态推进。
- 领用审批：普通试剂单级审批，高风险试剂教师审批后必须管理员复核。
- 出库与使用：办理发放时事务扣减库存，自动建立使用记录。
- 归还登记：记录实际使用量、归还量和异常说明，归还量自动回补库存。
- 风险中心：库存不足、即将/已经过期预警，异常上报与处理闭环。
- 废弃处置：危废申请、暂存、转运、处理中、已处置全流程。
- 审计与报表：关键动作不可删除，提供汇总统计和角色演示切换。

课堂演示建议依次操作：采购入库 → 新建领用申请 → 教师审批 → 管理员复核 → 办理发放 → 查看使用记录 → 风险中心扫描 → 登记废弃处置 → 审计记录。

## API 速查

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 检查服务状态 |
| GET | `/api/dashboard` | 获取总览指标 |
| GET | `/api/chemicals?keyword=` | 查询危化品档案 |
| GET | `/api/requests` | 查询领用申请 |
| POST | `/api/requests` | 提交领用申请 |
| PATCH | `/api/requests/{id}/approve` | 批准申请 |
| PATCH | `/api/requests/{id}/reject` | 驳回申请 |
| PATCH | `/api/requests/{id}/issue` | 办理出库并建立使用记录 |
| GET | `/api/usages` | 查询使用归还记录 |
| PATCH | `/api/usages/{id}/return` | 登记实际使用量和归还量 |
| GET | `/api/procurements` | 查询采购入库流程 |
| GET | `/api/alerts` | 查询有效预警 |
| POST | `/api/alerts/refresh` | 扫描库存和有效期预警 |
| GET | `/api/incidents` | 查询异常上报 |
| GET | `/api/disposals` | 查询废弃处置 |
| GET | `/api/audit` | 查询审计日志 |
| GET | `/api/reports/summary` | 获取统计报表摘要 |

## 下一阶段建议

1. 增加 JWT 登录和角色权限。
2. 增加管理员新增、编辑、冻结危化品接口。
3. 增加批次表、使用记录表、处置记录表和审计日志表。
4. 用 draw.io 将 `docs/modeling.md` 中的模型转成课堂展示版图片。
