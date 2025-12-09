# Facebook帖子管理和广告管理功能

## 概述

系统已添加Facebook帖子管理（发布、删除）和广告管理（ads_management）功能。

## 帖子管理功能

### 1. 发布帖子

```python
from src.facebook.api_client import FacebookAPIClient

client = FacebookAPIClient()

# 发布纯文本帖子
result = await client.create_post(
    page_id="your_page_id",
    message="这是要发布的帖子内容"
)

# 发布带链接的帖子
result = await client.create_post(
    page_id="your_page_id",
    message="查看我们的新产品",
    link="https://example.com/product"
)

# 创建草稿（不立即发布）
result = await client.create_post(
    page_id="your_page_id",
    message="这是草稿内容",
    published=False
)
```

**参数说明**：
- `page_id`: Facebook页面ID（必需）
- `message`: 帖子内容（必需）
- `link`: 链接URL（可选）
- `published`: 是否立即发布，默认True

**返回**：包含创建的帖子ID

### 2. 删除帖子

```python
result = await client.delete_post(post_id="post_id_here")
```

**参数说明**：
- `post_id`: 要删除的帖子ID（必需）

**返回**：删除成功确认

### 3. 获取帖子信息

```python
# 获取基本信息
post = await client.get_post(post_id="post_id_here")

# 获取指定字段
post = await client.get_post(
    post_id="post_id_here",
    fields="id,message,created_time,likes.summary(true),comments.summary(true)"
)
```

**默认字段**：id, message, created_time, updated_time, likes, comments, shares

## 广告管理功能

### 权限要求

广告管理功能需要以下权限：
- `ads_read` - 读取广告数据
- `ads_management` - 管理广告

在Facebook Developer Console中为应用添加这些权限。

### 1. 获取广告账户

```python
accounts = await client.get_ad_accounts()
```

**返回**：广告账户列表，包含账户ID、名称、状态等信息

### 2. 获取广告列表

```python
ads = await client.get_ads(ad_account_id="your_account_id")

# 获取指定字段
ads = await client.get_ads(
    ad_account_id="your_account_id",
    fields="id,name,status,effective_status,insights"
)
```

**默认字段**：id, name, status, effective_status, adset_id, campaign_id

### 3. 获取单个广告信息

```python
ad = await client.get_ad(ad_id="ad_id_here")
```

### 4. 创建广告

```python
result = await client.create_ad(
    ad_account_id="your_account_id",
    adset_id="adset_id_here",
    creative_id="creative_id_here",
    name="新广告名称",
    status="PAUSED"  # 或 "ACTIVE"
)
```

**参数说明**：
- `ad_account_id`: 广告账户ID（必需）
- `adset_id`: 广告组ID（必需）
- `creative_id`: 创意ID（必需）
- `name`: 广告名称（必需）
- `status`: 广告状态，默认"PAUSED"

### 5. 更新广告

```python
# 更新广告名称
result = await client.update_ad(
    ad_id="ad_id_here",
    name="新名称"
)

# 更新广告状态
result = await client.update_ad(
    ad_id="ad_id_here",
    status="ACTIVE"
)

# 同时更新多个字段
result = await client.update_ad(
    ad_id="ad_id_here",
    name="新名称",
    status="PAUSED"
)
```

### 6. 删除广告

```python
result = await client.delete_ad(ad_id="ad_id_here")
```

### 7. 获取广告系列列表

```python
campaigns = await client.get_campaigns(ad_account_id="your_account_id")
```

**默认字段**：id, name, status, objective, spend_cap

### 8. 获取广告组列表

```python
adsets = await client.get_adsets(ad_account_id="your_account_id")
```

**默认字段**：id, name, status, campaign_id, daily_budget, lifetime_budget

## 使用示例

### 完整示例：发布帖子并获取信息

```python
import asyncio
from src.facebook.api_client import FacebookAPIClient

async def main():
    client = FacebookAPIClient()
    
    try:
        # 发布帖子
        result = await client.create_post(
            page_id="your_page_id",
            message="这是测试帖子"
        )
        post_id = result.get("id")
        print(f"帖子已发布，ID: {post_id}")
        
        # 获取帖子信息
        post = await client.get_post(post_id)
        print(f"帖子内容: {post.get('message')}")
        
        # 删除帖子（如果需要）
        # delete_result = await client.delete_post(post_id)
        # print("帖子已删除")
        
    finally:
        await client.close()

asyncio.run(main())
```

### 完整示例：广告管理

```python
import asyncio
from src.facebook.api_client import FacebookAPIClient

async def main():
    client = FacebookAPIClient()
    
    try:
        # 获取广告账户
        accounts = await client.get_ad_accounts()
        if accounts.get("data"):
            account_id = accounts["data"][0]["id"].replace("act_", "")
            print(f"使用广告账户: {account_id}")
            
            # 获取广告列表
            ads = await client.get_ads(account_id)
            print(f"共有 {len(ads.get('data', []))} 个广告")
            
            # 获取广告系列
            campaigns = await client.get_campaigns(account_id)
            print(f"共有 {len(campaigns.get('data', []))} 个广告系列")
            
            # 获取广告组
            adsets = await client.get_adsets(account_id)
            print(f"共有 {len(adsets.get('data', []))} 个广告组")
        
    finally:
        await client.close()

asyncio.run(main())
```

## API端点参考

### 帖子管理
- `POST /{page-id}/feed` - 发布帖子
- `DELETE /{post-id}` - 删除帖子
- `GET /{post-id}` - 获取帖子信息

### 广告管理
- `GET /me/adaccounts` - 获取广告账户
- `GET /act_{account-id}/ads` - 获取广告列表
- `GET /{ad-id}` - 获取广告信息
- `POST /act_{account-id}/ads` - 创建广告
- `POST /{ad-id}` - 更新广告
- `DELETE /{ad-id}` - 删除广告
- `GET /act_{account-id}/campaigns` - 获取广告系列
- `GET /act_{account-id}/adsets` - 获取广告组

## 注意事项

1. **权限要求**：
   - 帖子管理需要 `pages_manage_posts` 权限
   - 广告管理需要 `ads_read` 和 `ads_management` 权限

2. **访问令牌**：
   - 确保访问令牌具有相应的权限
   - 页面帖子需要使用页面访问令牌（Page Access Token）

3. **错误处理**：
   - 所有方法都会抛出异常，建议使用try-except处理
   - 检查API响应的错误信息

4. **速率限制**：
   - Facebook API有速率限制，注意控制请求频率
   - 广告API的速率限制更严格

## 相关文档

- [Facebook Graph API - Posts](https://developers.facebook.com/docs/graph-api/reference/post/)
- [Facebook Marketing API - Ads](https://developers.facebook.com/docs/marketing-apis)
- [Facebook Permissions](https://developers.facebook.com/docs/permissions/reference)







