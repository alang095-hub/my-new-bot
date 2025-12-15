"""统一的页面管理工具 - 整合Token管理和自动回复开关"""
import os
import sys
import asyncio
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.config import settings
from src.config.page_token_manager import page_token_manager
from src.config.page_settings import page_settings

load_dotenv()


async def sync_all_pages(user_token: Optional[str] = None):
    """从用户Token同步所有页面的Token，并自动启用自动回复"""
    if not user_token:
        user_token = settings.facebook_access_token
    
    print("=" * 70)
    print("同步所有页面Token和设置")
    print("=" * 70)
    print()
    
    print(f"使用Token: {user_token[:20]}...")
    print()
    
    count = await page_token_manager.sync_from_user_token(user_token)
    
    if count > 0:
        print(f"✅ 成功同步 {count} 个页面的Token")
        print()
        
        # 自动为所有同步的页面启用自动回复
        pages = page_token_manager.list_pages()
        enabled_count = 0
        for page_id, info in pages.items():
            page_name = info.get("name", "未知")
            # 如果页面设置中还没有配置，则添加并启用
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
        print("❌ 同步失败，请检查Token权限")
    
    print()
    print("=" * 70)


async def add_page(page_id: str, token: str, page_name: Optional[str] = None, auto_reply: bool = True):
    """添加新页面（配置Token和自动回复设置）"""
    print("=" * 70)
    print("添加新页面")
    print("=" * 70)
    print()
    
    # 配置Token
    page_token_manager.set_token(page_id, token, page_name)
    print(f"✅ 已配置页面 {page_id} 的Token")
    
    # 配置自动回复
    page_settings.add_page(page_id, auto_reply_enabled=auto_reply, name=page_name)
    status = "启用" if auto_reply else "禁用"
    print(f"✅ 已{status}页面 {page_id} 的自动回复")
    
    if page_name:
        print(f"   页面名称: {page_name}")
    
    print()
    print("=" * 70)


async def enable_auto_reply(page_id: str):
    """启用指定页面的自动回复"""
    print("=" * 70)
    print(f"启用页面 {page_id} 的自动回复")
    print("=" * 70)
    print()
    
    page_config = page_settings.get_page_config(page_id)
    page_name = page_config.get("name", "未知")
    
    page_settings.add_page(page_id, auto_reply_enabled=True, name=page_name)
    print(f"✅ 已启用页面 {page_id} ({page_name}) 的自动回复")
    
    print()
    print("=" * 70)


async def disable_auto_reply(page_id: str):
    """禁用指定页面的自动回复"""
    print("=" * 70)
    print(f"禁用页面 {page_id} 的自动回复")
    print("=" * 70)
    print()
    
    page_config = page_settings.get_page_config(page_id)
    page_name = page_config.get("name", "未知")
    
    page_settings.add_page(page_id, auto_reply_enabled=False, name=page_name)
    print(f"✅ 已禁用页面 {page_id} ({page_name}) 的自动回复")
    
    print()
    print("=" * 70)


async def show_status():
    """显示所有页面的状态"""
    print("=" * 70)
    print("页面状态总览")
    print("=" * 70)
    print()
    
    tokens = page_token_manager._tokens
    pages = page_token_manager.list_pages()
    
    # 显示默认Token状态
    if "default" in tokens:
        print("📄 默认Token: ✅ 已配置")
        print()
    
    if not pages and "default" not in tokens:
        print("⚠️  未配置任何页面")
        print()
        print("💡 运行以下命令同步所有页面:")
        print("   python scripts/tools/manage_pages.py sync")
    else:
        if pages:
            print(f"📋 已配置 {len(pages)} 个页面:")
            print()
            print(f"{'页面名称':<30} {'页面ID':<20} {'Token':<8} {'自动回复':<10}")
            print("-" * 70)
            
            for page_id, info in pages.items():
                page_name = info.get("name", "未知")
                has_token = "✅" if page_id in tokens else "❌"
                auto_reply_status = "✅ 启用" if page_settings.is_auto_reply_enabled(page_id) else "❌ 禁用"
                
                # 截断长名称
                display_name = page_name[:28] + ".." if len(page_name) > 30 else page_name
                print(f"{display_name:<30} {page_id:<20} {has_token:<8} {auto_reply_status:<10}")
        else:
            print("📋 未配置特定页面Token（使用默认Token）")
    
    print()
    print("=" * 70)


async def enable_all_pages():
    """启用所有页面的自动回复"""
    print("=" * 70)
    print("启用所有页面的自动回复")
    print("=" * 70)
    print()
    
    pages = page_token_manager.list_pages()
    
    if not pages:
        print("⚠️  未找到任何页面")
        print()
        print("💡 请先运行同步命令:")
        print("   python scripts/tools/manage_pages.py sync")
        print()
        print("=" * 70)
        return
    
    enabled_count = 0
    for page_id, info in pages.items():
        page_name = info.get("name", "未知")
        if not page_settings.is_auto_reply_enabled(page_id):
            page_settings.add_page(page_id, auto_reply_enabled=True, name=page_name)
            enabled_count += 1
            print(f"✅ 已启用: {page_name} (ID: {page_id})")
        else:
            print(f"ℹ️  已启用: {page_name} (ID: {page_id})")
    
    print()
    if enabled_count > 0:
        print(f"✅ 成功启用 {enabled_count} 个页面的自动回复")
    else:
        print("ℹ️  所有页面已经启用自动回复")
    
    print()
    print("=" * 70)


async def disable_all_pages():
    """禁用所有页面的自动回复"""
    print("=" * 70)
    print("禁用所有页面的自动回复")
    print("=" * 70)
    print()
    
    pages = page_token_manager.list_pages()
    
    if not pages:
        print("⚠️  未找到任何页面")
        print()
        print("=" * 70)
        return
    
    disabled_count = 0
    for page_id, info in pages.items():
        page_name = info.get("name", "未知")
        if page_settings.is_auto_reply_enabled(page_id):
            page_settings.add_page(page_id, auto_reply_enabled=False, name=page_name)
            disabled_count += 1
            print(f"✅ 已禁用: {page_name} (ID: {page_id})")
        else:
            print(f"ℹ️  已禁用: {page_name} (ID: {page_id})")
    
    print()
    if disabled_count > 0:
        print(f"✅ 成功禁用 {disabled_count} 个页面的自动回复")
    else:
        print("ℹ️  所有页面已经禁用自动回复")
    
    print()
    print("=" * 70)


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("页面管理工具 - 统一管理Token和自动回复")
        print("=" * 70)
        print()
        print("用法:")
        print()
        print("  添加新页面（自动启用自动回复）:")
        print("    python manage_pages.py add <page_id> <token> [page_name]")
        print()
        print("  启用页面自动回复:")
        print("    python manage_pages.py enable <page_id>")
        print()
        print("  禁用页面自动回复:")
        print("    python manage_pages.py disable <page_id>")
        print()
        print("  启用所有页面:")
        print("    python manage_pages.py enable-all")
        print()
        print("  禁用所有页面:")
        print("    python manage_pages.py disable-all")
        print()
        print("  查看所有页面状态:")
        print("    python manage_pages.py status")
        print()
        print("  同步所有页面Token（从用户Token）:")
        print("    python manage_pages.py sync")
        print()
        print("=" * 70)
        return
    
    command = sys.argv[1].lower()
    
    if command == "sync":
        await sync_all_pages()
    elif command == "status":
        await show_status()
    elif command == "enable-all":
        await enable_all_pages()
    elif command == "disable-all":
        await disable_all_pages()
    elif command == "add":
        if len(sys.argv) < 4:
            print("❌ 用法: python manage_pages.py add <page_id> <token> [page_name]")
            print()
            print("示例:")
            print("  python manage_pages.py add 123456789 \"EAAB...\" \"我的页面\"")
            return
        page_id = sys.argv[2]
        token = sys.argv[3]
        page_name = sys.argv[4] if len(sys.argv) > 4 else None
        await add_page(page_id, token, page_name, auto_reply=True)
    elif command == "enable":
        if len(sys.argv) < 3:
            print("❌ 用法: python manage_pages.py enable <page_id>")
            return
        page_id = sys.argv[2]
        await enable_auto_reply(page_id)
    elif command == "disable":
        if len(sys.argv) < 3:
            print("❌ 用法: python manage_pages.py disable <page_id>")
            return
        page_id = sys.argv[2]
        await disable_auto_reply(page_id)
    else:
        print(f"❌ 未知命令: {command}")
        print()
        print("💡 运行不带参数的命令查看帮助")


if __name__ == "__main__":
    asyncio.run(main())

