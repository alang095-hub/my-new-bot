#!/usr/bin/env python3
"""
部署前敏感信息检查脚本
检查代码中是否有硬编码的敏感信息（API密钥、Token等）
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 敏感信息模式
SENSITIVE_PATTERNS = {
    "facebook_token": [
        r'EAAG[A-Za-z0-9]{100,}',  # Facebook长期Token
        r'EAAMDtAYXh[A-Za-z0-9]{100,}',  # Facebook Token格式
    ],
    "openai_key": [
        r'sk-[A-Za-z0-9]{30,}',  # OpenAI API Key
        r'sk-proj-[A-Za-z0-9]{30,}',  # OpenAI项目Key
    ],
    "github_token": [
        r'ghp_[A-Za-z0-9]{30,}',  # GitHub Personal Access Token
        r'gho_[A-Za-z0-9]{30,}',  # GitHub OAuth Token
    ],
    "telegram_token": [
        r'\d{8,}:[A-Za-z0-9_-]{30,}',  # Telegram Bot Token
    ],
    "secret_key": [
        r'SECRET_KEY\s*=\s*["\'][A-Za-z0-9_-]{32,}["\']',  # 硬编码的SECRET_KEY
    ],
    "database_url": [
        r'postgresql://[^:]+:[^@]+@',  # 包含密码的数据库URL
        r'mysql://[^:]+:[^@]+@',  # MySQL URL with password
    ],
}

# 应该忽略的文件和目录
IGNORE_PATTERNS = [
    '.git',
    '__pycache__',
    '.pytest_cache',
    'venv',
    'env',
    '.venv',
    'node_modules',
    '.env',
    '.env.local',
    '*.pyc',
    '*.pyo',
    '*.log',
    'logs/',
    'dist/',
    'build/',
    '.idea',
    '.vscode',
]

# 应该检查的文件扩展名
CHECK_EXTENSIONS = ['.py', '.yaml', '.yml', '.json', '.md', '.txt', '.bat', '.sh', '.ps1']


def should_ignore_file(file_path: Path) -> bool:
    """检查文件是否应该被忽略"""
    path_str = str(file_path)
    
    # 检查是否匹配忽略模式
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
    
    # 检查是否在.gitignore中（通过检查常见敏感文件）
    sensitive_local_files = [
        '.page_tokens.json',
        'logs/',
        '.env',
        'config/config.yaml',
    ]
    for sensitive_file in sensitive_local_files:
        if sensitive_file in path_str:
            return True
    
    # 忽略日志文件（即使扩展名匹配）
    if 'log' in path_str.lower() or file_path.suffix == '.log':
        return True
    
    # 检查扩展名
    if file_path.suffix not in CHECK_EXTENSIONS:
        return False
    
    return False


def check_file_for_sensitive_data(file_path: Path) -> List[Dict[str, any]]:
    """检查文件中的敏感信息"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return issues
    
    # 检查每个敏感信息模式
    for category, patterns in SENSITIVE_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # 检查是否是占位符或示例
                matched_text = match.group(0)
                if any(placeholder in matched_text.lower() for placeholder in ['your_', 'placeholder', 'example', 'sample', 'test_', 'password', 'postgres', 'abc123']):
                    continue
                
                # 对于数据库URL，检查是否是示例（包含常见的示例密码）
                if category == "database_url":
                    if any(example in matched_text.lower() for example in ['postgres:postgres', 'user:password', 'username:password', 'localhost']):
                        continue
                
                # 找到匹配的行号
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ''
                
                # 忽略占位符Token
                if any(placeholder in matched_text for placeholder in ['YOUR_', 'PLACEHOLDER', 'EXAMPLE_TOKEN']):
                    continue
                
                # 忽略检查脚本本身的正则表达式模式
                if 'check_sensitive_data.py' in str(file_path):
                    # 检查是否是正则表达式定义（包含 r' 或 r" 或 # 注释）
                    line_before = lines[line_num - 2] if line_num > 1 else ''
                    if 'r\'' in line_content or 'r"' in line_content or '#' in line_content or 'SENSITIVE_PATTERNS' in line_before:
                        continue
                
                issues.append({
                    "category": category,
                    "pattern": pattern,
                    "matched_text": matched_text[:50] + "..." if len(matched_text) > 50 else matched_text,
                    "line": line_num,
                    "file": str(file_path),
                    "line_content": line_content.strip()[:100]
                })
    
    return issues


def scan_directory(root_dir: Path) -> List[Dict[str, any]]:
    """扫描目录查找敏感信息"""
    all_issues = []
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and not should_ignore_file(file_path):
            issues = check_file_for_sensitive_data(file_path)
            all_issues.extend(issues)
    
    return all_issues


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 敏感信息检查")
    print("=" * 60)
    print()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent.parent.parent
    root_dir = script_dir
    
    print(f"扫描目录: {root_dir}")
    print()
    
    # 扫描文件
    print("正在扫描文件...")
    issues = scan_directory(root_dir)
    
    # 按类别分组
    issues_by_category = {}
    for issue in issues:
        category = issue["category"]
        if category not in issues_by_category:
            issues_by_category[category] = []
        issues_by_category[category].append(issue)
    
    # 打印结果
    if not issues:
        print("✅ 未发现敏感信息泄露！")
        print()
        return 0
    
    print(f"⚠️  发现 {len(issues)} 个潜在敏感信息泄露问题：")
    print()
    
    for category, category_issues in issues_by_category.items():
        print(f"📋 {category.upper()} ({len(category_issues)} 个问题)")
        print("-" * 60)
        
        for issue in category_issues[:5]:  # 只显示前5个
            print(f"  文件: {issue['file']}")
            print(f"  行号: {issue['line']}")
            print(f"  匹配: {issue['matched_text']}")
            print(f"  内容: {issue['line_content']}")
            print()
        
        if len(category_issues) > 5:
            print(f"  ... 还有 {len(category_issues) - 5} 个问题未显示")
            print()
    
    print("=" * 60)
    print("⚠️  建议")
    print("=" * 60)
    print()
    print("1. 检查上述文件，确认是否包含真实的敏感信息")
    print("2. 如果是真实密钥，请立即：")
    print("   - 删除或替换为占位符")
    print("   - 在相关服务中撤销/重新生成密钥")
    print("3. 确保 .env 文件在 .gitignore 中")
    print("4. 确保 config/config.yaml 在 .gitignore 中")
    print("5. 检查 Git 历史记录，如果已提交敏感信息，考虑清理历史")
    print()
    
    return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

