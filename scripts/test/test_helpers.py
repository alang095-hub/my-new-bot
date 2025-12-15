"""
测试辅助工具
提供测试中常用的工具函数和模拟数据生成器
"""
import random
import string
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from faker import Faker

# 初始化Faker（如果可用）
try:
    fake = Faker('zh_CN')
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    fake = None


def generate_random_string(length: int = 10) -> str:
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_email() -> str:
    """生成随机邮箱"""
    if FAKER_AVAILABLE:
        return fake.email()
    return f"test_{generate_random_string(8)}@example.com"


def generate_phone() -> str:
    """生成随机电话号码"""
    if FAKER_AVAILABLE:
        return fake.phone_number()
    # 生成11位手机号
    return f"1{random.randint(3, 9)}{''.join([str(random.randint(0, 9)) for _ in range(9)])}"


def generate_name() -> str:
    """生成随机姓名"""
    if FAKER_AVAILABLE:
        return fake.name()
    return f"测试用户{generate_random_string(6)}"


def generate_facebook_message_id() -> str:
    """生成模拟的Facebook消息ID"""
    return f"mid.{generate_random_string(20)}"


def generate_facebook_user_id() -> str:
    """生成模拟的Facebook用户ID"""
    return str(random.randint(100000000000000, 999999999999999))


def create_mock_facebook_webhook_event(
    sender_id: Optional[str] = None,
    message_text: Optional[str] = None,
    message_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建模拟的Facebook Webhook事件
    
    Args:
        sender_id: 发送者ID
        message_text: 消息文本
        message_id: 消息ID
        
    Returns:
        模拟的Webhook事件数据
    """
    if not sender_id:
        sender_id = generate_facebook_user_id()
    if not message_text:
        message_text = "测试消息"
    if not message_id:
        message_id = generate_facebook_message_id()
    
    return {
        "object": "page",
        "entry": [
            {
                "id": "page_id",
                "time": int(datetime.now().timestamp() * 1000),
                "messaging": [
                    {
                        "sender": {
                            "id": sender_id
                        },
                        "recipient": {
                            "id": "page_id"
                        },
                        "timestamp": int(datetime.now().timestamp() * 1000),
                        "message": {
                            "mid": message_id,
                            "text": message_text
                        }
                    }
                ]
            }
        ]
    }


def create_mock_conversation_data(
    customer_id: Optional[int] = None,
    platform: str = "facebook",
    content: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建模拟的对话数据
    
    Args:
        customer_id: 客户ID
        platform: 平台类型
        content: 消息内容
        
    Returns:
        模拟的对话数据
    """
    if not content:
        content = "测试消息内容"
    
    return {
        "customer_id": customer_id or 1,
        "platform": platform,
        "platform_message_id": generate_facebook_message_id(),
        "message_type": "message",
        "content": content,
        "received_at": datetime.now(timezone.utc)
    }


def create_mock_customer_data(
    platform: str = "facebook",
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建模拟的客户数据
    
    Args:
        platform: 平台类型
        name: 姓名
        email: 邮箱
        phone: 电话
        
    Returns:
        模拟的客户数据
    """
    return {
        "platform": platform,
        "platform_user_id": generate_facebook_user_id(),
        "name": name or generate_name(),
        "email": email or generate_email(),
        "phone": phone or generate_phone()
    }


def create_mock_collected_data(
    conversation_id: int,
    data_type: str = "email",
    value: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建模拟的收集数据
    
    Args:
        conversation_id: 对话ID
        data_type: 数据类型
        value: 数据值
        
    Returns:
        模拟的收集数据
    """
    if data_type == "email":
        value = value or generate_email()
    elif data_type == "phone":
        value = value or generate_phone()
    elif data_type == "name":
        value = value or generate_name()
    
    return {
        "conversation_id": conversation_id,
        "data": {
            "type": data_type,
            "value": value
        }
    }


def create_test_message_with_info(
    email: bool = True,
    phone: bool = True,
    name: bool = True
) -> str:
    """
    创建包含客户信息的测试消息
    
    Args:
        email: 是否包含邮箱
        phone: 是否包含电话
        name: 是否包含姓名
        
    Returns:
        测试消息文本
    """
    parts = []
    
    if name:
        parts.append(f"我的名字是 {generate_name()}")
    if email:
        parts.append(f"我的邮箱是 {generate_email()}")
    if phone:
        parts.append(f"我的电话是 {generate_phone()}")
    
    if not parts:
        return "测试消息"
    
    return "，".join(parts) + "，我想咨询贷款"


def wait_for_condition(
    condition_func,
    timeout: float = 10.0,
    interval: float = 0.5,
    error_message: str = "条件未满足"
):
    """
    等待条件满足
    
    Args:
        condition_func: 条件函数（返回True表示满足）
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）
        error_message: 超时错误消息
    """
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    
    raise TimeoutError(error_message)


def cleanup_test_data(db, model_class, test_marker: str = "test_"):
    """
    清理测试数据
    
    Args:
        db: 数据库会话
        model_class: 模型类
        test_marker: 测试数据标记
    """
    try:
        # 根据标记删除测试数据
        # 这里需要根据实际模型结构调整
        if hasattr(model_class, 'platform_user_id'):
            test_items = db.query(model_class).filter(
                model_class.platform_user_id.like(f"{test_marker}%")
            ).all()
        elif hasattr(model_class, 'content'):
            test_items = db.query(model_class).filter(
                model_class.content.like(f"{test_marker}%")
            ).all()
        else:
            # 如果没有合适的标记字段，跳过清理
            return
        
        for item in test_items:
            db.delete(item)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"清理测试数据失败: {str(e)}")


class MockAPIClient:
    """模拟API客户端"""
    
    def __init__(self):
        self.responses = {}
        self.requests = []
    
    def set_response(self, url: str, response: Dict[str, Any], status_code: int = 200):
        """设置模拟响应"""
        self.responses[url] = {
            "status_code": status_code,
            "json": response
        }
    
    def get(self, url: str, **kwargs):
        """模拟GET请求"""
        self.requests.append({"method": "GET", "url": url, "kwargs": kwargs})
        
        if url in self.responses:
            return MockResponse(**self.responses[url])
        else:
            return MockResponse(status_code=404, json={"error": "Not found"})
    
    def post(self, url: str, **kwargs):
        """模拟POST请求"""
        self.requests.append({"method": "POST", "url": url, "kwargs": kwargs})
        
        if url in self.responses:
            return MockResponse(**self.responses[url])
        else:
            return MockResponse(status_code=404, json={"error": "Not found"})


class MockResponse:
    """模拟HTTP响应"""
    
    def __init__(self, status_code: int = 200, json: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self._json = json or {}
        self.headers = {}
    
    def json(self):
        return self._json
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def create_test_database_url() -> str:
    """创建测试数据库URL（SQLite）"""
    import tempfile
    import os
    
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, f"test_db_{generate_random_string(8)}.db")
    return f"sqlite:///{db_path}"


def setup_test_environment():
    """设置测试环境"""
    import os
    
    # 设置测试环境变量
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("DATABASE_URL", create_test_database_url())
    
    # 设置测试用的API密钥（如果未设置）
    if not os.getenv("FACEBOOK_ACCESS_TOKEN"):
        os.environ["FACEBOOK_ACCESS_TOKEN"] = "test_token"
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test_key"
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        os.environ["TELEGRAM_BOT_TOKEN"] = "test_bot_token"
    if not os.getenv("SECRET_KEY"):
        os.environ["SECRET_KEY"] = generate_random_string(32)


if __name__ == "__main__":
    # 测试工具函数
    print("测试辅助工具")
    print("=" * 60)
    
    print(f"随机字符串: {generate_random_string()}")
    print(f"随机邮箱: {generate_email()}")
    print(f"随机电话: {generate_phone()}")
    print(f"随机姓名: {generate_name()}")
    print(f"Facebook消息ID: {generate_facebook_message_id()}")
    print(f"Facebook用户ID: {generate_facebook_user_id()}")
    
    print("\n模拟Webhook事件:")
    webhook = create_mock_facebook_webhook_event(message_text="测试消息")
    print(f"  发送者ID: {webhook['entry'][0]['messaging'][0]['sender']['id']}")
    print(f"  消息内容: {webhook['entry'][0]['messaging'][0]['message']['text']}")
    
    print("\n包含信息的测试消息:")
    message = create_test_message_with_info()
    print(f"  {message}")

