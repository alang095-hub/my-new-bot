# 项目文档索引

本文档提供了项目中所有文档的索引，方便快速查找所需信息。

## 📚 文档分类

### 🚀 部署文档

#### 生产环境部署 (production/)
- **[ZEABUR_DEPLOYMENT.md](production/ZEABUR_DEPLOYMENT.md)** - Zeabur平台完整部署指南（推荐）
- **[ZEABUR_QUICK_START.md](production/ZEABUR_QUICK_START.md)** - Zeabur快速开始指南
- **[DEPLOYMENT_CHECKLIST.md](production/DEPLOYMENT_CHECKLIST.md)** - 部署检查清单
- **[DEPLOYMENT_GUIDE.md](production/DEPLOYMENT_GUIDE.md)** - 通用部署指南
- **[ZEABUR_ENV_VARS.md](production/ZEABUR_ENV_VARS.md)** - 环境变量详细说明
- **[ZEABUR_MULTI_PAGE_SETUP.md](production/ZEABUR_MULTI_PAGE_SETUP.md)** - 多页面配置指南
- **[POST_DEPLOYMENT_STEPS.md](production/POST_DEPLOYMENT_STEPS.md)** - 部署后步骤

#### 故障排查 (production/)
- **[502_TROUBLESHOOTING_STEPS.md](production/502_TROUBLESHOOTING_STEPS.md)** - 502错误排查步骤
- **[FIX_DATABASE_CONNECTION.md](production/FIX_DATABASE_CONNECTION.md)** - 数据库连接问题修复
- **[FIX_PORT_CONFIGURATION.md](production/FIX_PORT_CONFIGURATION.md)** - 端口配置修复
- **[DIAGNOSE_502_ERROR.md](production/DIAGNOSE_502_ERROR.md)** - 502错误诊断

#### 小白友好部署文档（推荐）
- **[Docker小白完全指南](deployment/DOCKER_FOR_BEGINNERS.md)** ⭐ 新手必读 - Docker概念解释
- **[小白部署完全指南](deployment/BEGINNER_DEPLOYMENT_GUIDE.md)** ⭐ 推荐从这里开始 - 零基础部署教程
- **[部署检查清单](deployment/DEPLOYMENT_CHECKLIST.md)** ⭐ 部署时使用 - 完整检查清单
- **[部署文档索引](deployment/README.md)** - 所有部署文档索引

#### 其他部署文档
- **[deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)** - 通用部署指南

### 📖 功能指南 (guides/)

系统功能使用指南：

- **[PAGE_AUTO_REPLY_GUIDE.md](guides/PAGE_AUTO_REPLY_GUIDE.md)** - 页面自动回复功能指南
- **[DATA_RECORDING_GUIDE.md](guides/DATA_RECORDING_GUIDE.md)** - 数据记录功能指南
- **[STATISTICS_GUIDE.md](guides/STATISTICS_GUIDE.md)** - 统计功能指南
- **[MODULAR_PROCESSORS_GUIDE.md](guides/MODULAR_PROCESSORS_GUIDE.md)** - 模块化处理器使用指南
- **[MULTI_PAGE_TOKEN_MANAGEMENT.md](guides/MULTI_PAGE_TOKEN_MANAGEMENT.md)** - 多页面Token管理
- **[FACEBOOK_PAGE_TOKEN_EXPLAINED.md](guides/FACEBOOK_PAGE_TOKEN_EXPLAINED.md)** - Facebook页面Token说明
- **[FACEBOOK_WEBHOOK_EVENTS.md](guides/FACEBOOK_WEBHOOK_EVENTS.md)** - Facebook Webhook事件说明

### 🏗️ 架构文档 (architecture/)

系统架构和设计文档：

- **[MODULAR_ARCHITECTURE.md](architecture/MODULAR_ARCHITECTURE.md)** - 模块化架构设计文档
- **[SYSTEM_FEATURES.md](architecture/SYSTEM_FEATURES.md)** - 系统功能说明文档

### 🔧 故障排查 (troubleshooting/)

- **[AI_REPLY_TROUBLESHOOTING.md](troubleshooting/AI_REPLY_TROUBLESHOOTING.md)** - AI回复问题排查
- **[TOKEN_MISMATCH_FIX.md](troubleshooting/TOKEN_MISMATCH_FIX.md)** - Token不匹配问题修复
- **[VIEWING_LOGS.md](troubleshooting/VIEWING_LOGS.md)** - 日志查看指南
- **[CORS_CONFIGURATION.md](troubleshooting/CORS_CONFIGURATION.md)** - CORS配置说明

### 📊 测试文档 (testing/)

- **[本地测试指南](testing/LOCAL_TEST_GUIDE.md)** - 详细的本地测试指南
- **[本地测试检查清单](testing/LOCAL_TEST_CHECKLIST.md)** - 完整的测试检查清单
- **[PRODUCTION_TEST_CHECKLIST.md](testing/PRODUCTION_TEST_CHECKLIST.md)** - 生产环境测试检查清单
- **[PRODUCTION_TESTING_FLOW.md](testing/PRODUCTION_TESTING_FLOW.md)** - 生产环境测试流程
- **[测试文档索引](testing/README.md)** - 所有测试文档的索引

### 📝 项目文档

- **[REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)** - 重构指南（了解新的项目结构）
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - 使用指南
- **[FINAL_MIGRATION_REPORT.md](FINAL_MIGRATION_REPORT.md)** - 最终迁移报告
- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - 清理总结

## 🔍 快速查找

### 按主题查找

**部署相关**
- 快速开始：查看 [production/ZEABUR_QUICK_START.md](production/ZEABUR_QUICK_START.md)
- 完整指南：查看 [production/ZEABUR_DEPLOYMENT.md](production/ZEABUR_DEPLOYMENT.md)
- 检查清单：查看 [production/DEPLOYMENT_CHECKLIST.md](production/DEPLOYMENT_CHECKLIST.md)

**功能使用**
- 查看 [guides/](guides/) 目录

**系统架构**
- 查看 [architecture/](architecture/) 目录

**故障排查**
- 查看 [troubleshooting/](troubleshooting/) 和 [production/](production/) 目录中的故障排查文档

## 📝 文档维护

如需添加新文档，请按照以下分类放置：

1. **部署文档** → `production/` 或 `deployment/`
2. **功能指南** → `guides/`
3. **架构文档** → `architecture/`
4. **故障排查** → `troubleshooting/` 或 `production/`
5. **测试文档** → `testing/`

并更新本索引文件。
