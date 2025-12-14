# Zeabur 多页面 Token 配置 - 快速答案

## 问题：多页面自动回复时，FACEBOOK_ACCESS_TOKEN 怎么写？

### 答案

**对于多页面系统，`FACEBOOK_ACCESS_TOKEN` 应该设置为：**

#### 推荐方式：用户级别Token

```
FACEBOOK_ACCESS_TOKEN=你的用户级别Token（有pages_show_list权限）
```

**为什么？**
- 可以自动获取所有页面的Token
- 部署后运行同步脚本即可
- 不需要手动配置每个页面

**部署后操作：**
```bash
python scripts/tools/manage_page_tokens.py sync
```

#### 备选方式：默认页面Token

如果无法获取用户级别Token：

```
FACEBOOK_ACCESS_TOKEN=其中一个页面的Token（作为默认Token）
```

**注意：**
- 其他页面需要单独配置Token
- 需要通过SSH手动添加每个页面的Token

## 完整配置步骤

### 1. 在Zeabur设置环境变量

```
FACEBOOK_ACCESS_TOKEN=EAAB...你的用户Token（推荐）或页面Token
```

### 2. 部署应用

等待Zeabur完成部署。

### 3. 同步页面Token（如果使用用户Token）

通过Zeabur的终端/SSH运行：

```bash
python scripts/tools/manage_page_tokens.py sync
```

### 4. 验证配置

```bash
python scripts/tools/manage_page_tokens.py list
```

应该看到所有页面已配置。

## 工作原理

1. **环境变量中的Token** → 作为默认Token或用于同步
2. **同步脚本** → 自动获取所有页面的Token，保存到 `.page_tokens.json`
3. **系统自动选择** → 收到消息时，根据页面ID自动选择对应的Token

## 详细文档

- [完整多页面配置指南](ZEABUR_MULTI_PAGE_SETUP.md)
- [Zeabur部署指南](ZEABUR_DEPLOYMENT.md)

