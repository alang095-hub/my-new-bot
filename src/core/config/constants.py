"""常量定义 - 提取硬编码值"""
from enum import Enum


class MessageType(str, Enum):
    """消息类型"""
    AD = "ad"
    MESSAGE = "message"
    COMMENT = "comment"


class ReviewStatus(str, Enum):
    """审核状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"


class Priority(str, Enum):
    """优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Platform(str, Enum):
    """平台类型"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"


# API 相关常量
FACEBOOK_GRAPH_API_VERSION = "v18.0"
FACEBOOK_GRAPH_API_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_GRAPH_API_VERSION}"

# 默认配置值
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_TEMPERATURE = 0.7
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_PORT = 8000

# 日志相关
DEFAULT_LOG_LEVEL = "INFO"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 10

# 数据库相关
# 连接池配置（生产环境优化）
# 根据应用负载调整这些值：
# - 小型应用（<100并发）: DB_POOL_SIZE=10, DB_MAX_OVERFLOW=20
# - 中型应用（100-500并发）: DB_POOL_SIZE=20, DB_MAX_OVERFLOW=40
# - 大型应用（>500并发）: DB_POOL_SIZE=50, DB_MAX_OVERFLOW=100
DB_POOL_SIZE = 20  # 连接池大小（推荐：CPU核心数 * 2 + 磁盘数）
DB_MAX_OVERFLOW = 40  # 最大溢出连接数（允许超过pool_size的连接数）
DB_POOL_RECYCLE = 3600  # 连接回收时间（秒），1小时，防止连接过期
DB_POOL_TIMEOUT = 30  # 获取连接超时时间（秒）
DB_POOL_PRE_PING = True  # 连接前ping检查，确保连接有效

# 消息处理相关
MESSAGE_SUMMARY_MAX_LENGTH = 500
MAX_MESSAGE_PREVIEW_LENGTH = 200

# 重试相关
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1

