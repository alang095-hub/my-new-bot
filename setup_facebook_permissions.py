"""Facebook权限配置自动化工具"""
import sys
import os
import webbrowser
import asyncio
import httpx

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_current_permissions():
    """检查当前权限状态"""
    print("=" * 60)
    print("步骤1：检查当前权限状态")
    print("=" * 60)
    
    try:
        from src.config import settings
        access_token = settings.facebook_access_token
        
        if not access_token:
            print("❌ 访问令牌未配置")
            return False, None
        
        print(f"\n✅ 找到访问令牌: {access_token[:20]}...")
        
        # 检查权限
        base_url = "https://graph.facebook.com/v18.0"
        
        async def check():
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{base_url}/me/permissions"
                params = {"access_token": access_token}
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                permissions = {p["permission"]: p["status"] == "granted" 
                             for p in data.get("data", [])}
                
                required = {
                    "pages_messaging": "基础权限",
                    "pages_read_engagement": "基础权限",
                    "pages_manage_metadata": "基础权限",
                    "pages_manage_posts": "帖子管理",
                    "ads_read": "广告管理",
                    "ads_management": "广告管理"
                }
                
                missing = []
                granted = []
                
                print("\n权限检查结果:")
                for perm, category in required.items():
                    if perm in permissions and permissions[perm]:
                        print(f"  ✅ {perm} ({category})")
                        granted.append(perm)
                    else:
                        print(f"  ❌ {perm} ({category}) - 缺失")
                        missing.append(perm)
                
                return len(missing) == 0, missing
        
        result, missing = asyncio.run(check())
        return result, missing
        
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False, None


def generate_oauth_url():
    """生成OAuth授权URL"""
    print("\n" + "=" * 60)
    print("步骤2：生成OAuth授权URL")
    print("=" * 60)
    
    try:
        from src.config import settings
        app_id = settings.facebook_app_id
        print(f"\n✅ 使用App ID: {app_id}")
    except Exception as e:
        print(f"⚠️  无法从配置读取App ID: {str(e)}")
        app_id = input("请输入Facebook App ID: ").strip()
        if not app_id:
            print("❌ App ID不能为空")
            return None
    
    redirect_uri = "http://localhost:8000/oauth/callback"
    scope = "pages_messaging,pages_read_engagement,pages_manage_metadata,pages_manage_posts,ads_read,ads_management"
    
    import urllib.parse
    base_url = "https://www.facebook.com/v18.0/dialog/oauth"
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": "token"
    }
    
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{base_url}?{query_string}"
    
    print(f"\n✅ 授权URL已生成")
    print(f"\n包含的权限:")
    print("  - pages_messaging (基础权限)")
    print("  - pages_read_engagement (基础权限)")
    print("  - pages_manage_metadata (基础权限)")
    print("  - pages_manage_posts (帖子管理)")
    print("  - ads_read (广告管理)")
    print("  - ads_management (广告管理)")
    
    return auth_url


def open_browser(auth_url):
    """在浏览器中打开授权URL"""
    print("\n" + "=" * 60)
    print("步骤3：打开授权页面")
    print("=" * 60)
    
    print(f"\n授权URL:")
    print(f"{auth_url}\n")
    
    print("是否在浏览器中自动打开？(y/n): ", end="")
    if sys.stdin.isatty():
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes', '']:
                print("\n正在打开浏览器...")
                webbrowser.open(auth_url)
                print("✅ 浏览器已打开")
                return True
        except:
            pass
    
    print("\n请手动复制上面的URL并在浏览器中打开")
    return False


def extract_and_update_token():
    """提取并更新访问令牌"""
    print("\n" + "=" * 60)
    print("步骤4：提取并更新访问令牌")
    print("=" * 60)
    
    print("\n请粘贴授权后的重定向URL:")
    print("格式: http://localhost:8000/oauth/callback#access_token=TOKEN&...")
    
    if sys.stdin.isatty():
        url = input("\nURL: ").strip()
    else:
        print("(非交互模式，跳过令牌提取)")
        return False
    
    if not url:
        print("❌ URL不能为空")
        return False
    
    # 提取令牌
    import urllib.parse
    try:
        if '#' in url:
            fragment = url.split('#')[1]
            params = urllib.parse.parse_qs(fragment)
            
            if 'access_token' in params:
                access_token = params['access_token'][0]
                expires_in = params.get('expires_in', ['N/A'])[0]
                
                print(f"\n✅ 访问令牌提取成功")
                print(f"过期时间: {expires_in} 秒")
                
                # 更新.env文件
                env_file = ".env"
                if os.path.exists(env_file):
                    with open(env_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    updated = False
                    new_lines = []
                    for line in lines:
                        if line.startswith("FACEBOOK_ACCESS_TOKEN="):
                            new_lines.append(f"FACEBOOK_ACCESS_TOKEN={access_token}\n")
                            updated = True
                        else:
                            new_lines.append(line)
                    
                    if not updated:
                        new_lines.append(f"FACEBOOK_ACCESS_TOKEN={access_token}\n")
                    
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    
                    print(f"✅ 已更新到 .env 文件")
                    
                    # 提示交换长期令牌
                    if isinstance(expires_in, str) and expires_in.isdigit():
                        days = int(expires_in) // 86400
                        if days < 30:
                            print(f"\n⚠️  这是短期令牌（{days}天）")
                            print("建议运行 python exchange_token.py 交换长期令牌（60天）")
                    
                    return True
                else:
                    print("⚠️  .env文件不存在，请手动添加:")
                    print(f"FACEBOOK_ACCESS_TOKEN={access_token}")
                    return False
            else:
                print("❌ URL中未找到access_token")
                return False
        else:
            print("❌ URL格式不正确，应包含#access_token")
            return False
    except Exception as e:
        print(f"❌ 提取失败: {str(e)}")
        return False


def verify_permissions():
    """验证权限配置"""
    print("\n" + "=" * 60)
    print("步骤5：验证权限配置")
    print("=" * 60)
    
    result, missing = check_current_permissions()
    
    if result:
        print("\n" + "=" * 60)
        print("✅ 所有权限已成功配置！")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠️  仍有权限缺失:")
        for perm in missing:
            print(f"  - {perm}")
        print("\n请重新运行授权流程")
        print("=" * 60)
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Facebook权限配置自动化工具")
    print("=" * 60)
    
    # 步骤1：检查当前权限
    all_granted, missing = check_current_permissions()
    
    if all_granted:
        print("\n" + "=" * 60)
        print("✅ 所有权限已授予，无需配置！")
        print("=" * 60)
        return 0
    
    if missing:
        print(f"\n缺失 {len(missing)} 个权限，需要重新授权")
    
    # 步骤2：生成授权URL
    auth_url = generate_oauth_url()
    if not auth_url:
        return 1
    
    # 步骤3：打开浏览器
    opened = open_browser(auth_url)
    
    if not opened:
        print("\n请手动复制URL并在浏览器中打开")
    
    # 步骤4：提取并更新令牌
    print("\n" + "=" * 60)
    print("等待授权完成...")
    print("=" * 60)
    print("\n授权完成后，请:")
    print("1. 从浏览器地址栏复制重定向URL")
    print("2. 粘贴到下面的提示中")
    
    token_updated = extract_and_update_token()
    
    if not token_updated:
        print("\n⚠️  令牌未更新，请手动更新.env文件")
        print("然后运行: python check_facebook_permissions.py")
        return 1
    
    # 步骤5：验证权限
    print("\n等待3秒后验证权限...")
    import time
    time.sleep(3)
    
    verified = verify_permissions()
    
    if verified:
        print("\n🎉 权限配置完成！")
        print("\n您现在可以使用:")
        print("  - 帖子管理功能（发布、删除帖子）")
        print("  - 广告管理功能（创建、更新、删除广告）")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)







