"""
配置管理模块

本模块负责管理计算器的配置项，包括角度/弧度模式、小数位数、
兼容模式等设置的持久化存储。

作者: Development Team
版本: 2.0.0
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class CalculatorConfig:
    """计算器配置数据类"""
    
    # 角度模式: 'degrees' 或 'radians'
    angle_mode: str = 'degrees'
    
    # 小数位数 (0-10)
    decimal_places: int = 4
    
    # 兼容模式: True为旧版兼容模式，False为新版交互模式
    compatibility_mode: bool = False
    
    # 自动科学计数法
    auto_scientific: bool = True
    
    # 科学计数法阈值
    scientific_threshold_high: float = 1e10
    scientific_threshold_low: float = 1e-10
    
    # 历史记录设置
    max_history_size: int = 1000
    auto_save_history: bool = True
    
    # 界面设置
    show_welcome_message: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorConfig':
        """从字典创建配置"""
        # 过滤掉无效的键
        valid_keys = {k for k in cls.__dataclass_fields__.keys()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


class ConfigHandler:
    """配置处理器类"""
    
    # 默认配置文件路径
    DEFAULT_CONFIG_FILE = "calculator_config.json"
    
    # 有效角度模式
    VALID_ANGLE_MODES = ['degrees', 'radians']
    
    # 小数位数范围
    DECIMAL_PLACES_RANGE = (0, 10)
    
    def __init__(self, config_file: str = None):
        """
        初始化配置处理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self._config = CalculatorConfig()
        self._load_config()
    
    def _load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = CalculatorConfig.from_dict(data)
                    self._validate_config()
            except (json.JSONDecodeError, IOError, TypeError) as e:
                print(f"警告: 加载配置失败，使用默认配置 - {e}")
                self._config = CalculatorConfig()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"警告: 保存配置失败 - {e}")
    
    def _validate_config(self):
        """验证并修正配置值"""
        # 验证角度模式
        if self._config.angle_mode not in self.VALID_ANGLE_MODES:
            self._config.angle_mode = 'degrees'
        
        # 验证小数位数
        if not (self.DECIMAL_PLACES_RANGE[0] <= self._config.decimal_places <= self.DECIMAL_PLACES_RANGE[1]):
            self._config.decimal_places = 4
        
        # 验证历史记录大小
        if self._config.max_history_size < 10 or self._config.max_history_size > 10000:
            self._config.max_history_size = 1000
    
    # ==================== 配置项 getter/setter ====================
    
    @property
    def angle_mode(self) -> str:
        """获取角度模式"""
        return self._config.angle_mode
    
    @angle_mode.setter
    def angle_mode(self, mode: str):
        """设置角度模式"""
        mode = mode.lower()
        if mode not in self.VALID_ANGLE_MODES:
            raise ValueError(f"无效的角度模式 '{mode}'，有效值: {self.VALID_ANGLE_MODES}")
        self._config.angle_mode = mode
        self._save_config()
    
    @property
    def use_degrees(self) -> bool:
        """是否使用度数"""
        return self._config.angle_mode == 'degrees'
    
    @property
    def decimal_places(self) -> int:
        """获取小数位数"""
        return self._config.decimal_places
    
    @decimal_places.setter
    def decimal_places(self, places: int):
        """设置小数位数"""
        if not isinstance(places, int):
            raise ValueError("小数位数必须是整数")
        if not (self.DECIMAL_PLACES_RANGE[0] <= places <= self.DECIMAL_PLACES_RANGE[1]):
            raise ValueError(f"小数位数必须在 {self.DECIMAL_PLACES_RANGE[0]}-{self.DECIMAL_PLACES_RANGE[1]} 之间")
        self._config.decimal_places = places
        self._save_config()
    
    @property
    def compatibility_mode(self) -> bool:
        """获取兼容模式状态"""
        return self._config.compatibility_mode
    
    @compatibility_mode.setter
    def compatibility_mode(self, enabled: bool):
        """设置兼容模式"""
        self._config.compatibility_mode = bool(enabled)
        self._save_config()
    
    @property
    def auto_scientific(self) -> bool:
        """获取自动科学计数法状态"""
        return self._config.auto_scientific
    
    @auto_scientific.setter
    def auto_scientific(self, enabled: bool):
        """设置自动科学计数法"""
        self._config.auto_scientific = bool(enabled)
        self._save_config()
    
    @property
    def max_history_size(self) -> int:
        """获取最大历史记录数"""
        return self._config.max_history_size
    
    # ==================== 配置操作方法 ====================
    
    def toggle_angle_mode(self) -> str:
        """
        切换角度模式
        
        Returns:
            切换后的模式
        """
        if self._config.angle_mode == 'degrees':
            self._config.angle_mode = 'radians'
        else:
            self._config.angle_mode = 'degrees'
        self._save_config()
        return self._config.angle_mode
    
    def toggle_compatibility_mode(self) -> bool:
        """
        切换兼容模式
        
        Returns:
            切换后的状态
        """
        self._config.compatibility_mode = not self._config.compatibility_mode
        self._save_config()
        return self._config.compatibility_mode
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self._config = CalculatorConfig()
        self._save_config()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """获取配置字典"""
        return self._config.to_dict()
    
    def update_from_dict(self, updates: Dict[str, Any]):
        """
        从字典更新配置
        
        Args:
            updates: 配置更新字典
        """
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self._validate_config()
        self._save_config()
    
    def export_config(self, filename: str) -> str:
        """
        导出配置到指定文件
        
        Args:
            filename: 目标文件名
        
        Returns:
            导出的文件路径
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self._config.to_dict(), f, ensure_ascii=False, indent=2)
        return filename
    
    def import_config(self, filename: str):
        """
        从文件导入配置
        
        Args:
            filename: 源文件名
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._config = CalculatorConfig.from_dict(data)
            self._validate_config()
            self._save_config()


# 全局配置处理器实例
_config_handler: Optional[ConfigHandler] = None


def get_config_handler() -> ConfigHandler:
    """获取全局配置处理器实例"""
    global _config_handler
    if _config_handler is None:
        _config_handler = ConfigHandler()
    return _config_handler


def set_config_handler(handler: ConfigHandler):
    """设置全局配置处理器实例"""
    global _config_handler
    _config_handler = handler
