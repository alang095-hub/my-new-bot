# 生产环境部署检查清单

使用此清单确保生产环境部署的完整性和正确性。

## 部署前检查

### 0. 本地测试（强烈推荐）

- [ ] 运行部署前测试脚本
  ```bash
  # Windows
  scripts\test\pre_deployment_test.bat
  
  # Linux/Mac
  ./scripts/test/pre_deployment_test.sh
  ```
- [ ] 所有基础测试通过
- [ ] 多页面Token配置正确
- [ ] Webhook接收测试通过
- [ ] 自动回复功能测试通过
- [ ] 性能测试通过

**详细测试步骤：** 参考 [部署前本地测试指南](PRE_DEPLOYMENT_TESTING.md)

### 环境准备
- [ ] 服务器已准备（VPS/云服务器）
- [ ] 操作系统已更新
- [ ] Python 3.9+ 已安装
- [ ] PostgreSQL 12+ 已安装（或使用SQLite）
- [ ] Git 已安装
- [ ] 防火墙已配置（开放必要端口）

### 配置文件
- [ ] `.env` 文件已创建并配置所有必需的环境变量
  - [ ] `DATABASE_URL` - 数据库连接字符串
  - [ ] `FACEBOOK_APP_ID` - Facebook应用ID
  - [ ] `FACEBOOK_APP_SECRET` - Facebook应用密钥
  - [ ] `FACEBOOK_ACCESS_TOKEN` - Facebook访问令牌
  - [ ] `FACEBOOK_VERIFY_TOKEN` - Facebook验证令牌
  - [ ] `OPENAI_API_KEY` - OpenAI API密钥
  - [ ] `TELEGRAM_BOT_TOKEN` - Telegram机器人令牌
  - [ ] `TELEGRAM_CHAT_ID` - Telegram聊天ID
  - [ ] `SECRET_KEY` - 应用密钥（至少32字符）
  - [ ] `CORS_ORIGINS` - CORS允许的来源（生产环境必需）
  - [ ] `DEBUG=false` - 生产环境必须关闭调试模式

- [ ] `config/config.yaml` 已创建并配置业务规则
  - [ ] 自动回复配置
  - [ ] 资料收集配置
  - [ ] 过滤规则配置
  - [ ] 页面设置
  - [ ] Telegram通知配置

### 代码准备
- [ ] 代码已从仓库拉取或上传
- [ ] 虚拟环境已创建
- [ ] 依赖已安装（`pip install -r requirements.txt`）
- [ ] 代码无语法错误
- [ ] 所有测试通过

### 数据库准备
- [ ] 数据库已创建（PostgreSQL或SQLite）
- [ ] 数据库用户已创建并授权（PostgreSQL）
- [ ] 数据库连接测试通过
- [ ] 数据库迁移文件已准备

## 部署步骤

### 1. 运行部署脚本
- [ ] 运行部署脚本：`./scripts/deployment/deploy_production.sh` (Linux/Mac)
- [ ] 或：`scripts\deployment\deploy_production.bat` (Windows)
- [ ] 检查部署脚本输出，确认无错误

### 2. 数据库迁移
- [ ] 运行数据库迁移：`alembic upgrade head`
- [ ] 验证所有表已创建
- [ ] 检查迁移日志，确认无错误

### 3. 配置验证
- [ ] 验证环境变量加载：`python -c "from src.core.config import settings; print('OK')"`
- [ ] 验证数据库连接：`python -c "from src.core.database.connection import engine; engine.connect()"`
- [ ] 验证服务启动：`python -c "from src.main import app; print('OK')"`

### 4. 服务启动
- [ ] 选择启动方式：
  - [ ] systemd服务（Linux）
  - [ ] Docker容器
  - [ ] 直接运行（开发/测试）

- [ ] 服务已启动
- [ ] 服务状态正常（无错误日志）

### 5. 功能验证
- [ ] 健康检查通过：`curl http://localhost:8000/health`
- [ ] API端点可访问：`curl http://localhost:8000/`
- [ ] 性能指标可访问：`curl http://localhost:8000/metrics`
- [ ] 统计API可访问：`curl http://localhost:8000/statistics/daily`

### 6. 集成测试
- [ ] Webhook接收测试（发送测试消息到Facebook页面）
- [ ] AI自动回复测试
- [ ] 数据库记录验证
- [ ] Telegram通知测试

## 部署后检查

### 服务状态
- [ ] 服务运行正常（无崩溃）
- [ ] 日志输出正常（无错误）
- [ ] 资源使用正常（CPU、内存、磁盘）

### 性能检查
- [ ] 响应时间正常（< 500ms）
- [ ] 并发处理正常
- [ ] 数据库查询性能正常

### 安全检查
- [ ] CORS配置正确（不允许所有来源）
- [ ] DEBUG模式已关闭
- [ ] 敏感信息不在日志中
- [ ] API密钥安全存储

### 监控设置
- [ ] 性能监控已启动（可选）
- [ ] 告警机制已配置
- [ ] 日志轮转已配置
- [ ] 备份机制已设置

## 回滚准备

### 备份
- [ ] 数据库已备份
- [ ] 配置文件已备份
- [ ] 代码版本已标记（Git tag）

### 回滚方案
- [ ] 回滚步骤已文档化
- [ ] 回滚脚本已准备
- [ ] 回滚测试已进行

## 文档和记录

### 文档
- [ ] 部署文档已阅读
- [ ] 配置文档已阅读
- [ ] 故障排查文档已准备

### 记录
- [ ] 部署时间已记录
- [ ] 部署版本已记录
- [ ] 部署人员已记录
- [ ] 部署环境已记录

## 最终验证

### 完整测试
- [ ] 运行完整生产环境测试：`python scripts/test/production_test.py --test all`
- [ ] 所有关键测试通过
- [ ] 性能测试通过

### 监控验证
- [ ] 监控系统正常工作
- [ ] 告警系统正常工作
- [ ] 日志系统正常工作

## 部署完成确认

- [ ] 所有检查项已完成
- [ ] 所有测试通过
- [ ] 系统运行正常
- [ ] 监控和告警已设置

**部署人员签名：** ___________  
**部署日期：** ___________  
**部署版本：** ___________

---

## 紧急联系

如遇到问题：
1. 查看日志：`logs/app.log`
2. 查看系统日志：`sudo journalctl -u customer-service`
3. 参考故障排查文档
4. 联系技术支持

