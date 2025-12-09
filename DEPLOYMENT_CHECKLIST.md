# 部署检查清单

## 📋 部署前检查

### 环境准备
- [ ] Python 3.9+ 已安装
- [ ] PostgreSQL 12+ 已安装并运行
- [ ] Git 已安装（如果从仓库部署）
- [ ] 虚拟环境工具已安装（venv/virtualenv）

### 配置文件
- [ ] `.env` 文件已创建并配置
  - [ ] `DATABASE_URL` - 数据库连接字符串
  - [ ] `FACEBOOK_APP_ID` - Facebook 应用 ID
  - [ ] `FACEBOOK_APP_SECRET` - Facebook 应用密钥
  - [ ] `FACEBOOK_ACCESS_TOKEN` - Facebook 访问令牌
  - [ ] `FACEBOOK_VERIFY_TOKEN` - Facebook 验证令牌
  - [ ] `OPENAI_API_KEY` - OpenAI API 密钥
  - [ ] `TELEGRAM_BOT_TOKEN` - Telegram Bot 令牌
  - [ ] `TELEGRAM_CHAT_ID` - Telegram 聊天 ID
  - [ ] `SECRET_KEY` - 应用密钥
- [ ] `config.yaml` 文件已创建并配置
  - [ ] 自动回复配置
  - [ ] 资料收集配置
  - [ ] 过滤规则配置
  - [ ] 页面设置（如果使用）

### 数据库
- [ ] PostgreSQL 数据库已创建
- [ ] 数据库用户已创建并授权
- [ ] 数据库连接测试通过
- [ ] 数据库迁移已运行（`alembic upgrade head`）

### 依赖安装
- [ ] 虚拟环境已创建
- [ ] 依赖已安装（`pip install -r requirements.txt`）
- [ ] 所有依赖安装成功，无错误

### API 密钥验证
- [ ] Facebook API 密钥有效
- [ ] OpenAI API 密钥有效
- [ ] Telegram Bot 令牌有效
- [ ] 所有 API 密钥权限正确

## 🚀 部署步骤

### 开发环境
- [ ] 运行部署脚本：`./deploy.sh` 或 `deploy.bat`
- [ ] 启动服务：`python run.py`
- [ ] 验证服务运行：访问 http://localhost:8000/health

### 生产环境（Docker）
- [ ] Docker 和 Docker Compose 已安装
- [ ] `.env` 文件已配置
- [ ] 运行：`docker-compose up -d`
- [ ] 验证容器运行：`docker-compose ps`
- [ ] 查看日志：`docker-compose logs -f app`

### 生产环境（系统服务）
- [ ] systemd 服务文件已创建
- [ ] 服务已启动：`sudo systemctl start customer-service`
- [ ] 服务已设置开机自启：`sudo systemctl enable customer-service`
- [ ] 服务状态正常：`sudo systemctl status customer-service`

### Nginx 配置（如果使用）
- [ ] Nginx 已安装
- [ ] Nginx 配置文件已创建
- [ ] 配置文件已启用
- [ ] Nginx 配置测试通过：`sudo nginx -t`
- [ ] Nginx 已重启：`sudo systemctl reload nginx`
- [ ] SSL 证书已配置（如果使用 HTTPS）

## ✅ 部署后验证

### 服务健康检查
- [ ] 健康检查接口正常：`curl http://localhost:8000/health`
- [ ] API 文档可访问：http://localhost:8000/docs
- [ ] 统计接口可访问：http://localhost:8000/statistics/daily

### 功能测试
- [ ] Facebook Webhook 配置正确
- [ ] 可以接收 Facebook 消息
- [ ] AI 自动回复功能正常
- [ ] 数据收集功能正常
- [ ] Telegram 通知功能正常
- [ ] 统计功能正常

### 日志检查
- [ ] 应用日志正常输出
- [ ] 无错误日志
- [ ] 日志级别设置正确

### 性能检查
- [ ] 服务响应时间正常
- [ ] 数据库查询性能正常
- [ ] 内存使用正常
- [ ] CPU 使用正常

## 🔧 维护检查

### 定期任务
- [ ] 数据库备份已配置
- [ ] 日志轮转已配置
- [ ] 监控告警已设置
- [ ] 健康检查脚本已配置

### 安全检查
- [ ] 防火墙规则已配置
- [ ] HTTPS 已启用（生产环境）
- [ ] API 密钥已安全存储
- [ ] 数据库密码强度足够
- [ ] 敏感信息不在代码中

## 📊 监控检查

### 系统监控
- [ ] CPU 使用率监控
- [ ] 内存使用率监控
- [ ] 磁盘使用率监控
- [ ] 网络流量监控

### 应用监控
- [ ] 服务可用性监控
- [ ] API 响应时间监控
- [ ] 错误率监控
- [ ] 数据库连接监控

## 🆘 故障排查准备

### 文档准备
- [ ] 部署文档已阅读
- [ ] 故障排查指南已准备
- [ ] 联系信息已记录

### 工具准备
- [ ] 日志查看工具已准备
- [ ] 数据库管理工具已准备
- [ ] 监控工具已配置

## 📝 部署记录

### 部署信息
- [ ] 部署时间已记录
- [ ] 部署版本已记录
- [ ] 部署人员已记录
- [ ] 部署环境已记录

### 问题记录
- [ ] 部署过程中的问题已记录
- [ ] 解决方案已记录
- [ ] 后续改进计划已记录

---

## 快速检查命令

```bash
# 检查配置
python -c "from src.config import settings; print('✅ 配置OK')"

# 检查数据库
python -c "from src.database.database import engine; engine.connect(); print('✅ 数据库OK')"

# 检查服务
curl http://localhost:8000/health

# 检查 Docker
docker-compose ps

# 检查系统服务
sudo systemctl status customer-service
```

---

完成所有检查项后，系统即可正常使用！




