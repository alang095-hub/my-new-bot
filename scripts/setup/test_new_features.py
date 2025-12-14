"""测试新功能脚本"""
import asyncio
import httpx
import json
from typing import Dict, Any

# API基础URL（根据实际情况修改）
BASE_URL = "http://localhost:8000"


async def test_api_usage_statistics():
    """测试API使用统计"""
    print("\n=== 测试API使用统计 ===")
    
    async with httpx.AsyncClient() as client:
        # 获取今日统计
        response = await client.get(f"{BASE_URL}/api-usage/daily")
        print(f"今日统计: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 获取多日统计
        response = await client.get(f"{BASE_URL}/api-usage/statistics?days=7&api_type=openai")
        print(f"\n7天统计: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))


async def test_templates():
    """测试模板管理"""
    print("\n=== 测试模板管理 ===")
    
    async with httpx.AsyncClient() as client:
        # 列出模板
        response = await client.get(f"{BASE_URL}/templates")
        print(f"列出模板: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 创建测试模板
        template_data = {
            "name": "test_greeting",
            "category": "greeting",
            "content": "您好{{customer_name}}！欢迎咨询我们的服务。",
            "variables": ["customer_name"],
            "description": "测试问候模板",
            "priority": 10
        }
        
        response = await client.post(
            f"{BASE_URL}/templates",
            json=template_data
        )
        print(f"\n创建模板: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            template_id = data.get("data", {}).get("id")
            
            # 渲染模板
            if template_id:
                render_data = {
                    "template_name": "test_greeting",
                    "variables": {
                        "customer_name": "张三"
                    }
                }
                response = await client.post(
                    f"{BASE_URL}/templates/render",
                    json=render_data
                )
                print(f"\n渲染模板: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(json.dumps(data, indent=2, ensure_ascii=False))


async def test_ab_testing():
    """测试A/B测试"""
    print("\n=== 测试A/B测试 ===")
    
    async with httpx.AsyncClient() as client:
        # 列出版本
        response = await client.get(f"{BASE_URL}/ab-testing/versions")
        print(f"列出版本: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 创建测试版本
        version_data = {
            "name": "测试版本1",
            "version_code": "test_v1",
            "prompt_content": "你是一个专业的客服助手，回复要正式、专业。",
            "traffic_percentage": 50,
            "description": "测试版本1"
        }
        
        response = await client.post(
            f"{BASE_URL}/ab-testing/versions",
            json=version_data
        )
        print(f"\n创建版本: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))


async def main():
    """主函数"""
    print("开始测试新功能...")
    
    try:
        await test_api_usage_statistics()
        await test_templates()
        await test_ab_testing()
        
        print("\n✅ 所有测试完成！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

