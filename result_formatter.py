"""
结果格式化模块

本模块负责处理计算结果的格式化输出，包括小数位数控制、
科学计数法转换、超大数处理等功能。

作者: Development Team
版本: 2.0.0
"""

from typing import Union

Number = Union[int, float]


class FormatterConfig:
    """格式化配置类"""
    
    # 默认小数位数
    DEFAULT_DECIMAL_PLACES = 4
    
    # 科学计数法阈值（超过此值自动转换）
    SCIENTIFIC_NOTATION_THRESHOLD = 1e10
    
    # 极小值阈值
    SCIENTIFIC_NOTATION_SMALL_THRESHOLD = 1e-10
    
    # 是否启用科学计数法
    AUTO_SCIENTIFIC = True


class ResultFormatter:
    """结果格式化器类"""
    
    def __init__(
        self,
        decimal_places: int = None,
        auto_scientific: bool = None,
        threshold_high: float = None,
        threshold_low: float = None
    ):
        """
        初始化格式化器
        
        Args:
            decimal_places: 小数位数，默认4位
            auto_scientific: 是否自动使用科学计数法
            threshold_high: 科学计数法上限阈值
            threshold_low: 科学计数法下限阈值
        """
        self.decimal_places = decimal_places or FormatterConfig.DEFAULT_DECIMAL_PLACES
        self.auto_scientific = auto_scientific if auto_scientific is not None else FormatterConfig.AUTO_SCIENTIFIC
        self.threshold_high = threshold_high or FormatterConfig.SCIENTIFIC_NOTATION_THRESHOLD
        self.threshold_low = threshold_low or FormatterConfig.SCIENTIFIC_NOTATION_SMALL_THRESHOLD
    
    def format(self, value: Number) -> str:
        """
        格式化数值输出
        
        Args:
            value: 待格式化的数值
        
        Returns:
            格式化后的字符串
        """
        # 处理整数
        if isinstance(value, int):
            return self._format_integer(value)
        
        # 处理浮点数
        if isinstance(value, float):
            return self._format_float(value)
        
        return str(value)
    
    def _format_integer(self, value: int) -> str:
        """格式化整数"""
        # 检查是否需要科学计数法
        if self.auto_scientific and abs(value) >= self.threshold_high:
            return f"{value:.{self.decimal_places}e}"
        return str(value)
    
    def _format_float(self, value: float) -> str:
        """格式化浮点数"""
        # 处理特殊值
        if value != value:  # NaN
            return "NaN"
        if value == float('inf'):
            return "+∞"
        if value == float('-inf'):
            return "-∞"
        
        # 检查是否需要科学计数法
        abs_value = abs(value)
        if self.auto_scientific:
            if abs_value >= self.threshold_high or (0 < abs_value <= self.threshold_low):
                return f"{value:.{self.decimal_places}e}"
        
        # 常规格式化
        formatted = f"{value:.{self.decimal_places}f}"
        
        # 去除末尾的0和多余的小数点
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        
        # 如果结果为空（0值），返回"0"
        if not formatted or formatted == '-':
            formatted = '0'
        
        return formatted
    
    def format_with_details(self, value: Number, operation: str = "") -> str:
        """
        带详细信息的格式化输出
        
        Args:
            value: 待格式化的数值
            operation: 运算描述
        
        Returns:
            格式化后的详细字符串
        """
        basic = self.format(value)
        
        # 添加原始科学计数法表示（对于超大/超小数）
        if isinstance(value, float) and value == value:  # 不是NaN
            abs_val = abs(value)
            if abs_val >= self.threshold_high or (0 < abs_val <= self.threshold_low):
                scientific = f"{value:.{self.decimal_places}e}"
                if operation:
                    return f"{operation} = {basic} (科学计数法: {scientific})"
                return f"{basic} (科学计数法: {scientific})"
        
        if operation:
            return f"{operation} = {basic}"
        return basic
    
    def set_decimal_places(self, places: int):
        """
        设置小数位数
        
        Args:
            places: 小数位数（0-10）
        
        Raises:
            ValueError: 当places不在有效范围内时抛出
        """
        if not isinstance(places, int) or places < 0 or places > 10:
            raise ValueError("小数位数必须在0-10之间")
        self.decimal_places = places
    
    def toggle_scientific_notation(self, enable: bool = None):
        """
        切换科学计数法自动转换
        
        Args:
            enable: 是否启用，None则切换当前状态
        """
        if enable is None:
            self.auto_scientific = not self.auto_scientific
        else:
            self.auto_scientific = bool(enable)


# 全局格式化器实例
_default_formatter = ResultFormatter()


def format_result(value: Number, decimal_places: int = None) -> str:
    """
    快捷格式化函数
    
    Args:
        value: 待格式化的数值
        decimal_places: 可选，指定小数位数
    
    Returns:
        格式化后的字符串
    """
    if decimal_places is not None:
        formatter = ResultFormatter(decimal_places=decimal_places)
        return formatter.format(value)
    return _default_formatter.format(value)


def format_scientific(value: Number, precision: int = 4) -> str:
    """
    格式化为科学计数法
    
    Args:
        value: 待格式化的数值
        precision: 精度位数
    
    Returns:
        科学计数法字符串
    """
    if value == 0:
        return f"0.{ '0' * precision }e+00"
    return f"{value:.{precision}e}"


def format_percentage(value: Number, decimal_places: int = 2) -> str:
    """
    格式化为百分比
    
    Args:
        value: 待格式化的数值（0.5表示50%）
        decimal_places: 小数位数
    
    Returns:
        百分比字符串
    """
    return f"{value * 100:.{decimal_places}f}%"


def parse_formatted_number(formatted_str: str) -> Number:
    """
    解析格式化后的数字字符串
    
    Args:
        formatted_str: 格式化后的数字字符串
    
    Returns:
        解析后的数字
    
    Raises:
        ValueError: 当解析失败时抛出
    """
    formatted_str = formatted_str.strip()
    
    # 处理无穷大
    if formatted_str in ['+∞', 'inf', '+inf']:
        return float('inf')
    if formatted_str in ['-∞', '-inf']:
        return float('-inf')
    if formatted_str == 'NaN':
        return float('nan')
    
    # 尝试解析为整数
    try:
        return int(formatted_str)
    except ValueError:
        pass
    
    # 解析为浮点数
    try:
        return float(formatted_str)
    except ValueError:
        raise ValueError(f"无法解析 '{formatted_str}' 为数字")
