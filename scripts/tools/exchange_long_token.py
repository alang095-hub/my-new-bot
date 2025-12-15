"""将Facebook短期Token转换为长期Token（60天有效期）"""
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


async def exchange_long_token(short_token: str = None):
    """将短期Token转换为长期Token"""
    
    if not short_token:
        short_token = settings.facebook_access_token
    
    if not short_token:
        print("❌ 错误: 未提供Token")
        print("使用方法: python scripts/tools/exchange_long_token.py [TOKEN]")
        return
    
    app_id = settings.facebook_app_id
    app_secret = settings.facebook_app_secret
    
    if not app_id or not app_secret:
        print("❌ 错误: FACEBOOK_APP_ID 或 FACEBOOK_APP_SECRET 未配置")
        return
    
    print("=" * 70)
    print("将短期Token转换为长期Token（60天有效期）")
    print("=" * 70)
    print()
    print(f"应用ID: {app_id}")
    print(f"短期Token: {short_token[:20]}...{short_token[-10:]}")
    print()
    
    # 转换Token
    print("正在转换Token...")
    try:
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                long_token = data.get("access_token")
                expires_in = data.get("expires_in", 0)  # 秒数
                
                if long_token:
                    # 计算过期时间
                    from datetime import datetime, timedelta, timezone
                    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                    days = expires_in // 86400  # 转换为天数
                    
                    print("✅ Token转换成功！")
                    print()
                    print("=" * 70)
                    print("长期Token（请复制保存）:")
                    print("=" * 70)
                    print()
                    print(long_token)
                    print()
                    print("=" * 70)
                    print()
                    print(f"有效期: {days} 天")
                    print(f"过期时间: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    print()
                    print("=" * 70)
                    print()
                    print("⚠️  重要提示:")
                    print("1. 请立即复制上面的Token")
                    print("2. 在Zeabur中更新 FACEBOOK_ACCESS_TOKEN 环境变量")
                    print("3. 运行同步脚本: python scripts/tools/manage_pages.py sync")
                    print()
                    
                    # 验证新Token
                    print("验证新Token...")
                    try:
                        verify_url = "https://graph.facebook.com/v18.0/debug_token"
                        verify_params = {
                            "input_token": long_token,
                            "access_token": f"{app_id}|{app_secret}"
                        }
                        verify_response = await client.get(verify_url, params=verify_params)
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json().get("data", {})
                            token_type = verify_data.get("type", "未知")
                            print(f"✅ Token验证成功")
                            print(f"   Token类型: {token_type}")
                            
                            # 测试获取页面列表
                            if token_type == "USER":
                                pages_url = "https://graph.facebook.com/v18.0/me/accounts"
                                pages_params = {"access_token": long_token}
                                pages_response = await client.get(pages_url, params=pages_params)
                                
                                if pages_response.status_code == 200:
                                    pages_data = pages_response.json()
                                    pages_count = len(pages_data.get("data", []))
                                    print(f"   ✅ 可以管理 {pages_count} 个页面")
                                else:
                                    print(f"   ⚠️  无法获取页面列表（可能需要权限）")
                        else:
                            print("   ⚠️  Token验证失败，但Token已生成")
                    except Exception as e:
                        print(f"   ⚠️  验证Token时出错: {str(e)}")
                    
                    print()
                    print("=" * 70)
                    
                else:
                    print("❌ 转换失败: 响应中未找到access_token")
                    print(f"响应: {data}")
            else:
                error_data = response.json()
                error_code = error_data.get("error", {}).get("code")
                error_msg = error_data.get("error", {}).get("message", "未知错误")
                
                print(f"❌ Token转换失败")
                print(f"错误码: {error_code}")
                print(f"错误信息: {error_msg}")
                print()
                
                if error_code == 190:
                    print("可能的原因:")
                    print("- Token已过期")
                    print("- Token无效")
                    print("- 需要重新获取Token")
                elif error_code == 100:
                    print("可能的原因:")
                    print("- App ID 或 App Secret 不正确")
                    print("- Token不属于此应用")
                
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 支持从命令行参数获取Token
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1]
    
    asyncio.run(exchange_long_token(token))




