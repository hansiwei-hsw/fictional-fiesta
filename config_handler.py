"""
config_handler.py - 配置管理模块

该模块负责：
- API密钥管理（加密存储）
- 翻译引擎配置
- 模式配置持久化
- 配置文件读写

遵循PEP8规范，所有函数均添加文档字符串。
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigEncryption:
    """
    配置加密工具类
    
    使用简单的Base64+哈希混淆进行配置加密。
    """
    
    _KEY_SALT = "translator_v1.0_salt"
    
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


class ConfigHandler:
    """
    配置管理器类
    
    管理翻译器的所有配置参数，支持多翻译引擎配置。
    """
    
    DEFAULT_CONFIG = {
        'current_engine': 'baidu',
        'mode': 'professional',
        'cache_enabled': True,
        'cache_expire_hours': 24,
        'max_cache_size': 1000,
        'auto_save_history': True,
        'max_history_records': 500,
        'timeout': 10,
        'retry_times': 3,
        'show_pronunciation': True,
        'show_examples': True,
        'show_part_of_speech': True,
        'engines': {
            'baidu': {
                'app_id': '',
                'secret_key': '',
                'enabled': True
            },
            'youdao': {
                'app_key': '',
                'app_secret': '',
                'enabled': False
            },
            'google': {
                'api_key': '',
                'enabled': False
            }
        }
    }
    
    VALID_ENGINES = ('baidu', 'youdao', 'google')
    VALID_MODES = ('professional', 'simple')
    
    DEFAULT_CONFIG_FILE = "translator_config.json"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径（可选）
        """
        self._config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._config_file = config_file or self.DEFAULT_CONFIG_FILE
        self._modified = False
        
        self._load_config()
    
    def _load_config(self) -> None:
        """从文件加载配置"""
        if not os.path.exists(self._config_file):
            self._create_default_config()
            return
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            self._merge_config(loaded_config)
            self._decrypt_api_keys()
            self._modified = False
            
        except (json.JSONDecodeError, IOError) as e:
            self._create_default_config()
    
    def _merge_config(self, loaded_config: Dict) -> None:
        """
        合并加载的配置到默认配置
        
        Args:
            loaded_config: 加载的配置字典
        """
        for key, value in loaded_config.items():
            if key == 'engines':
                for engine, engine_config in value.items():
                    if engine in self._config['engines']:
                        self._config['engines'][engine].update(engine_config)
            elif key in self._config:
                self._config[key] = value
    
    def _decrypt_api_keys(self) -> None:
        """解密API密钥"""
        for engine, config in self._config['engines'].items():
            for key in ['app_id', 'secret_key', 'app_key', 'app_secret', 'api_key']:
                if key in config and config[key]:
                    decrypted = ConfigEncryption.decrypt(config[key])
                    if decrypted:
                        config[key] = decrypted
    
    def _encrypt_api_keys(self) -> Dict:
        """
        加密API密钥用于保存
        
        Returns:
            加密后的配置副本
        """
        config_copy = json.loads(json.dumps(self._config))
        
        for engine, config in config_copy['engines'].items():
            for key in ['app_id', 'secret_key', 'app_key', 'app_secret', 'api_key']:
                if key in config and config[key]:
                    config[key] = ConfigEncryption.encrypt(config[key])
        
        return config_copy
    
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            config_to_save = self._encrypt_api_keys()
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)
            
            self._modified = False
            return True
            
        except IOError as e:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键名
            value: 配置值
            auto_save: 是否自动保存
            
        Returns:
            是否设置成功
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._modified = True
        
        if auto_save:
            return self.save()
        
        return True
    
    @property
    def current_engine(self) -> str:
        """获取当前翻译引擎"""
        return self._config['current_engine']
    
    @current_engine.setter
    def current_engine(self, engine: str) -> None:
        """
        设置当前翻译引擎
        
        Args:
            engine: 引擎名称
            
        Raises:
            ValueError: 当引擎无效时
        """
        if engine not in self.VALID_ENGINES:
            raise ValueError(f"无效的翻译引擎: {engine}，请使用 {self.VALID_ENGINES}")
        self.set('current_engine', engine)
    
    @property
    def mode(self) -> str:
        """获取当前模式"""
        return self._config['mode']
    
    @mode.setter
    def mode(self, mode: str) -> None:
        """
        设置当前模式
        
        Args:
            mode: 模式名称 ('professional' 或 'simple')
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"无效的模式: {mode}，请使用 {self.VALID_MODES}")
        self.set('mode', mode)
    
    def get_engine_config(self, engine: Optional[str] = None) -> Dict:
        """
        获取指定引擎的配置
        
        Args:
            engine: 引擎名称，默认为当前引擎
            
        Returns:
            引擎配置字典
        """
        engine = engine or self.current_engine
        return self._config['engines'].get(engine, {})
    
    def set_engine_config(self, engine: str, config: Dict, 
                          auto_save: bool = True) -> bool:
        """
        设置引擎配置
        
        Args:
            engine: 引擎名称
            config: 配置字典
            auto_save: 是否自动保存
            
        Returns:
            是否设置成功
        """
        if engine not in self.VALID_ENGINES:
            return False
        
        self._config['engines'][engine].update(config)
        self._modified = True
        
        if auto_save:
            return self.save()
        
        return True
    
    def is_engine_configured(self, engine: Optional[str] = None) -> bool:
        """
        检查引擎是否已配置
        
        Args:
            engine: 引擎名称，默认为当前引擎
            
        Returns:
            是否已配置
        """
        engine = engine or self.current_engine
        config = self.get_engine_config(engine)
        
        if engine == 'baidu':
            return bool(config.get('app_id') and config.get('secret_key'))
        elif engine == 'youdao':
            return bool(config.get('app_key') and config.get('app_secret'))
        elif engine == 'google':
            return bool(config.get('api_key'))
        
        return False
    
    def get_available_engines(self) -> List[str]:
        """
        获取已配置的可用引擎列表
        
        Returns:
            可用引擎名称列表
        """
        available = []
        for engine in self.VALID_ENGINES:
            if self.is_engine_configured(engine) and self._config['engines'][engine].get('enabled', True):
                available.append(engine)
        return available
    
    def reset_to_default(self, auto_save: bool = True) -> None:
        """
        重置为默认配置
        
        Args:
            auto_save: 是否自动保存
        """
        self._config = json.loads(json.dumps(self.DEFAULT_CONFIG))
        self._modified = True
        
        if auto_save:
            self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            配置字典的副本
        """
        return json.loads(json.dumps(self._config))
    
    def is_modified(self) -> bool:
        """
        检查配置是否已修改
        
        Returns:
            是否已修改
        """
        return self._modified
    
    def __str__(self) -> str:
        """字符串表示"""
        lines = ["当前配置:"]
        lines.append(f"  当前引擎: {self.current_engine}")
        lines.append(f"  当前模式: {self.mode}")
        lines.append(f"  缓存启用: {self._config['cache_enabled']}")
        lines.append(f"  自动保存历史: {self._config['auto_save_history']}")
        return '\n'.join(lines)
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"ConfigHandler(engine={self.current_engine}, mode={self.mode})"


class ConfigManager:
    """
    配置管理器单例类
    
    提供全局配置访问点。
    """
    
    _instance: Optional['ConfigHandler'] = None
    
    @classmethod
    def get_instance(cls) -> ConfigHandler:
        """
        获取配置管理器实例
        
        Returns:
            ConfigHandler 实例
        """
        if cls._instance is None:
            cls._instance = ConfigHandler()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """重置实例"""
        cls._instance = None


def get_config() -> ConfigHandler:
    """
    获取全局配置管理器实例
    
    Returns:
        ConfigHandler 实例
    """
    return ConfigManager.get_instance()


def create_config(config_file: Optional[str] = None) -> ConfigHandler:
    """
    工厂函数：创建配置管理器实例
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        ConfigHandler 实例
    """
    return ConfigHandler(config_file=config_file)
