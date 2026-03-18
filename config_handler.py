"""
config_handler.py - 配置管理模块

该模块负责：
- 管理计算器配置参数
- 配置持久化存储
- 配置导入导出
- 兼容模式管理

遵循PEP8规范，所有函数均添加文档字符串。
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigHandler:
    """
    配置管理器类
    
    管理计算器的所有配置参数，支持持久化存储。
    """
    
    DEFAULT_CONFIG = {
        'angle_mode': 'degree',
        'decimal_places': 4,
        'use_scientific': True,
        'scientific_threshold_high': 1e10,
        'scientific_threshold_low': 1e-6,
        'use_cache': True,
        'max_cache_size': 1000,
        'compatibility_mode': False,
        'auto_save_history': True,
        'max_history_records': 1000,
        'language': 'zh_CN',
        'theme': 'default',
        'show_tips': True
    }
    
    VALID_ANGLE_MODES = ('degree', 'radian')
    VALID_THEMES = ('default', 'dark', 'light')
    VALID_LANGUAGES = ('zh_CN', 'en_US')
    
    DEFAULT_CONFIG_FILE = "calculator_config.json"
    
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
            return
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            for key, value in loaded_config.items():
                if key in self._config:
                    self._config[key] = value
            
            self._modified = False
            
        except (json.JSONDecodeError, IOError) as e:
            pass
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            
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
        return self._config.get(key, default)
    
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
        if key not in self.DEFAULT_CONFIG:
            return False
        
        if not self._validate_value(key, value):
            return False
        
        self._config[key] = value
        self._modified = True
        
        if auto_save:
            return self.save()
        
        return True
    
    def _validate_value(self, key: str, value: Any) -> bool:
        """
        验证配置值
        
        Args:
            key: 配置键名
            value: 配置值
            
        Returns:
            是否有效
        """
        validators = {
            'angle_mode': lambda v: v in self.VALID_ANGLE_MODES,
            'decimal_places': lambda v: isinstance(v, int) and 0 <= v <= 15,
            'use_scientific': lambda v: isinstance(v, bool),
            'scientific_threshold_high': lambda v: isinstance(v, (int, float)) and v > 0,
            'scientific_threshold_low': lambda v: isinstance(v, (int, float)) and v > 0,
            'use_cache': lambda v: isinstance(v, bool),
            'max_cache_size': lambda v: isinstance(v, int) and v > 0,
            'compatibility_mode': lambda v: isinstance(v, bool),
            'auto_save_history': lambda v: isinstance(v, bool),
            'max_history_records': lambda v: isinstance(v, int) and v > 0,
            'language': lambda v: v in self.VALID_LANGUAGES,
            'theme': lambda v: v in self.VALID_THEMES,
            'show_tips': lambda v: isinstance(v, bool)
        }
        
        validator = validators.get(key)
        if validator:
            return validator(value)
        
        return True
    
    def reset_to_default(self, auto_save: bool = True) -> None:
        """
        重置为默认配置
        
        Args:
            auto_save: 是否自动保存
        """
        self._config = self.DEFAULT_CONFIG.copy()
        self._modified = True
        
        if auto_save:
            self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            配置字典的副本
        """
        return self._config.copy()
    
    def update(self, config_dict: Dict[str, Any], auto_save: bool = True) -> bool:
        """
        批量更新配置
        
        Args:
            config_dict: 配置字典
            auto_save: 是否自动保存
            
        Returns:
            是否全部更新成功
        """
        success = True
        for key, value in config_dict.items():
            if not self.set(key, value, auto_save=False):
                success = False
        
        if success and auto_save:
            return self.save()
        
        return success
    
    @property
    def angle_mode(self) -> str:
        """获取角度模式"""
        return self._config['angle_mode']
    
    @angle_mode.setter
    def angle_mode(self, mode: str) -> None:
        """
        设置角度模式
        
        Args:
            mode: 'degree' 或 'radian'
            
        Raises:
            ValueError: 当模式无效时
        """
        if mode not in self.VALID_ANGLE_MODES:
            raise ValueError(f"无效的角度模式: {mode}，请使用 {self.VALID_ANGLE_MODES}")
        self.set('angle_mode', mode)
    
    @property
    def decimal_places(self) -> int:
        """获取小数位数"""
        return self._config['decimal_places']
    
    @decimal_places.setter
    def decimal_places(self, places: int) -> None:
        """
        设置小数位数
        
        Args:
            places: 小数位数（0-15）
            
        Raises:
            ValueError: 当位数无效时
        """
        if not isinstance(places, int) or places < 0 or places > 15:
            raise ValueError(f"小数位数必须在0-15之间，当前: {places}")
        self.set('decimal_places', places)
    
    @property
    def compatibility_mode(self) -> bool:
        """获取兼容模式状态"""
        return self._config['compatibility_mode']
    
    @compatibility_mode.setter
    def compatibility_mode(self, enabled: bool) -> None:
        """
        设置兼容模式
        
        Args:
            enabled: 是否启用兼容模式
        """
        self.set('compatibility_mode', enabled)
    
    @property
    def use_cache(self) -> bool:
        """获取缓存启用状态"""
        return self._config['use_cache']
    
    @use_cache.setter
    def use_cache(self, enabled: bool) -> None:
        """
        设置缓存启用状态
        
        Args:
            enabled: 是否启用缓存
        """
        self.set('use_cache', enabled)
    
    @property
    def use_scientific(self) -> bool:
        """获取科学计数法启用状态"""
        return self._config['use_scientific']
    
    @use_scientific.setter
    def use_scientific(self, enabled: bool) -> None:
        """
        设置科学计数法启用状态
        
        Args:
            enabled: 是否启用科学计数法
        """
        self.set('use_scientific', enabled)
    
    def export_config(self, file_path: str) -> bool:
        """
        导出配置到文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    def import_config(self, file_path: str) -> bool:
        """
        从文件导入配置
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            是否导入成功
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            return self.update(imported_config)
            
        except (json.JSONDecodeError, IOError):
            return False
    
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
        for key, value in self._config.items():
            lines.append(f"  {key}: {value}")
        return '\n'.join(lines)
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"ConfigHandler({self._config})"


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
        """重置实例（主要用于测试）"""
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
