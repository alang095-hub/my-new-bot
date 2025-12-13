"""诊断页面Token在API调用中的实际有效性"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import httpx
from src.config.page_token_manager import page_token_manager
from src.config.page_settings import page_settings

async def test_conversations_endpoint(page_id: str, token: str) -> dict:
    """测试conversations端点是否可用"""
    result = {
        "page_id": page_id,
        "endpoint_works": False,
        "error": None,
        "conversation_count": 0
    }
    
    try:
        url = f"https://graph.facebook.com/v18.0/{page_id}/conversations"
        params = {
            "access_token": token,
            "fields": "id,updated_time,message_count,unread_count",
            "limit": 5  # 只获取5个，用于测试
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                conversations = data.get("data", [])
                result["endpoint_works"] = True
                result["conversation_count"] = len(conversations)
            elif response.status_code == 400:
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get("error", {})
                    error_message = error_msg.get("message", "Bad Request")
                    error_code = error_msg.get("code")
                    result["error"] = f"{error_message} (code: {error_code})"
                except:
                    result["error"] = f"HTTP 400: {response.text[:200]}"
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                
    except Exception as e:
        result["error"] = f"Exception: {str(e)}"
    
    return result

async def diagnose_all_pages_api():
    """诊断所有页面的API端点可用性"""
    print("=" * 70)
    print("页面Token API端点诊断工具")
    print("=" * 70)
    print()
    print("此工具直接测试 /conversations 端点，比Token验证更准确")
    print()
    
    pages = page_token_manager.list_pages()
    
    if not pages:
        print("❌ 没有配置任何页面")
        return
    
    print(f"找到 {len(pages)} 个配置的页面")
    print()
    
    results = []
    
    for page_id, page_info in pages.items():
        if page_id == "default":
            continue
        
        token = page_token_manager.get_token(page_id)
        page_name = page_info.get("name", "未知")
        auto_reply_enabled = page_settings.is_auto_reply_enabled(page_id)
        
        print(f"测试页面: {page_name} (ID: {page_id})")
        print(f"自动回复: {'✅ 启用' if auto_reply_enabled else '❌ 禁用'}")
        print("-" * 70)
        
        if not token:
            print("  ❌ Token未配置")
            results.append({
                "page_id": page_id,
                "page_name": page_name,
                "status": "no_token",
                "error": "Token未配置"
            })
        else:
            result = await test_conversations_endpoint(page_id, token)
            results.append({
                "page_id": page_id,
                "page_name": page_name,
                "auto_reply_enabled": auto_reply_enabled,
                **result
            })
            
            if result["endpoint_works"]:
                print(f"  ✅ API端点可用")
                print(f"  ✅ 找到 {result['conversation_count']} 个对话")
            else:
                print(f"  ❌ API端点不可用")
                if result["error"]:
                    print(f"  ❌ 错误: {result['error']}")
                    
                    # 检查是否是Token不匹配错误
                    if "Requested Page Does Not Match Page Access Token" in result["error"] or "code: 10" in result["error"]:
                        print(f"  ⚠️  这是Token不匹配错误！")
                        print(f"  💡 建议: 检查Token是否属于正确的页面")
                        print(f"  💡 访问: https://developers.facebook.com/tools/debug/accesstoken/")
        
        print()
        await asyncio.sleep(0.5)  # 避免API速率限制
    
    # 总结
    print("=" * 70)
    print("诊断总结")
    print("=" * 70)
    print()
    
    ok_count = sum(1 for r in results if r.get("endpoint_works", False))
    error_count = sum(1 for r in results if not r.get("endpoint_works", False) and r.get("status") != "no_token")
    no_token_count = sum(1 for r in results if r.get("status") == "no_token")
    
    print(f"✅ API端点可用: {ok_count} 个页面")
    print(f"❌ API端点错误: {error_count} 个页面")
    print(f"⚠️  Token未配置: {no_token_count} 个页面")
    print()
    
    if error_count > 0:
        print("需要修复的页面:")
        print()
        for r in results:
            if not r.get("endpoint_works", False) and r.get("status") != "no_token":
                print(f"  - {r['page_name']} (ID: {r['page_id']})")
                if r.get("error"):
                    print(f"    错误: {r['error']}")
                print()
        
        print("修复方法:")
        print("  1. 访问 https://developers.facebook.com/tools/debug/accesstoken/")
        print("  2. 输入Token检查其实际所属页面")
        print("  3. 如果Token属于其他页面，需要:")
        print("     a) 获取正确的页面Token")
        print("     b) 运行: python scripts/tools/manage_pages.py")
        print("     c) 或直接更新 .page_tokens.json 文件")
        print()
    
    if no_token_count > 0:
        print("需要配置Token的页面:")
        for r in results:
            if r.get("status") == "no_token":
                print(f"  - {r['page_name']} (ID: {r['page_id']})")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(diagnose_all_pages_api())
    except Exception as e:
        print(f"❌ 诊断过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

