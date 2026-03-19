"""
cache_manager.py - 缓存管理模块

该模块负责：
- 翻译结果缓存
- 缓存增删改查
- 过期清理
- 加密存储

遵循PEP8规范，所有函数均添加文档字符串。
"""

import os
import json
import time
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
from pathlib import Path


class CacheEncryption:
    """
    缓存加密工具类
    
    使用简单的Base64+哈希混淆进行缓存加密。
    """
    
    _KEY_SALT = "cache_v1.0_salt"
    
    @classmethod
    def encrypt(cls, data: str) -> str:
        """
        加密字符串
        
        Args:
            data: 原始字符串
            
        Returns:
            加密后的字符串
        """
        key = hashlib.sha256(cls._KEY_SALT.encode()).digest()
        data_bytes = data.encode('utf-8')
        xored = bytes([data_bytes[i] ^ key[i % len(key)] for i in range(len(data_bytes))])
        return base64.b64encode(xored).decode('utf-8')
    
    @classmethod
    def decrypt(cls, data: str) -> str:
        """
        解密字符串
        
        Args:
            data: 加密后的字符串
            
        Returns:
            原始字符串
        """
        try:
            key = hashlib.sha256(cls._KEY_SALT.encode()).digest()
            data_bytes = base64.b64decode(data.encode('utf-8'))
            xored = bytes([data_bytes[i] ^ key[i % len(key)] for i in range(len(data_bytes))])
            return xored.decode('utf-8')
        except Exception:
            return ""


class CacheEntry:
    """
    缓存条目类
    
    表示单条缓存记录。
    """
    
    def __init__(self, cache_key: str, source_text: str, translated_text: str,
                 source_lang: str, target_lang: str, engine: str,
                 additional_data: Optional[Dict] = None,
                 created_at: Optional[float] = None,
                 expire_hours: int = 24):
        """
        初始化缓存条目
        
        Args:
            cache_key: 缓存键
            source_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            additional_data: 附加数据（如发音、例句等）
            created_at: 创建时间戳
            expire_hours: 过期时间（小时）
        """
        self.cache_key = cache_key
        self.source_text = source_text
        self.translated_text = translated_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.engine = engine
        self.additional_data = additional_data or {}
        self.created_at = created_at or time.time()
        self.expire_hours = expire_hours
    
    @property
    def expire_at(self) -> float:
        """获取过期时间戳"""
        return self.created_at + (self.expire_hours * 3600)
    
    @property
    def is_expired(self) -> bool:
        """检查是否已过期"""
        return time.time() > self.expire_at
    
    @property
    def remaining_time(self) -> int:
        """获取剩余有效时间（秒）"""
        remaining = self.expire_at - time.time()
        return max(0, int(remaining))
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            包含所有属性的字典
        """
        return {
            'cache_key': self.cache_key,
            'source_text': self.source_text,
            'translated_text': self.translated_text,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'engine': self.engine,
            'additional_data': self.additional_data,
            'created_at': self.created_at,
            'expire_hours': self.expire_hours
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        """
        从字典创建缓存条目
        
        Args:
            data: 包含缓存数据的字典
            
        Returns:
            CacheEntry 实例
        """
        return cls(
            cache_key=data['cache_key'],
            source_text=data['source_text'],
            translated_text=data['translated_text'],
            source_lang=data['source_lang'],
            target_lang=data['target_lang'],
            engine=data['engine'],
            additional_data=data.get('additional_data'),
            created_at=data.get('created_at'),
            expire_hours=data.get('expire_hours', 24)
        )


class CacheManager:
    """
    缓存管理器类
    
    管理翻译缓存的增删改查和持久化。
    """
    
    DEFAULT_CACHE_FILE = "translator_cache.json"
    DEFAULT_MAX_SIZE = 1000
    DEFAULT_EXPIRE_HOURS = 24
    
    def __init__(self, cache_file: Optional[str] = None,
                 max_size: int = 1000,
                 expire_hours: int = 24,
                 auto_save: bool = True):
        """
        初始化缓存管理器
        
        Args:
            cache_file: 缓存文件路径
            max_size: 最大缓存数量
            expire_hours: 默认过期时间（小时）
            auto_save: 是否自动保存
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_file = cache_file or self.DEFAULT_CACHE_FILE
        self._max_size = max_size
        self._expire_hours = expire_hours
        self._auto_save = auto_save
        self._modified = False
        
        self._hits = 0
        self._misses = 0
        
        self._load_cache()
    
    @staticmethod
    def generate_key(source_text: str, source_lang: str, 
                     target_lang: str, engine: str) -> str:
        """
        生成缓存键
        
        Args:
            source_text: 原文
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            
        Returns:
            缓存键字符串
        """
        normalized_text = source_text.strip().lower()
        key_string = f"{engine}:{source_lang}:{target_lang}:{normalized_text}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get(self, source_text: str, source_lang: str, 
            target_lang: str, engine: str) -> Optional[CacheEntry]:
        """
        获取缓存
        
        Args:
            source_text: 原文
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            
        Returns:
            缓存条目，如果不存在或已过期返回None
        """
        cache_key = self.generate_key(source_text, source_lang, target_lang, engine)
        
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            
            if entry.is_expired:
                del self._cache[cache_key]
                self._misses += 1
                self._save_if_needed()
                return None
            
            self._hits += 1
            return entry
        
        self._misses += 1
        return None
    
    def set(self, source_text: str, translated_text: str,
            source_lang: str, target_lang: str, engine: str,
            additional_data: Optional[Dict] = None,
            expire_hours: Optional[int] = None) -> CacheEntry:
        """
        设置缓存
        
        Args:
            source_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            additional_data: 附加数据
            expire_hours: 过期时间
            
        Returns:
            缓存条目
        """
        cache_key = self.generate_key(source_text, source_lang, target_lang, engine)
        
        if len(self._cache) >= self._max_size:
            self._evict_expired()
            
            if len(self._cache) >= self._max_size:
                self._evict_oldest()
        
        entry = CacheEntry(
            cache_key=cache_key,
            source_text=source_text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            engine=engine,
            additional_data=additional_data,
            expire_hours=expire_hours or self._expire_hours
        )
        
        self._cache[cache_key] = entry
        self._modified = True
        self._save_if_needed()
        
        return entry
    
    def delete(self, source_text: str, source_lang: str,
               target_lang: str, engine: str) -> bool:
        """
        删除缓存
        
        Args:
            source_text: 原文
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            
        Returns:
            是否删除成功
        """
        cache_key = self.generate_key(source_text, source_lang, target_lang, engine)
        
        if cache_key in self._cache:
            del self._cache[cache_key]
            self._modified = True
            self._save_if_needed()
            return True
        
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._modified = True
        self._save_if_needed()
    
    def clear_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的缓存数量
        """
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            self._modified = True
            self._save_if_needed()
        
        return len(expired_keys)
    
    def _evict_expired(self) -> None:
        """清理过期缓存（内部方法）"""
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]
        for key in expired_keys:
            del self._cache[key]
    
    def _evict_oldest(self) -> None:
        """清理最旧的缓存（内部方法）"""
        if not self._cache:
            return
        
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
        del self._cache[oldest_key]
    
    def _load_cache(self) -> None:
        """从文件加载缓存"""
        if not os.path.exists(self._cache_file):
            return
        
        try:
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            decrypted_data = CacheEncryption.decrypt(encrypted_data)
            if not decrypted_data:
                return
            
            data = json.loads(decrypted_data)
            
            for item in data:
                entry = CacheEntry.from_dict(item)
                if not entry.is_expired:
                    self._cache[entry.cache_key] = entry
            
            self._modified = False
            
        except (json.JSONDecodeError, IOError, KeyError) as e:
            pass
    
    def _save_if_needed(self) -> None:
        """根据设置保存缓存"""
        if self._auto_save:
            self.save()
    
    def save(self) -> bool:
        """
        保存缓存到文件
        
        Returns:
            是否保存成功
        """
        try:
            data = [entry.to_dict() for entry in self._cache.values()]
            json_data = json.dumps(data, ensure_ascii=False)
            encrypted_data = CacheEncryption.encrypt(json_data)
            
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            self._modified = False
            return True
            
        except IOError as e:
            return False
    
    def get_stats(self) -> Dict:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        expired_count = sum(1 for entry in self._cache.values() if entry.is_expired)
        
        return {
            'total_entries': len(self._cache),
            'expired_entries': expired_count,
            'valid_entries': len(self._cache) - expired_count,
            'max_size': self._max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate
        }
    
    def count(self) -> int:
        """
        获取缓存数量
        
        Returns:
            缓存数量
        """
        return len(self._cache)
    
    def is_empty(self) -> bool:
        """
        检查是否为空
        
        Returns:
            是否为空
        """
        return len(self._cache) == 0
    
    def __len__(self) -> int:
        """返回缓存数量"""
        return len(self._cache)
    
    def __contains__(self, key_tuple: Tuple) -> bool:
        """检查缓存是否存在"""
        source_text, source_lang, target_lang, engine = key_tuple
        cache_key = self.generate_key(source_text, source_lang, target_lang, engine)
        return cache_key in self._cache


def create_cache_manager(cache_file: Optional[str] = None,
                         max_size: int = 1000,
                         expire_hours: int = 24,
                         auto_save: bool = True) -> CacheManager:
    """
    工厂函数：创建缓存管理器实例
    
    Args:
        cache_file: 缓存文件路径
        max_size: 最大缓存数量
        expire_hours: 默认过期时间
        auto_save: 是否自动保存
        
    Returns:
        CacheManager 实例
    """
    return CacheManager(
        cache_file=cache_file,
        max_size=max_size,
        expire_hours=expire_hours,
        auto_save=auto_save
    )
