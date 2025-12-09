"""生成包含所有权限的Facebook OAuth授权URL"""
import urllib.parse
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def generate_full_permissions_url():
    """生成包含所有权限的OAuth URL"""
    print("=" * 60)
    print("生成包含所有权限的Facebook OAuth授权URL")
    print("=" * 60)
    
    try:
        from src.config import settings
        app_id = settings.facebook_app_id
        print(f"\n使用App ID: {app_id}")
    except Exception as e:
        print(f"\n⚠️  无法从配置读取App ID: {str(e)}")
        app_id = input("请输入Facebook App ID: ").strip()
        if not app_id:
            print("❌ App ID不能为空")
            return None
    
    redirect_uri = "http://localhost:8000/oauth/callback"
    
    # 完整权限列表
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
    
    print("\n" + "=" * 60)
    print("生成的授权URL（包含所有权限）")
    print("=" * 60)
    print(f"\n{auth_url}\n")
    print("=" * 60)
    
    print("\n包含的权限:")
    print("  ✅ pages_messaging - 发送和接收消息")
    print("  ✅ pages_read_engagement - 读取页面互动数据")
    print("  ✅ pages_manage_metadata - 管理页面元数据")
    print("  ✅ pages_manage_posts - 管理页面帖子（发布、删除）")
    print("  ✅ ads_read - 读取广告数据")
    print("  ✅ ads_management - 管理广告（创建、更新、删除）")
    
    print("\n" + "=" * 60)
    print("下一步操作")
    print("=" * 60)
    print("\n1. 复制上面的URL")
    print("2. 在浏览器中打开")
    print("3. 登录您的Facebook账号")
    print("4. 授权所有请求的权限")
    print("5. 从重定向URL中提取access_token")
    print("   重定向URL格式: http://localhost:8000/oauth/callback#access_token=...")
    print("\n6. 更新.env文件中的FACEBOOK_ACCESS_TOKEN")
    print("7. 运行 python check_facebook_permissions.py 验证权限")
    
    # 尝试自动打开浏览器
    try:
        import webbrowser
        print("\n是否在浏览器中打开授权URL？(y/n): ", end="")
        if sys.stdin.isatty():
            choice = input().strip().lower()
            if choice == 'y' or choice == 'yes' or choice == '':
                print("正在打开浏览器...")
                webbrowser.open(auth_url)
        else:
            print("\n(非交互模式，跳过自动打开浏览器)")
    except Exception:
        pass
    
    return auth_url


if __name__ == "__main__":
    url = generate_full_permissions_url()
    if url:
        print("\n✅ URL生成成功！")
    else:
        print("\n❌ URL生成失败")
        sys.exit(1)







