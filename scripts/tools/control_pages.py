"""
交互式页面控制工具 - 可以选择要操作的页面
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.config import settings
from src.config.page_token_manager import page_token_manager
from src.config.page_settings import page_settings

load_dotenv()


def show_pages_menu(pages: Dict) -> None:
    """显示页面选择菜单"""
    print("\n" + "=" * 70)
    print("页面列表")
    print("=" * 70)
    print()
    print(f"{'序号':<6} {'页面名称':<30} {'页面ID':<20} {'状态':<10}")
    print("-" * 70)
    
    page_list = []
    for idx, (page_id, info) in enumerate(pages.items(), 1):
        page_name = info.get("name", "未知")
        is_enabled = page_settings.is_auto_reply_enabled(page_id)
        status = "✅ 启用" if is_enabled else "❌ 禁用"
        
        # 截断长名称
        display_name = page_name[:28] + ".." if len(page_name) > 30 else page_name
        print(f"{idx:<6} {display_name:<30} {page_id:<20} {status:<10}")
        page_list.append((page_id, page_name, is_enabled))
    
    print()
    print("=" * 70)
    return page_list


def get_selected_pages(page_list: List) -> List[str]:
    """获取用户选择的页面ID列表"""
    print("\n请选择要操作的页面：")
    print("  - 输入序号（如：1）选择单个页面")
    print("  - 输入多个序号，用逗号分隔（如：1,3,5）选择多个页面")
    print("  - 输入 'all' 选择所有页面")
    print("  - 输入 'enabled' 选择所有已启用的页面")
    print("  - 输入 'disabled' 选择所有已禁用的页面")
    print("  - 输入 'q' 退出")
    print()
    
    choice = input("请输入选择: ").strip().lower()
    
    if choice == 'q':
        return []
    
    if choice == 'all':
        return [page_id for page_id, _, _ in page_list]
    
    if choice == 'enabled':
        return [page_id for page_id, _, enabled in page_list if enabled]
    
    if choice == 'disabled':
        return [page_id for page_id, _, enabled in page_list if not enabled]
    
    # 解析多个序号
    try:
        indices = [int(x.strip()) for x in choice.split(',')]
        selected = []
        for idx in indices:
            if 1 <= idx <= len(page_list):
                selected.append(page_list[idx - 1][0])
            else:
                print(f"⚠️  序号 {idx} 无效，跳过")
        return selected
    except ValueError:
        print("❌ 输入格式错误，请重新输入")
        return get_selected_pages(page_list)


async def enable_selected_pages(page_ids: List[str], pages: Dict) -> None:
    """启用选中的页面"""
    print("\n" + "=" * 70)
    print("启用页面自动回复")
    print("=" * 70)
    print()
    
    if not page_ids:
        print("⚠️  未选择任何页面")
        return
    
    enabled_count = 0
    for page_id in page_ids:
        if page_id in pages:
            page_name = pages[page_id].get("name", "未知")
            if not page_settings.is_auto_reply_enabled(page_id):
                page_settings.add_page(page_id, auto_reply_enabled=True, name=page_name)
                print(f"✅ 已启用: {page_name} (ID: {page_id})")
                enabled_count += 1
            else:
                print(f"ℹ️  已启用: {page_name} (ID: {page_id})")
    
    print()
    if enabled_count > 0:
        print(f"✅ 成功启用 {enabled_count} 个页面的自动回复")
    else:
        print("ℹ️  所有选中的页面已经启用自动回复")
    
    print()
    print("=" * 70)


async def disable_selected_pages(page_ids: List[str], pages: Dict) -> None:
    """禁用选中的页面"""
    print("\n" + "=" * 70)
    print("禁用页面自动回复")
    print("=" * 70)
    print()
    
    if not page_ids:
        print("⚠️  未选择任何页面")
        return
    
    disabled_count = 0
    for page_id in page_ids:
        if page_id in pages:
            page_name = pages[page_id].get("name", "未知")
            if page_settings.is_auto_reply_enabled(page_id):
                page_settings.add_page(page_id, auto_reply_enabled=False, name=page_name)
                print(f"✅ 已禁用: {page_name} (ID: {page_id})")
                disabled_count += 1
            else:
                print(f"ℹ️  已禁用: {page_name} (ID: {page_id})")
    
    print()
    if disabled_count > 0:
        print(f"✅ 成功禁用 {disabled_count} 个页面的自动回复")
    else:
        print("ℹ️  所有选中的页面已经禁用自动回复")
    
    print()
    print("=" * 70)


async def toggle_selected_pages(page_ids: List[str], pages: Dict) -> None:
    """切换选中页面的状态（启用变禁用，禁用变启用）"""
    print("\n" + "=" * 70)
    print("切换页面自动回复状态")
    print("=" * 70)
    print()
    
    if not page_ids:
        print("⚠️  未选择任何页面")
        return
    
    toggled_count = 0
    for page_id in page_ids:
        if page_id in pages:
            page_name = pages[page_id].get("name", "未知")
            current_status = page_settings.is_auto_reply_enabled(page_id)
            new_status = not current_status
            
            page_settings.add_page(page_id, auto_reply_enabled=new_status, name=page_name)
            status_text = "启用" if new_status else "禁用"
            print(f"✅ 已{status_text}: {page_name} (ID: {page_id})")
            toggled_count += 1
    
    print()
    print(f"✅ 成功切换 {toggled_count} 个页面的状态")
    print()
    print("=" * 70)


async def main():
    """主函数"""
    print("=" * 70)
    print("交互式页面控制工具")
    print("=" * 70)
    print()
    
    # 获取所有页面
    pages = page_token_manager.list_pages()
    
    if not pages:
        print("⚠️  未找到任何页面")
        print()
        print("💡 请先运行同步命令:")
        print("   python scripts/tools/manage_pages.py sync")
        print()
        return
    
    while True:
        # 显示页面列表
        page_list = show_pages_menu(pages)
        
        # 显示操作菜单
        print("\n请选择操作：")
        print("  [1] 启用选中的页面")
        print("  [2] 禁用选中的页面")
        print("  [3] 切换选中页面的状态（启用↔禁用）")
        print("  [4] 刷新页面列表")
        print("  [0] 退出")
        print()
        
        action = input("请输入操作 (0-4): ").strip()
        
        if action == '0':
            print("\n再见！")
            break
        elif action == '1':
            selected = get_selected_pages(page_list)
            if selected:
                await enable_selected_pages(selected, pages)
                input("\n按回车键继续...")
        elif action == '2':
            selected = get_selected_pages(page_list)
            if selected:
                await disable_selected_pages(selected, pages)
                input("\n按回车键继续...")
        elif action == '3':
            selected = get_selected_pages(page_list)
            if selected:
                await toggle_selected_pages(selected, pages)
                input("\n按回车键继续...")
        elif action == '4':
            # 刷新页面列表
            pages = page_token_manager.list_pages()
            print("\n✅ 页面列表已刷新")
            input("\n按回车键继续...")
        else:
            print("\n❌ 无效的操作，请重新选择")
            input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

