# 部署检查清单（小白版）

本文档提供了完整的部署检查清单，确保每一步都正确完成。

## 📋 部署前检查

### 代码准备

- [ ] 代码已推送到GitHub
- [ ] GitHub仓库是公开的或已授权Zeabur访问
- [ ] `requirements.txt`文件存在且完整
- [ ] `Dockerfile`文件存在（可选，Zeabur会自动检测）
- [ ] 代码在本地可以正常运行

### 环境变量准备

- [ ] **Facebook配置**已准备
  - [ ] `FACEBOOK_APP_ID`
  - [ ] `FACEBOOK_APP_SECRET`
  - [ ] `FACEBOOK_ACCESS_TOKEN`
  - [ ] `FACEBOOK_VERIFY_TOKEN`（任意字符串）

- [ ] **OpenAI配置**已准备
  - [ ] `OPENAI_API_KEY`

- [ ] **Telegram配置**已准备
  - [ ] `TELEGRAM_BOT_TOKEN`
  - [ ] `TELEGRAM_CHAT_ID`

- [ ] **安全配置**已准备
  - [ ] `SECRET_KEY`（32位以上随机字符串）
  - [ ] `DEBUG=false`

### 本地测试

- [ ] 运行了本地快速测试
  ```bash
  python scripts/test/local_test.py
  ```
- [ ] 所有基础测试通过
- [ ] 服务可以在本地启动

## 🚀 部署中检查

### Zeabur账号和项目

- [ ] Zeabur账号已创建
- [ ] 已登录Zeabur控制台
- [ ] 新项目已创建
- [ ] 项目名称已设置

### GitHub连接

- [ ] GitHub仓库已连接到Zeabur
- [ ] Zeabur可以访问仓库
- [ ] 项目类型已自动检测（Python/FastAPI）

### 数据库服务

- [ ] PostgreSQL服务已添加
- [ ] 数据库服务创建成功（绿色状态）
- [ ] `DATABASE_URL`已复制
- [ ] 数据库服务运行正常

### 环境变量配置

- [ ] **数据库配置**
  - [ ] `DATABASE_URL`已添加（从PostgreSQL服务复制）

- [ ] **Facebook配置**
  - [ ] `FACEBOOK_APP_ID`已添加
  - [ ] `FACEBOOK_APP_SECRET`已添加
  - [ ] `FACEBOOK_ACCESS_TOKEN`已添加
  - [ ] `FACEBOOK_VERIFY_TOKEN`已添加

- [ ] **OpenAI配置**
  - [ ] `OPENAI_API_KEY`已添加
  - [ ] `OPENAI_MODEL`已添加（可选，默认：gpt-4o-mini）
  - [ ] `OPENAI_TEMPERATURE`已添加（可选，默认：0.7）

- [ ] **Telegram配置**
  - [ ] `TELEGRAM_BOT_TOKEN`已添加
  - [ ] `TELEGRAM_CHAT_ID`已添加

- [ ] **安全配置**
  - [ ] `SECRET_KEY`已添加（32位以上）
  - [ ] `DEBUG=false`已添加

- [ ] **服务器配置**（可选）
  - [ ] `HOST=0.0.0.0`已添加（可选）

### 部署启动

- [ ] 点击了"Deploy"（部署）按钮
- [ ] 构建已启动
- [ ] 正在查看构建日志
- [ ] 构建过程中无错误

## ✅ 部署后检查

### 服务状态

- [ ] 服务状态为绿色（运行中）
- [ ] 无错误提示
- [ ] 服务日志正常

### 应用URL

- [ ] 应用URL已获取
- [ ] URL格式正确（https://xxx.zeabur.app）
- [ ] URL已复制保存

### 数据库迁移

- [ ] 已通过Zeabur终端运行迁移
  ```bash
  alembic upgrade head
  ```
- [ ] 迁移执行成功
- [ ] 无迁移错误

### 健康检查

- [ ] 访问了 `/health/simple` 端点
- [ ] 返回状态为 `{"status": "ok"}`
- [ ] 响应时间正常（< 1秒）

### API文档

- [ ] 访问了 `/docs` 端点
- [ ] Swagger文档页面正常显示
- [ ] 可以看到所有API端点

## 🔗 外部配置检查

### Facebook Webhook配置

- [ ] 已登录Facebook开发者控制台
- [ ] 已进入应用设置
- [ ] Webhook URL已配置
  - [ ] URL格式：`https://your-app-name.zeabur.app/webhook`
  - [ ] URL正确无误
- [ ] Verify Token已配置
  - [ ] Token与`FACEBOOK_VERIFY_TOKEN`环境变量一致
- [ ] Webhook验证成功（绿色勾号）
- [ ] 已订阅事件
  - [ ] `messages` - 消息
  - [ ] `messaging_postbacks` - 回传
  - [ ] `feed` - 评论（如果需要）

## 🧪 功能测试检查

### Webhook接收测试

- [ ] 在Facebook Messenger发送了测试消息
- [ ] 在Zeabur日志中看到了消息接收记录
- [ ] 消息已保存到数据库（可选检查）

### AI回复测试

- [ ] 发送了需要AI回复的消息
- [ ] AI回复已生成
- [ ] 回复已发送到Facebook

### 数据收集测试

- [ ] 发送了包含邮箱的消息
- [ ] 邮箱已被正确提取
- [ ] 发送了包含电话的消息
- [ ] 电话已被正确提取

### Telegram通知测试

- [ ] 触发了需要通知的场景
- [ ] Telegram通知已发送
- [ ] 通知内容正确

## 📊 性能检查

### API响应时间

- [ ] 健康检查响应时间 < 100ms
- [ ] API端点响应时间 < 500ms
- [ ] 无超时错误

### 数据库性能

- [ ] 数据库查询正常
- [ ] 无慢查询警告
- [ ] 连接池正常

### 服务稳定性

- [ ] 服务运行稳定
- [ ] 无频繁重启
- [ ] 内存使用正常
- [ ] CPU使用正常

## 📝 文档和记录

### 部署记录

- [ ] 部署时间已记录
- [ ] 部署URL已保存
- [ ] 环境变量配置已备份（可选）
- [ ] 部署版本已记录（Git commit hash）

### 问题记录

- [ ] 部署过程中的问题已记录
- [ ] 解决方案已记录
- [ ] 错误日志已保存（如果有）

## 🎯 最终确认

### 所有功能正常

- [ ] 服务可以访问
- [ ] 健康检查通过
- [ ] API端点可访问
- [ ] Webhook可以接收消息
- [ ] AI回复功能正常
- [ ] 数据收集功能正常
- [ ] Telegram通知正常

### 配置正确

- [ ] 所有环境变量已配置
- [ ] Facebook Webhook已配置
- [ ] 数据库连接正常
- [ ] 所有服务运行正常

### 文档完整

- [ ] 部署步骤已记录
- [ ] 配置信息已保存
- [ ] 问题解决方案已记录

## 🚨 紧急情况处理

### 如果部署失败

1. [ ] 查看构建日志
2. [ ] 检查环境变量
3. [ ] 检查代码错误
4. [ ] 查看错误信息
5. [ ] 搜索解决方案

### 如果服务无法访问

1. [ ] 检查服务状态
2. [ ] 查看服务日志
3. [ ] 检查环境变量
4. [ ] 检查数据库连接
5. [ ] 查看错误信息

### 如果Webhook不工作

1. [ ] 检查Webhook URL
2. [ ] 检查Verify Token
3. [ ] 检查服务状态
4. [ ] 查看服务日志
5. [ ] 测试Webhook验证

## 📋 快速检查命令

### 在Zeabur终端中

```bash
# 检查环境变量
env | grep -E "(DATABASE|FACEBOOK|OPENAI|TELEGRAM|SECRET|PORT)"

# 检查Python环境
python --version
pip list | grep fastapi

# 检查数据库连接
python -c "from src.core.database.connection import get_db; next(get_db()); print('✅ 数据库连接成功')"

# 检查服务状态
curl http://localhost:$PORT/health/simple
```

### 在本地

```bash
# 运行部署验证测试
python scripts/test/full_local_test.py --url https://your-app-name.zeabur.app
```

## ✅ 完成确认

当所有检查项都完成时：

- [ ] 所有功能测试通过
- [ ] 所有配置正确
- [ ] 所有服务运行正常
- [ ] 部署文档已记录

**恭喜！部署完成！** 🎉

---

**提示**：保存此检查清单，每次部署时都按照清单检查，确保不遗漏任何步骤。
