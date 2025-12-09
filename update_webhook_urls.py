"""更新Webhook URL配置指南脚本"""
import sys
from src.config import settings

def show_webhook_config():
    """显示Webhook配置信息"""
    print("=" * 70)
    print("Webhook URL配置指南")
    print("=" * 70)
    
    print("\n【当前配置】")
    print(f"  验证令牌: {settings.facebook_verify_token}")
    if hasattr(settings, 'instagram_verify_token') and settings.instagram_verify_token:
        print(f"  Instagram验证令牌: {settings.instagram_verify_token}")
    else:
        print(f"  Instagram验证令牌: {settings.facebook_verify_token} (使用Facebook令牌)")
    
    print("\n【需要在Facebook开发者后台配置的URL】")
    print("\n1. Facebook Messenger Webhook:")
    print("   URL: https://YOUR-APP.zeabur.app/webhook")
    print("   验证令牌: " + settings.facebook_verify_token)
    print("   订阅事件: messages, messaging_postbacks, message_deliveries, message_reads")
    
    print("\n2. Instagram Webhook:")
    print("   URL: https://YOUR-APP.zeabur.app/instagram/webhook")
    instagram_token = getattr(settings, 'instagram_verify_token', None) or settings.facebook_verify_token
    print("   验证令牌: " + instagram_token)
    print("   订阅事件: messages")
    
    print("\n【配置步骤】")
    print("1. 登录 Facebook开发者后台: https://developers.facebook.com/")
    print("2. 选择您的应用")
    print("3. 进入产品设置 → Messenger/Instagram")
    print("4. 在Webhooks部分添加上述URL")
    print("5. 使用上述验证令牌进行验证")
    print("6. 订阅相应的事件")
    
    print("\n【测试Webhook】")
    print("配置完成后，可以使用以下命令测试：")
    print("\nFacebook Webhook验证:")
    print(f'  curl "https://YOUR-APP.zeabur.app/webhook?hub.mode=subscribe&hub.verify_token={settings.facebook_verify_token}&hub.challenge=test123"')
    print("\nInstagram Webhook验证:")
    print(f'  curl "https://YOUR-APP.zeabur.app/instagram/webhook?hub.mode=subscribe&hub.verify_token={instagram_token}&hub.challenge=test123"')
    
    print("\n" + "=" * 70)
    print("⚠️  请将 YOUR-APP.zeabur.app 替换为您的实际Zeabur域名")
    print("=" * 70)

if __name__ == "__main__":
    try:
        show_webhook_config()
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


