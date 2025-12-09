# Facebook权限配置指南

## 概述

本指南说明如何为Facebook应用配置所需的权限，以使用帖子管理和广告管理功能。

## 所需权限列表

### 基础权限（消息功能）
- `pages_messaging` - 发送和接收消息
- `pages_read_engagement` - 读取页面互动数据
- `pages_manage_metadata` - 管理页面元数据

### 帖子管理权限
- `pages_manage_posts` - 管理页面帖子（发布、删除）

### 广告管理权限
- `ads_read` - 读取广告数据
- `ads_management` - 管理广告（创建、更新、删除）

## 配置步骤

### 步骤1：访问Facebook Developer Console

1. 访问 https://developers.facebook.com/
2. 登录您的Facebook账号
3. 选择您的应用（或创建新应用）

### 步骤2：添加产品

#### 添加Facebook Login产品（如果未添加）

1. 在应用仪表板中，点击"添加产品"
2. 找到"Facebook Login"并点击"设置"
3. 按照提示完成基本配置

#### 添加Marketing API产品（用于广告管理）

1. 在应用仪表板中，点击"添加产品"
2. 找到"Marketing API"并点击"设置"
3. 按照提示完成基本配置

### 步骤3：配置权限

#### 方法1：通过应用设置配置

1. 进入应用设置 → 基本
2. 找到"应用审查"部分
3. 点击"权限和功能"
4. 添加以下权限：
   - `pages_manage_posts`
   - `ads_read`
   - `ads_management`

#### 方法2：通过OAuth URL配置

在生成OAuth授权URL时，包含所有需要的权限：

```
https://www.facebook.com/v18.0/dialog/oauth?
  client_id=YOUR_APP_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &scope=pages_messaging,pages_read_engagement,pages_manage_metadata,pages_manage_posts,ads_read,ads_management
  &response_type=token
```

### 步骤4：权限审查（如需要）

某些高级权限（如`ads_management`）可能需要通过Facebook的应用审查：

1. 进入应用审查 → 权限和功能
2. 找到需要审查的权限
3. 点击"请求"或"开始使用"
4. 按照提示提交审查申请
5. 等待Facebook审核（通常需要1-3个工作日）

### 步骤5：获取访问令牌

#### 短期访问令牌

1. 使用Graph API Explorer：
   - 访问 https://developers.facebook.com/tools/explorer/
   - 选择您的应用
   - 选择所需的权限
   - 点击"生成访问令牌"

#### 长期访问令牌

使用短期令牌交换长期令牌：

```bash
python exchange_token.py
```

或使用脚本：

```python
# 交换长期令牌
GET https://graph.facebook.com/v18.0/oauth/access_token?
  grant_type=fb_exchange_token
  &client_id=YOUR_APP_ID
  &client_secret=YOUR_APP_SECRET
  &fb_exchange_token=SHORT_LIVED_TOKEN
```

### 步骤6：验证权限

运行权限检查工具：

```bash
python check_facebook_permissions.py
```

## 权限说明

### pages_manage_posts

**用途**：管理Facebook页面帖子

**功能**：
- 发布新帖子
- 删除帖子
- 编辑帖子（通过API）

**审查要求**：通常不需要审查（对于已管理的页面）

### ads_read

**用途**：读取广告账户和广告数据

**功能**：
- 查看广告账户信息
- 查看广告列表
- 查看广告详情
- 查看广告系列和广告组

**审查要求**：通常不需要审查

### ads_management

**用途**：管理广告（创建、更新、删除）

**功能**：
- 创建新广告
- 更新广告设置
- 删除广告
- 管理广告系列和广告组

**审查要求**：**需要应用审查**

## 应用审查流程

### 1. 准备审查材料

- 应用说明文档
- 使用场景说明
- 隐私政策URL
- 应用截图或视频演示

### 2. 提交审查

1. 进入应用审查 → 权限和功能
2. 找到`ads_management`权限
3. 点击"开始使用"
4. 填写审查表单
5. 提交审查申请

### 3. 审查时间

- 通常需要1-3个工作日
- Facebook可能会要求提供更多信息

### 4. 审查通过后

- 权限将自动激活
- 可以开始使用广告管理功能

## 测试权限

### 测试帖子管理权限

```python
from src.facebook.api_client import FacebookAPIClient

client = FacebookAPIClient()

# 测试发布帖子（需要pages_manage_posts权限）
try:
    result = await client.create_post(
        page_id="your_page_id",
        message="测试帖子"
    )
    print("✅ 帖子管理权限正常")
except Exception as e:
    print(f"❌ 权限不足: {e}")
```

### 测试广告管理权限

```python
# 测试获取广告账户（需要ads_read权限）
try:
    accounts = await client.get_ad_accounts()
    print("✅ ads_read权限正常")
except Exception as e:
    print(f"❌ ads_read权限不足: {e}")

# 测试创建广告（需要ads_management权限）
try:
    ad = await client.create_ad(
        ad_account_id="account_id",
        adset_id="adset_id",
        creative_id="creative_id",
        name="测试广告"
    )
    print("✅ ads_management权限正常")
except Exception as e:
    print(f"❌ ads_management权限不足: {e}")
```

## 常见问题

### Q: 为什么无法发布帖子？

**A**: 检查以下几点：
1. 是否已添加`pages_manage_posts`权限
2. 访问令牌是否包含该权限
3. 是否使用页面访问令牌（Page Access Token）而不是用户访问令牌

### Q: 为什么无法访问广告数据？

**A**: 检查以下几点：
1. 是否已添加`ads_read`权限
2. 访问令牌是否包含该权限
3. 广告账户是否与Facebook账号关联

### Q: 为什么无法创建广告？

**A**: 检查以下几点：
1. 是否已添加`ads_management`权限
2. 是否已通过应用审查
3. 访问令牌是否包含该权限
4. 是否有广告账户的管理权限

### Q: 如何检查当前令牌的权限？

**A**: 使用以下API调用：

```
GET https://graph.facebook.com/v18.0/me/permissions?access_token=YOUR_TOKEN
```

或运行权限检查工具：

```bash
python check_facebook_permissions.py
```

## 相关文档

- `FACEBOOK_POST_AND_ADS_MANAGEMENT.md` - 功能使用指南
- `FACEBOOK_OAUTH_GUIDE.md` - OAuth授权指南
- `GET_ACCESS_TOKEN.md` - 获取访问令牌指南

## 快速参考

### 完整权限列表（OAuth scope）

```
pages_messaging,pages_read_engagement,pages_manage_metadata,pages_manage_posts,ads_read,ads_management
```

### 权限检查API

```
GET /me/permissions?access_token=YOUR_TOKEN
```

### 交换长期令牌

```
GET /oauth/access_token?
  grant_type=fb_exchange_token
  &client_id=APP_ID
  &client_secret=APP_SECRET
  &fb_exchange_token=SHORT_TOKEN
```







