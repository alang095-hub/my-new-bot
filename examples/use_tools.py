"""工具使用示例"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools import (
    TokenManager,
    ConfigChecker,
    PermissionChecker,
    ExchangeTokenTool,
    registry,
    CLI
)


async def example_token_manager():
    """令牌管理器示例"""
    print("=" * 60)
    print("示例1: 使用令牌管理器")
    print("=" * 60)
    
    manager = TokenManager()
    
    # 示例URL（实际使用时替换为真实的授权URL）
    example_url = "http://localhost:8000/oauth/callback#access_token=TOKEN&token_type=bearer&expires_in=5183944"
    
    result = await manager.execute(action='extract', url=example_url)
    
    if result.is_success():
        print(f"✅ {result.message}")
        print(f"令牌: {result.data.get('access_token', 'N/A')[:20]}...")
        print(f"过期时间: {result.data.get('expires_in', 'N/A')}")
    else:
        print(f"❌ {result.message}")
        for error in result.errors or []:
            print(f"  - {error}")


async def example_config_checker():
    """配置检查器示例"""
    print("\n" + "=" * 60)
    print("示例2: 使用配置检查器")
    print("=" * 60)
    
    checker = ConfigChecker()
    
    # 检查.env文件
    result = checker.check_env_file()
    print(f"{'✅' if result.is_success() else '❌'} {result.message}")
    
    # 检查Facebook配置
    result = await checker.execute(type='facebook')
    print(f"\n{'✅' if result.is_success() else '⚠️' if result.has_warnings() else '❌'} {result.message}")
    
    if result.errors:
        print("问题:")
        for error in result.errors:
            print(f"  - {error}")


async def example_permission_checker():
    """权限检查器示例"""
    print("\n" + "=" * 60)
    print("示例3: 使用权限检查器")
    print("=" * 60)
    
    checker = PermissionChecker()
    
    # 需要提供访问令牌（实际使用时从环境变量或配置获取）
    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    
    if not access_token:
        print("⚠️  未设置 FACEBOOK_ACCESS_TOKEN，跳过权限检查")
        return
    
    result = await checker.execute(access_token=access_token)
    
    if result.is_success():
        print(f"✅ {result.message}")
        if result.data:
            print(f"已授予的权限: {len(result.data.get('granted_permissions', []))}")
    elif result.has_warnings():
        print(f"⚠️  {result.message}")
        if result.errors:
            print("缺失的权限:")
            for error in result.errors:
                print(f"  - {error}")
    else:
        print(f"❌ {result.message}")
        if result.errors:
            for error in result.errors:
                print(f"  - {error}")


async def example_registry():
    """工具注册器示例"""
    print("\n" + "=" * 60)
    print("示例4: 使用工具注册器")
    print("=" * 60)
    
    print("已注册的工具:")
    for tool_name in registry.list_tools():
        tool = registry.create_tool(tool_name)
        if tool:
            print(f"  - {tool_name}: {tool.description}")


async def example_cli():
    """CLI示例"""
    print("\n" + "=" * 60)
    print("示例5: 使用CLI接口")
    print("=" * 60)
    
    cli = CLI()
    
    # 显示帮助
    print("\n可用工具:")
    cli.show_help()
    
    # 列出所有工具
    print("\n已注册的工具:")
    for name in cli.registry.list_tools():
        print(f"  - {name}")


async def main():
    """主函数"""
    print("工具模块使用示例\n")
    
    # 运行各个示例
    await example_token_manager()
    await example_config_checker()
    await example_permission_checker()
    await example_registry()
    await example_cli()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())






