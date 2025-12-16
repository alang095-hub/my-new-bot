# 部署前安全检查清单

## ⚠️ 重要：部署前必须检查

在将代码推送到GitHub或部署到Zeabur之前，**必须**完成以下安全检查，确保没有敏感信息泄露。

## 🔍 检查步骤

### 1. 运行敏感信息检查脚本

```bash
python scripts/tools/check_sensitive_data.py
```

**预期结果**：应该显示 `✅ 未发现敏感信息泄露！`

**如果发现问题**：
- 立即修复所有发现的敏感信息
- 如果是真实密钥，需要：
  1. 在相关服务中撤销/重新生成密钥
  2. 删除或替换为占位符
  3. 检查Git历史，如果已提交，考虑清理历史

### 2. 检查关键文件

确保以下文件**不在Git仓库中**：

- ✅ `.env` - 环境变量文件
- ✅ `.env.local` - 本地环境变量
- ✅ `config/config.yaml` - 配置文件（包含真实配置）
- ✅ `.page_tokens.json` - 页面Token文件
- ✅ `logs/` - 日志目录（可能包含敏感信息）
- ✅ `*.log` - 日志文件

**检查方法**：
```bash
git status
```

这些文件不应该出现在 `git status` 的输出中。

### 3. 检查 .gitignore

确保 `.gitignore` 包含：

```gitignore
# Environment variables
.env
.env.local

# 配置文件
config/config.yaml
!config/config.yaml.example

# 敏感信息文件
.page_tokens.json
logs/
*.log
```

### 4. 检查文档文件

检查所有 `.md` 文档文件，确保：
- ✅ 没有硬编码的真实API密钥
- ✅ 没有硬编码的真实Token
- ✅ 没有硬编码的真实密码
- ✅ 所有示例都使用占位符（如 `your_token_here`）

### 5. 检查配置文件

确保 `config/config.yaml` 文件：
- ✅ 在 `.gitignore` 中
- ✅ 不会被提交到Git
- ✅ 只提交 `config/config.yaml.example`

### 6. 检查代码文件

确保源代码中：
- ✅ 所有API密钥从环境变量读取
- ✅ 没有硬编码的真实密钥
- ✅ 占位符值会被验证器拒绝（如 `your_` 开头）

## 🚨 发现敏感信息后的处理

### 如果发现真实密钥已提交到Git

1. **立即撤销密钥**：
   - Facebook Token：在Facebook开发者控制台撤销
   - OpenAI Key：在OpenAI平台撤销
   - Telegram Bot Token：重新生成Bot Token
   - GitHub Token：在GitHub设置中撤销

2. **清理Git历史**（如果密钥已提交）：
   ```bash
   # 使用 git-filter-repo 清理历史
   git filter-repo --path config/config.yaml --invert-paths
   git filter-repo --path .page_tokens.json --invert-paths
   ```

3. **强制推送**（谨慎使用）：
   ```bash
   git push --force
   ```

## ✅ 部署前最终检查

在推送到GitHub之前，运行：

```bash
# 1. 检查敏感信息
python scripts/tools/check_sensitive_data.py

# 2. 检查Git状态
git status

# 3. 检查要提交的文件
git diff --cached --name-only
```

**确保**：
- ✅ 敏感信息检查通过
- ✅ 没有敏感文件被添加到暂存区
- ✅ `.gitignore` 正确配置

## 📋 快速检查清单

在每次提交前，快速检查：

- [ ] 运行 `python scripts/tools/check_sensitive_data.py`
- [ ] 检查 `git status` 没有敏感文件
- [ ] 检查文档中没有真实密钥
- [ ] 检查代码中没有硬编码密钥
- [ ] 确认 `.gitignore` 已更新

## 🔒 安全最佳实践

1. **永远不要提交**：
   - `.env` 文件
   - `config/config.yaml`（真实配置）
   - `.page_tokens.json`
   - 日志文件

2. **使用环境变量**：
   - 所有敏感信息通过环境变量配置
   - 在Zeabur中设置环境变量，不要硬编码

3. **使用占位符**：
   - 文档和示例使用占位符
   - 代码验证器会拒绝占位符值

4. **定期检查**：
   - 定期运行敏感信息检查脚本
   - 检查Git历史是否有敏感信息

## 📚 相关文档

- [部署准备检查](scripts/deployment/prepare_deployment.py)
- [敏感信息检查脚本](scripts/tools/check_sensitive_data.py)
- [.gitignore配置](.gitignore)

---

**重要提示**：如果发现敏感信息已泄露，立即撤销相关密钥并重新生成！

