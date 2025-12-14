# Zeabur 部署检查清单

使用此清单确保Zeabur部署的完整性和正确性。

## 部署前准备

### 环境变量准备

- [ ] `FACEBOOK_ACCESS_TOKEN` - 用户级Token（有pages_show_list权限）✅ 必需
- [ ] `FACEBOOK_APP_ID` - Facebook应用ID
- [ ] `FACEBOOK_APP_SECRET` - Facebook应用密钥
- [ ] `FACEBOOK_VERIFY_TOKEN` - Webhook验证令牌
- [ ] `OPENAI_API_KEY` - OpenAI API密钥
- [ ] `TELEGRAM_BOT_TOKEN` - Telegram Bot令牌
- [ ] `TELEGRAM_CHAT_ID` - Telegram聊天ID
- [ ] `SECRET_KEY` - 应用密钥（至少32字符）
- [ ] `DEBUG=false` - 生产环境必须
- [ ] `CORS_ORIGINS` - 部署后设置（格式：https://xxx.zeabur.app）

### 代码准备

- [ ] 代码已推送到GitHub（如果使用GitHub部署）
- [ ] 所有文件已保存
- [ ] 本地测试已通过
- [ ] `Procfile` 存在
- [ ] `requirements.txt` 完整

### 本地测试

- [ ] 运行部署前测试：`scripts\test\pre_deployment_test.bat`
- [ ] 所有基础测试通过
- [ ] 多页面Token配置正确

## Zeabur部署步骤

### 步骤1：创建项目

- [ ] 访问 https://zeabur.com
- [ ] 登录/注册账号
- [ ] 创建新项目
- [ ] 选择 "Deploy from GitHub"
- [ ] 选择仓库和分支

### 步骤2：添加数据库

- [ ] 添加PostgreSQL服务
- [ ] 等待数据库启动完成
- [ ] 确认 `DATABASE_URL` 自动设置

### 步骤3：配置环境变量

- [ ] 添加所有必需的环境变量
- [ ] `FACEBOOK_ACCESS_TOKEN` 设置为用户级Token
- [ ] `DEBUG=false`
- [ ] 保存环境变量

### 步骤4：部署

- [ ] 点击 "Deploy" 或等待自动部署
- [ ] 查看构建日志，确认成功
- [ ] 等待服务启动完成
- [ ] 获取应用URL

### 步骤5：运行数据库迁移

- [ ] 通过Zeabur终端连接
- [ ] 运行：`alembic upgrade head`
- [ ] 确认迁移成功

### 步骤6：同步页面Token（重要！）

- [ ] 运行：`python scripts/tools/manage_pages.py sync`
- [ ] 确认所有10+页面Token已同步
- [ ] 运行：`python scripts/tools/manage_pages.py status` 验证

### 步骤7：更新Facebook Webhook

- [ ] 登录Facebook Developer Console
- [ ] 更新Webhook URL为Zeabur地址
- [ ] 确认Verify Token一致
- [ ] 测试Webhook验证

### 步骤8：验证部署

- [ ] 健康检查：`curl https://your-app-name.zeabur.app/health`
- [ ] API文档可访问：`https://your-app-name.zeabur.app/docs`
- [ ] 发送测试消息到Facebook页面
- [ ] 验证自动回复功能
- [ ] 检查日志，确认无错误

## 部署后验证

### 功能验证

- [ ] 健康检查返回 "healthy"
- [ ] 所有API端点可访问
- [ ] 数据库连接正常
- [ ] 所有页面Token已配置
- [ ] Webhook接收正常
- [ ] AI自动回复功能正常
- [ ] 多页面功能正常（向不同页面发送消息测试）

### 性能验证

- [ ] 响应时间正常
- [ ] 无错误日志
- [ ] 资源使用正常

## 部署信息记录

- [ ] 部署时间：___________
- [ ] 部署人员：___________
- [ ] 应用URL：___________
- [ ] 数据库URL：___________
- [ ] 已配置页面数：___________

## 问题记录

如有问题，请记录：

**问题1：**
- 描述：___________
- 解决方案：___________

**问题2：**
- 描述：___________
- 解决方案：___________

## 部署完成确认

- [ ] 所有步骤已完成
- [ ] 所有验证通过
- [ ] 系统运行正常
- [ ] 可以开始使用

**部署人员签名：** ___________  
**部署日期：** ___________

