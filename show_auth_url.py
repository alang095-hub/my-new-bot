"""显示授权URL和后续步骤"""
import urllib.parse
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("Facebook权限配置 - 分步骤指南")
    print("=" * 70)
    
    # 获取App ID
    try:
        from src.config import settings
        app_id = settings.facebook_app_id
    except Exception as e:
        print(f"❌ 无法读取配置: {str(e)}")
        return 1
    
    # 生成授权URL
    redirect_uri = "http://localhost:8000/oauth/callback"
    scope = "pages_messaging,pages_read_engagement,pages_manage_metadata,pages_manage_posts,ads_read,ads_management"
    
    base_url = "https://www.facebook.com/v18.0/dialog/oauth"
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": "token"
    }
    
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{base_url}?{query_string}"
    
    print("\n【步骤1】✅ 检查当前权限 - 已完成")
    print("   发现缺少4个权限")
    
    print("\n【步骤2】✅ 生成授权URL - 已完成")
    print("\n" + "-" * 70)
    print("授权URL（请复制并在浏览器中打开）：")
    print("-" * 70)
    print(f"\n{auth_url}\n")
    print("-" * 70)
    
    print("\n【步骤3】⏳ 授权权限 - 待完成")
    print("\n操作步骤：")
    print("  1. 复制上面的授权URL")
    print("  2. 在浏览器中打开（建议使用Chrome或Edge）")
    print("  3. 登录您的Facebook账号（如果未登录）")
    print("  4. 查看权限列表，应该看到6个权限")
    print("  5. 点击'继续'或'授权'按钮")
    print("\n⚠️  注意：如果ads_management权限提示需要审查，这是正常的")
    print("     可以先授权其他权限，稍后提交审查申请")
    
    print("\n【步骤4】⏳ 获取重定向URL - 待完成")
    print("\n授权成功后，浏览器会重定向到类似这样的URL：")
    print("  http://localhost:8000/oauth/callback#access_token=TOKEN&token_type=bearer&expires_in=...")
    print("\n请完整复制这个URL（包括#access_token=后面的所有内容）")
    
    print("\n【步骤5】⏳ 提取并更新令牌 - 待完成")
    print("\n运行以下命令：")
    print("  python extract_token.py")
    print("\n然后：")
    print("  1. 粘贴完整的重定向URL")
    print("  2. 工具会自动提取访问令牌")
    print("  3. 输入 'y' 自动更新到.env文件")
    
    print("\n【步骤6】⏳ 验证权限 - 待完成")
    print("\n运行以下命令验证权限：")
    print("  python check_facebook_permissions.py")
    print("\n预期结果：所有权限应显示为'✅ 已授予'")
    
    print("\n" + "=" * 70)
    print("快速命令参考")
    print("=" * 70)
    print("\n# 提取令牌")
    print("python extract_token.py")
    print("\n# 验证权限")
    print("python check_facebook_permissions.py")
    print("\n# （可选）交换长期令牌（60天）")
    print("python exchange_token.py")
    
    print("\n" + "=" * 70)
    print("当前状态：等待您在浏览器中完成授权（步骤3）")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())







