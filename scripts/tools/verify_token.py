"""验证Facebook Token类型和权限"""
import sys
import asyncio
import httpx
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.config import settings

load_dotenv()


async def verify_token():
    """验证Token类型和权限"""
    token = settings.facebook_access_token
    
    if not token:
        print("❌ 错误: FACEBOOK_ACCESS_TOKEN 未配置")
        return
    
    print("=" * 70)
    print("验证Facebook Token类型和权限")
    print("=" * 70)
    print()
    print(f"Token: {token[:20]}...{token[-10:]}")
    print()
    
    # 1. 检查Token信息（使用debug_token端点）
    print("1. 检查Token信息...")
    try:
        url = "https://graph.facebook.com/v18.0/debug_token"
        params = {
            "input_token": token,
            "access_token": settings.facebook_app_id + "|" + settings.facebook_app_secret
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                token_type = data.get("type", "未知")
                app_id = data.get("app_id")
                user_id = data.get("user_id")
                expires_at = data.get("expires_at", 0)
                
                print(f"   ✅ Token有效")
                print(f"   Token类型: {token_type}")
                print(f"   应用ID: {app_id}")
                if user_id:
                    print(f"   用户ID: {user_id}")
                if expires_at:
                    from datetime import datetime
                    exp_time = datetime.fromtimestamp(expires_at)
                    print(f"   过期时间: {exp_time}")
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "未知错误")
                print(f"   ⚠️  无法验证Token详细信息: {error_msg}")
                print(f"   （这可能是正常的，继续检查页面列表...）")
    except Exception as e:
        print(f"   ⚠️  检查Token失败: {str(e)}")
        print(f"   （继续检查页面列表...）")
    
    print()
    
    # 2. 检查Token权限
    print("2. 检查Token权限...")
    try:
        url = "https://graph.facebook.com/v18.0/me/permissions"
        params = {"access_token": token}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                permissions = data.get("data", [])
                
                # 检查关键权限
                required_permissions = ["pages_show_list", "pages_messaging", "pages_read_engagement"]
                has_pages_show_list = False
                has_pages_messaging = False
                
                print("   已授予的权限:")
                for perm in permissions:
                    perm_name = perm.get("permission")
                    status = perm.get("status")
                    if status == "granted":
                        print(f"     ✅ {perm_name}")
                        if perm_name == "pages_show_list":
                            has_pages_show_list = True
                        if perm_name == "pages_messaging":
                            has_pages_messaging = True
                    else:
                        print(f"     ❌ {perm_name} ({status})")
                
                print()
                if has_pages_show_list:
                    print("   ✅ 具有 pages_show_list 权限（可以同步所有页面）")
                else:
                    print("   ❌ 缺少 pages_show_list 权限（无法同步所有页面）")
                    print("   ⚠️  这是一个页面级Token，不是用户级Token")
                
                if has_pages_messaging:
                    print("   ✅ 具有 pages_messaging 权限（可以发送消息）")
                else:
                    print("   ❌ 缺少 pages_messaging 权限（无法发送消息）")
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "未知错误")
                print(f"   ❌ 检查权限失败: {error_msg}")
    except Exception as e:
        print(f"   ❌ 检查权限失败: {str(e)}")
    
    print()
    
    # 3. 尝试获取页面列表（验证pages_show_list权限）
    print("3. 测试获取页面列表...")
    try:
        url = "https://graph.facebook.com/v18.0/me/accounts"
        params = {"access_token": token}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get("data", [])
                count = len(pages)
                
                print(f"   ✅ 成功获取页面列表")
                print(f"   找到 {count} 个页面:")
                for i, page in enumerate(pages[:10], 1):  # 只显示前10个
                    page_id = page.get("id")
                    page_name = page.get("name", "未知")
                    print(f"     {i}. {page_name} (ID: {page_id})")
                
                if count > 10:
                    print(f"     ... 还有 {count - 10} 个页面")
                
                print()
                if count > 0:
                    print("   ✅ 这是用户级Token，可以管理多个页面")
                else:
                    print("   ⚠️  这是用户级Token，但当前没有管理的页面")
            else:
                error_data = response.json()
                error_code = error_data.get("error", {}).get("code")
                error_msg = error_data.get("error", {}).get("message", "未知错误")
                
                if error_code == 200:
                    print("   ❌ 需要 pages_show_list 权限")
                elif error_code == 190:
                    print("   ❌ Token已过期或无效")
                else:
                    print(f"   ❌ 获取页面列表失败: {error_msg} (错误码: {error_code})")
                
                print()
                print("   ⚠️  这可能是页面级Token，不是用户级Token")
                print("   ⚠️  页面级Token只能管理单个页面，无法同步所有页面")
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
    
    print()
    print("=" * 70)
    print()
    print("总结:")
    print("- 如果看到'可以管理多个页面'，说明Token配置正确 ✅")
    print("- 如果看到'页面级Token'，需要更换为用户级Token ⚠️")
    print()


if __name__ == "__main__":
    asyncio.run(verify_token())

