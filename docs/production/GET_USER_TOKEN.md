# 如何获取Facebook用户级Token（用于管理10+页面）

## 为什么需要用户级Token？

- **页面级Token**：只能管理单个页面，无法获取其他页面列表
- **用户级Token**：可以获取所有管理的页面列表，自动同步所有页面Token

## 获取用户级Token的步骤

### 方法1：使用Facebook Graph API Explorer（推荐）

1. **访问Graph API Explorer**
   - 打开：https://developers.facebook.com/tools/explorer/
   - 登录您的Facebook账号

2. **选择应用**
   - 在右上角选择您的应用（App ID: 848496661333193）

3. **获取用户Token**
   - 点击 "Get Token" → "Get User Access Token"
   - 选择以下权限：
     - ✅ `pages_show_list` - **必需**（查看页面列表）
     - ✅ `pages_messaging` - **必需**（发送消息）
     - ✅ `pages_read_engagement` - 可选（读取互动数据）
     - ✅ `pages_manage_metadata` - 可选（管理元数据）

4. **生成Token**
   - 点击 "Generate Access Token"
   - 确认权限请求
   - 复制生成的Token

5. **验证Token**
   ```bash
   python scripts/tools/verify_token.py
   ```
   应该看到：
   - ✅ Token类型: USER
   - ✅ 可以管理多个页面

### 方法2：通过应用设置获取长期Token

1. **访问应用设置**
   - 打开：https://developers.facebook.com/apps/848496661333193/settings/basic/
   - 登录并选择您的应用

2. **创建长期Token**
   - 短期Token（1-2小时）会自动过期
   - 需要转换为长期Token（60天）

3. **转换长期Token**
   ```bash
   # 使用Graph API转换
   curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
   ```

### 方法3：使用系统验证脚本

运行验证脚本检查当前Token：

```bash
python scripts/tools/verify_token.py
```

## 配置用户级Token

### 在Zeabur中配置

1. **更新环境变量**
   - 在Zeabur项目设置中
   - 找到 `FACEBOOK_ACCESS_TOKEN`
   - 更新为用户级Token

2. **同步所有页面**
   ```bash
   python scripts/tools/manage_pages.py sync
   ```

3. **验证配置**
   ```bash
   python scripts/tools/manage_pages.py status
   ```
   应该看到所有10+页面都已配置

## Token类型对比

| 特性 | 页面级Token | 用户级Token |
|------|------------|------------|
| Token类型 | PAGE | USER |
| 管理页面数 | 1个 | 多个（所有管理的页面） |
| 获取页面列表 | ❌ 不支持 | ✅ 支持 |
| 自动同步 | ❌ 不支持 | ✅ 支持 |
| 适用场景 | 单页面 | 多页面（10+） |

## 当前状态

根据验证结果：
- ❌ 当前Token是**页面级Token**（PAGE类型）
- ⚠️  无法自动同步所有页面
- ✅ 系统已手动配置了3个页面Token（可以正常工作）
- ⚠️  如果要管理10+页面，建议更换为用户级Token

## 下一步

1. **获取用户级Token**（按照上述步骤）
2. **在Zeabur中更新** `FACEBOOK_ACCESS_TOKEN`
3. **运行同步脚本**：`python scripts/tools/manage_pages.py sync`
4. **验证配置**：`python scripts/tools/manage_pages.py status`

## 注意事项

1. **Token有效期**
   - 短期Token：1-2小时
   - 长期Token：60天
   - 需要定期更新

2. **权限要求**
   - 必须有 `pages_show_list` 权限
   - 必须有 `pages_messaging` 权限

3. **安全性**
   - 不要在代码中硬编码Token
   - 使用环境变量存储
   - 定期轮换Token

## 故障排查

### 问题1：无法获取页面列表

**原因：** Token缺少 `pages_show_list` 权限

**解决：** 重新生成Token，确保选择 `pages_show_list` 权限

### 问题2：Token过期

**原因：** Token有效期已过

**解决：** 重新获取Token并更新环境变量

### 问题3：权限被拒绝

**原因：** 应用未通过Facebook审核

**解决：** 提交应用审核，或使用测试Token（仅限测试环境）

