"""多页面Token管理器"""
import os
import json
import httpx
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class PageTokenManager:
    """管理多个Facebook页面的Token"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化Token管理器
        
        Args:
            config_file: Token配置文件路径，默认为项目根目录下的 .page_tokens.json
        """
        if config_file is None:
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / ".page_tokens.json"
        
        self.config_file = config_file
        self._tokens: Dict[str, str] = {}
        self._page_info: Dict[str, Dict] = {}
        self._load_tokens()
    
    def _load_tokens(self):
        """从文件加载Token配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._tokens = data.get("tokens", {})
                    self._page_info = data.get("page_info", {})
                logger.info(f"加载了 {len(self._tokens)} 个页面Token")
            except Exception as e:
                logger.error(f"加载Token配置失败: {str(e)}")
                self._tokens = {}
                self._page_info = {}
        else:
            # 如果文件不存在，尝试从环境变量加载默认Token
            default_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
            if default_token:
                logger.info("使用默认Token（从环境变量）")
                # 默认Token不关联特定页面ID，使用"default"作为key
                self._tokens["default"] = default_token
    
    def _save_tokens(self):
        """保存Token配置到文件"""
        try:
            data = {
                "tokens": self._tokens,
                "page_info": self._page_info
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"保存了 {len(self._tokens)} 个页面Token")
        except Exception as e:
            logger.error(f"保存Token配置失败: {str(e)}")
    
    def get_token(self, page_id: Optional[str] = None) -> Optional[str]:
        """
        获取指定页面的Token
        
        Args:
            page_id: 页面ID，如果为None则返回默认Token
            
        Returns:
            Token字符串，如果未找到则返回None
        """
        if page_id and page_id in self._tokens:
            return self._tokens[page_id]
        
        # 如果没有指定page_id或找不到，返回默认Token
        return self._tokens.get("default")
    
    def set_token(self, page_id: str, token: str, page_name: Optional[str] = None, expires_at: Optional[str] = None):
        """
        设置页面的Token
        
        Args:
            page_id: 页面ID
            token: Token字符串
            page_name: 页面名称（可选，用于记录）
            expires_at: Token过期时间（ISO格式字符串，可选）
        """
        self._tokens[page_id] = token
        if page_name or page_id in self._page_info:
            if page_id not in self._page_info:
                self._page_info[page_id] = {}
            if page_name:
                self._page_info[page_id]["name"] = page_name
            if expires_at:
                self._page_info[page_id]["expires_at"] = expires_at
            self._page_info[page_id]["updated_at"] = str(Path(__file__).stat().st_mtime) if Path(__file__).exists() else None
        self._save_tokens()
        logger.info(f"设置页面 {page_id} 的Token" + (f" (过期时间: {expires_at})" if expires_at else ""))
    
    def set_default_token(self, token: str):
        """设置默认Token（用于未指定page_id的情况）"""
        self._tokens["default"] = token
        self._save_tokens()
        logger.info("设置默认Token")
    
    def remove_token(self, page_id: str) -> bool:
        """
        移除页面的Token
        
        Args:
            page_id: 页面ID
            
        Returns:
            是否成功移除
        """
        if page_id in self._tokens:
            del self._tokens[page_id]
            if page_id in self._page_info:
                del self._page_info[page_id]
            self._save_tokens()
            logger.info(f"移除页面 {page_id} 的Token")
            return True
        return False
    
    def list_pages(self) -> Dict[str, Dict]:
        """
        列出所有已配置的页面
        
        Returns:
            页面信息字典，key为页面ID，value为页面信息
        """
        return self._page_info.copy()
    
    async def sync_from_user_token(self, user_token: str) -> int:
        """
        从用户Token同步所有页面的Token（支持分页，获取所有页面）
        
        Args:
            user_token: 用户级别的Token（需要有pages_show_list权限）
            
        Returns:
            同步的页面数量
        """
        from src.core.config.constants import FACEBOOK_ME_ACCOUNTS_URL
        
        try:
            all_pages = []
            url = FACEBOOK_ME_ACCOUNTS_URL
            params = {"access_token": user_token, "limit": 100}  # 每页最多100个
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                page_count = 0
                
                # 处理分页，获取所有页面
                while url:
                    response = await client.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        pages = data.get("data", [])
                        all_pages.extend(pages)
                        page_count += 1
                        logger.info(f"获取第 {page_count} 页，{len(pages)} 个页面（累计: {len(all_pages)} 个）")
                        
                        # 检查是否有下一页
                        paging = data.get("paging", {})
                        if "next" in paging:
                            url = paging["next"]
                            params = {}  # 下一页URL已经包含所有参数
                        else:
                            url = None
                    else:
                        logger.error(f"获取页面列表失败: HTTP {response.status_code}")
                        return 0
                
                # 保存所有页面
                count = 0
                for page in all_pages:
                    page_id = page.get("id")
                    page_token = page.get("access_token")
                    page_name = page.get("name")
                    
                    if page_id and page_token:
                        self.set_token(page_id, page_token, page_name)
                        count += 1
                
                logger.info(f"从用户Token同步了 {count} 个页面Token（共 {page_count} 页）")
                return count
        except Exception as e:
            logger.error(f"同步页面Token失败: {str(e)}", exc_info=True)
            return 0


# 全局Token管理器实例
page_token_manager = PageTokenManager()

