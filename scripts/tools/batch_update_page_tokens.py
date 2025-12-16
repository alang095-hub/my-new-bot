"""批量更新页面Token"""
from src.config import settings
from scripts.tools.convert_to_long_lived_token import exchange_for_long_lived_token, get_page_tokens_from_user_token
import asyncio
from src.config.page_token_manager import page_token_manager
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def batch_update_tokens():
    """批量更新Token"""
    print("=" * 70)
    print("批量更新页面Token")
    print("=" * 70)
    print()

    # 用户提供的Token列表
    # ⚠️ 警告：请替换为您的真实Token，不要提交真实Token到Git
    tokens = [
        "YOUR_FACEBOOK_ACCESS_TOKEN_1_HERE",
        "YOUR_FACEBOOK_ACCESS_TOKEN_2_HERE",
        "YOUR_FACEBOOK_ACCESS_TOKEN_3_HERE"
    ]

    print(f"收到 {len(tokens)} 个Token")
    print()

    # 尝试获取App ID和Secret
    try:
        app_id = settings.facebook_app_id
        app_secret = settings.facebook_app_secret
    except Exception:
        app_id = None
        app_secret = None

    # 首先尝试使用第一个Token作为用户Token获取所有页面
    print("尝试使用第一个Token作为用户Token获取所有页面...")
    print()

    user_token = tokens[0]

    # 如果配置了App ID和Secret，尝试转换为长期Token
    expires_at_str = None
    if app_id and app_secret:
        print("转换Token为长期Token...")
        long_token, expires_at_str = await exchange_for_long_lived_token(user_token, app_id, app_secret)
        if long_token:
            user_token = long_token
            print("✅ Token已转换为长期Token")
        else:
            print("⚠️  无法转换Token，将直接使用")
        print()

    # 尝试获取页面Token
    print("获取页面Token...")
    page_tokens = await get_page_tokens_from_user_token(user_token)

    if page_tokens:
        print(f"✅ 成功获取 {len(page_tokens)} 个页面Token")
        print()

        # 更新所有页面Token
        print("更新页面Token...")
        for page_id, page_info in page_tokens.items():
            page_token = page_info["token"]
            page_name = page_info["name"]

            page_token_manager.set_token(
                page_id, page_token, page_name, expires_at=expires_at_str)
            print(f"✅ 已更新页面 {page_id} ({page_name}) 的Token")

        print()
        print("=" * 70)
        print("✅ 所有页面Token已更新")
        print("=" * 70)
    else:
        print("⚠️  无法自动获取页面Token")
        print()
        print("将使用提供的Token直接更新已知页面...")
        print()

        # 获取已知的页面列表
        known_pages = {
            "474610872412780": "Iphone Loan Ph 9",
            "732287003311432": "页面 732287003311432",
            "849418138246708": "页面 849418138246708"
        }

        # 如果Token数量匹配，直接分配
        if len(tokens) >= len(known_pages):
            print("直接更新页面Token...")
            page_ids = list(known_pages.keys())
            for i, token in enumerate(tokens[:len(known_pages)]):
                page_id = page_ids[i]
                page_name = known_pages[page_id]

                # 尝试转换为长期Token
                if app_id and app_secret:
                    long_token, expires_at_str = await exchange_for_long_lived_token(token, app_id, app_secret)
                    if long_token:
                        token = long_token

                page_token_manager.set_token(
                    page_id, token, page_name, expires_at=expires_at_str)
                print(f"✅ 已更新页面 {page_id} ({page_name}) 的Token")

            print()
            print("=" * 70)
            print("✅ 所有页面Token已更新")
            print("=" * 70)
        else:
            print("❌ Token数量不匹配")
            print(f"   需要 {len(known_pages)} 个Token，但只提供了 {len(tokens)} 个")
            print()
            print("请手动指定每个Token对应的页面：")
            print(
                "  python scripts/tools/quick_update_page_token.py <页面ID> <Token> [页面名称]")

if __name__ == "__main__":
    asyncio.run(batch_update_tokens())
