"""
result_formatter.py - 结果格式化模块

该模块负责：
- 格式化计算结果输出
- 控制小数位数
- 科学计数法自动切换
- 处理特殊值（无穷大、NaN等）

遵循PEP8规范，所有函数均添加文档字符串。
"""

import math
from typing import Union, Optional


class ResultFormatter:
    """
    结果格式化器类
    
    提供多种格式化选项，支持科学计数法、小数位数控制等。
    """
    
    SCIENTIFIC_THRESHOLD_HIGH = 1e10
    SCIENTIFIC_THRESHOLD_LOW = 1e-6
    
    def __init__(self, decimal_places: int = 4, 
                 use_scientific: bool = True,
                 scientific_threshold_high: float = 1e10,
                 scientific_threshold_low: float = 1e-6,
                 strip_trailing_zeros: bool = True,
                 thousands_separator: str = ''):
        """
        初始化结果格式化器
        
        Args:
            decimal_places: 默认保留小数位数
            use_scientific: 是否使用科学计数法
            scientific_threshold_high: 科学计数法高阈值
            scientific_threshold_low: 科学计数法低阈值
            strip_trailing_zeros: 是否移除尾部多余的零
            thousands_separator: 千位分隔符
        """
        self._decimal_places = decimal_places
        self._use_scientific = use_scientific
        self._scientific_threshold_high = scientific_threshold_high
        self._scientific_threshold_low = scientific_threshold_low
        self._strip_trailing_zeros = strip_trailing_zeros
        self._thousands_separator = thousands_separator
    
    @property
    def decimal_places(self) -> int:
        """获取当前小数位数设置"""
        return self._decimal_places
    
    @decimal_places.setter
    def decimal_places(self, value: int) -> None:
        """
        设置小数位数
        
        Args:
            value: 小数位数，必须为非负整数
            
        Raises:
            ValueError: 当值无效时
        """
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"小数位数必须为非负整数，当前: {value}")
        self._decimal_places = value
    
    @property
    def use_scientific(self) -> bool:
        """获取是否使用科学计数法"""
        return self._use_scientific
    
    @use_scientific.setter
    def use_scientific(self, value: bool) -> None:
        """设置是否使用科学计数法"""
        self._use_scientific = value
    
    def format(self, value: Union[int, float], 
               decimal_places: Optional[int] = None,
               force_scientific: bool = False) -> str:
        """
        格式化数值
        
        Args:
            value: 要格式化的数值
            decimal_places: 小数位数（可选，使用默认值）
            force_scientific: 是否强制使用科学计数法
            
        Returns:
            格式化后的字符串
        """
        if decimal_places is None:
            decimal_places = self._decimal_places
        
        if isinstance(value, int):
            return self._format_integer(value)
        
        if math.isnan(value):
            return "NaN"
        
        if math.isinf(value):
            return "+∞" if value > 0 else "-∞"
        
        abs_value = abs(value)
        
        use_sci = force_scientific or (
            self._use_scientific and (
                abs_value >= self._scientific_threshold_high or 
                (abs_value > 0 and abs_value < self._scientific_threshold_low)
            )
        )
        
        if use_sci:
            return self._format_scientific(value, decimal_places)
        
        return self._format_decimal(value, decimal_places)
    
    def _format_integer(self, value: int) -> str:
        """
        格式化整数
        
        Args:
            value: 整数值
            
        Returns:
            格式化后的字符串
        """
        if self._thousands_separator:
            return f"{value:,}".replace(',', self._thousands_separator)
        return str(value)
    
    def _format_decimal(self, value: float, decimal_places: int) -> str:
        """
        格式化小数
        
        Args:
            value: 小数值
            decimal_places: 小数位数
            
        Returns:
            格式化后的字符串
        """
        if value == int(value) and decimal_places == 0:
            return str(int(value))
        
        format_str = f"{{:.{decimal_places}f}}"
        result = format_str.format(value)
        
        if self._strip_trailing_zeros:
            if '.' in result:
                result = result.rstrip('0').rstrip('.')
        
        if self._thousands_separator and '.' not in result:
            result = f"{int(float(result)):,}".replace(',', self._thousands_separator)
        
        return result
    
    def _format_scientific(self, value: float, decimal_places: int) -> str:
        """
        格式化为科学计数法
        
        Args:
            value: 数值
            decimal_places: 小数位数
            
        Returns:
            科学计数法字符串
        """
        if value == 0:
            return "0"
        
        format_str = f"{{:.{decimal_places}e}}"
        result = format_str.format(value)
        
        result = result.replace('e+', 'E+').replace('e-', 'E-')
        
        parts = result.split('E')
        if len(parts) == 2:
            mantissa = parts[0]
            exponent = parts[1]
            
            if self._strip_trailing_zeros and '.' in mantissa:
                mantissa = mantissa.rstrip('0').rstrip('.')
            
            if exponent.startswith('+'):
                exponent = exponent[1:]
            
            exponent = exponent.lstrip('0') or '0'
            
            result = f"{mantissa}E{exponent}"
        
        return result
    
    def format_percentage(self, value: float, 
                          decimal_places: Optional[int] = None) -> str:
        """
        格式化为百分比
        
        Args:
            value: 数值（0.5 表示 50%）
            decimal_places: 小数位数
            
        Returns:
            百分比字符串
        """
        if decimal_places is None:
            decimal_places = self._decimal_places
        
        percentage = value * 100
        return f"{self._format_decimal(percentage, decimal_places)}%"
    
    def format_with_unit(self, value: float, unit: str,
                         decimal_places: Optional[int] = None) -> str:
        """
        格式化并添加单位
        
        Args:
            value: 数值
            unit: 单位字符串
            decimal_places: 小数位数
            
        Returns:
            带单位的字符串
        """
        formatted = self.format(value, decimal_places)
        return f"{formatted} {unit}"
    
    def format_angle(self, value: float, mode: str = 'degree',
                     decimal_places: Optional[int] = None) -> str:
        """
        格式化角度值
        
        Args:
            value: 角度值
            mode: 模式 ('degree' 或 'radian')
            decimal_places: 小数位数
            
        Returns:
            格式化后的角度字符串
        """
        if decimal_places is None:
            decimal_places = self._decimal_places
        
        formatted = self._format_decimal(value, decimal_places)
        
        if mode == 'degree':
            return f"{formatted}°"
        else:
            return f"{formatted} rad"
    
    def format_complex_result(self, real: float, imag: float,
                              decimal_places: Optional[int] = None) -> str:
        """
        格式化复数结果（虚部）
        
        Args:
            real: 实部
            imag: 虚部
            decimal_places: 小数位数
            
        Returns:
            复数字符串
        """
        if decimal_places is None:
            decimal_places = self._decimal_places
        
        real_str = self._format_decimal(real, decimal_places)
        imag_str = self._format_decimal(abs(imag), decimal_places)
        
        if imag >= 0:
            return f"{real_str} + {imag_str}i"
        else:
            return f"{real_str} - {imag_str}i"
    
    def format_error(self, error_message: str, 
                     error_code: Optional[str] = None) -> str:
        """
        格式化错误信息
        
        Args:
            error_message: 错误信息
            error_code: 错误代码（可选）
            
        Returns:
            格式化后的错误字符串
        """
        if error_code:
            return f"[错误 {error_code}] {error_message}"
        return f"[错误] {error_message}"
    
    def format_operation(self, operator: str, operands: list,
                         result: float,
                         decimal_places: Optional[int] = None) -> str:
        """
        格式化完整运算表达式
        
        Args:
            operator: 运算符
            operands: 操作数列表
            result: 结果
            decimal_places: 小数位数
            
        Returns:
            格式化后的运算表达式
        """
        if decimal_places is None:
            decimal_places = self._decimal_places
        
        operands_str = ', '.join([self._format_decimal(op, decimal_places) 
                                   if isinstance(op, float) else str(op) 
                                   for op in operands])
        result_str = self.format(result, decimal_places)
        
        if len(operands) == 1:
            return f"{operator}({operands_str}) = {result_str}"
        elif len(operands) == 2:
            op_symbol = self._get_operator_symbol(operator)
            if op_symbol:
                return f"{operands[0]} {op_symbol} {operands[1]} = {result_str}"
            return f"{operator}({operands_str}) = {result_str}"
        else:
            return f"{operator}({operands_str}) = {result_str}"
    
    def _get_operator_symbol(self, operator: str) -> Optional[str]:
        """
        获取运算符符号
        
        Args:
            operator: 运算符名称
            
        Returns:
            运算符符号，如果不存在返回None
        """
        symbols = {
            'add': '+',
            'subtract': '-',
            'multiply': '×',
            'divide': '÷',
            'power': '^',
            'mod': '%',
        }
        return symbols.get(operator.lower())
    
    def format_table_row(self, values: list, widths: list,
                         decimal_places: Optional[int] = None) -> str:
        """
        格式化表格行
        
        Args:
            values: 值列表
            widths: 列宽列表
            decimal_places: 小数位数
            
        Returns:
            格式化后的表格行
        """
        if decimal_places is None:
            decimal_places = self._decimal_places
        
        formatted_values = []
        for i, value in enumerate(values):
            if isinstance(value, (int, float)):
                formatted = self.format(value, decimal_places)
            else:
                formatted = str(value)
            
            width = widths[i] if i < len(widths) else len(formatted)
            formatted_values.append(formatted.ljust(width))
        
        return ' | '.join(formatted_values)
    
    def parse_formatted_number(self, formatted: str) -> float:
        """
        解析格式化后的数字字符串
        
        Args:
            formatted: 格式化后的字符串
            
        Returns:
            数值
            
        Raises:
            ValueError: 当无法解析时
        """
        formatted = formatted.strip()
        
        if formatted in ('NaN', 'nan'):
            return float('nan')
        if formatted in ('+∞', 'inf', '+inf'):
            return float('inf')
        if formatted in ('-∞', '-inf'):
            return float('-inf')
        
        formatted = formatted.replace(',', '').replace(' ', '')
        formatted = formatted.replace('°', '').replace('rad', '')
        formatted = formatted.replace('%', '')
        
        if 'E' in formatted.upper():
            formatted = formatted.replace('E', 'e').replace('e+', 'e')
        
        try:
            if '%' in formatted:
                return float(formatted.replace('%', '')) / 100
            return float(formatted)
        except ValueError:
            raise ValueError(f"无法解析数字: '{formatted}'")


def create_formatter(decimal_places: int = 4, 
                     use_scientific: bool = True) -> ResultFormatter:
    """
    工厂函数：创建结果格式化器实例
    
    Args:
        decimal_places: 小数位数
        use_scientific: 是否使用科学计数法
        
    Returns:
        ResultFormatter 实例
    """
    return ResultFormatter(
        decimal_places=decimal_places,
        use_scientific=use_scientific
    )
