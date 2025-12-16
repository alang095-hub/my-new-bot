"""
同步所有Facebook页面（支持分页，获取所有页面）
"""
import os
import sys
import asyncio
import httpx
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.config import settings
from src.config.page_token_manager import page_token_manager
from src.config.page_settings import page_settings
from src.core.config.constants import FACEBOOK_ME_ACCOUNTS_URL

load_dotenv()


async def sync_all_pages_with_pagination(user_token: Optional[str] = None) -> int:
    """
    从用户Token同步所有页面的Token（支持分页，获取所有页面）
    
    Args:
        user_token: 用户级别的Token，如果为None则从环境变量读取
        
    Returns:
        同步的页面数量
    """
    if not user_token:
        user_token = settings.facebook_access_token
    
    if not user_token:
        print("❌ 错误：未找到FACEBOOK_ACCESS_TOKEN")
        print("请在环境变量中配置FACEBOOK_ACCESS_TOKEN")
        return 0
    
    print("=" * 70)
    print("同步所有页面Token（支持分页）")
    print("=" * 70)
    print()
    print(f"使用Token: {user_token[:20]}...")
    print()
    
    all_pages = []
    url = FACEBOOK_ME_ACCOUNTS_URL
    params = {"access_token": user_token, "limit": 100}  # 每页最多100个
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            page_count = 0
            
            while url:
                print(f"正在获取第 {page_count + 1} 页...")
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    pages = data.get("data", [])
                    all_pages.extend(pages)
                    page_count += 1
                    print(f"  获取到 {len(pages)} 个页面（累计: {len(all_pages)} 个）")
                    
                    # 检查是否有下一页
                    paging = data.get("paging", {})
                    if "next" in paging:
                        url = paging["next"]
                        params = {}  # 下一页URL已经包含所有参数
                    else:
                        url = None
                else:
                    print(f"❌ 获取页面列表失败: HTTP {response.status_code}")
                    print(f"   响应: {response.text[:200]}")
                    break
            
            print()
            print(f"✅ 总共获取到 {len(all_pages)} 个页面")
            print()
            
            # 保存所有页面
            count = 0
            for page in all_pages:
                page_id = page.get("id")
                page_token = page.get("access_token")
                page_name = page.get("name")
                
                if page_id and page_token:
                    page_token_manager.set_token(page_id, page_token, page_name)
                    count += 1
            
            if count > 0:
                print(f"✅ 成功同步 {count} 个页面的Token")
                print()
                
                # 自动为所有同步的页面启用自动回复
                pages = page_token_manager.list_pages()
                enabled_count = 0
                for page_id, info in pages.items():
                    page_name = info.get("name", "未知")
                    if not page_settings.get_page_config(page_id).get("auto_reply_enabled"):
                        page_settings.add_page(page_id, auto_reply_enabled=True, name=page_name)
                        enabled_count += 1
                
                print("已配置的页面:")
                for page_id, info in pages.items():
                    page_name = info.get("name", "未知")
                    auto_reply_status = "✅ 启用" if page_settings.is_auto_reply_enabled(page_id) else "❌ 禁用"
                    print(f"  - {page_name} (ID: {page_id}) - {auto_reply_status}")
                
                if enabled_count > 0:
                    print()
                    print(f"✅ 已自动启用 {enabled_count} 个页面的自动回复")
            else:
                print("❌ 同步失败，未找到任何有效页面")
            
            print()
            print("=" * 70)
            return count
            
    except Exception as e:
        print(f"❌ 同步失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        print("=" * 70)
        return 0


async def main():
    """主函数"""
    count = await sync_all_pages_with_pagination()
    
    if count == 0:
        print()
        print("💡 提示：")
        print("1. 确认FACEBOOK_ACCESS_TOKEN已配置")
        print("2. 确认Token有pages_show_list权限")
        print("3. 确认Token是用户级Token（不是页面Token）")
        sys.exit(1)
    else:
        print()
        print(f"🎉 同步完成！共同步 {count} 个页面")
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

