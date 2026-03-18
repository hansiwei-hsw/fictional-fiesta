"""
input_validator.py - 输入校验模块

该模块负责：
- 验证数字输入的合法性
- 验证运算符的合法性
- 格式化用户输入
- 提供友好的错误提示

遵循PEP8规范，所有函数均添加文档字符串。
"""

import re
from typing import Union, Tuple, Optional, List


class InputValidator:
    """
    输入校验器类
    
    提供各种输入验证和格式化功能。
    """
    
    VALID_OPERATORS = {
        '+', '-', '*', '/', '%', '^',
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
        'ln', 'log', 'log10',
        'sqrt', 'root',
        'fact', 'factorial',
        'abs', 'exp', 'floor', 'ceil', 'round',
        'perm', 'comb'
    }
    
    NUMBER_PATTERN = re.compile(
        r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$'
    )
    
    def __init__(self, decimal_separator: str = '.'):
        """
        初始化输入校验器
        
        Args:
            decimal_separator: 小数分隔符，默认为'.'
        """
        self._decimal_separator = decimal_separator
    
    def validate_number(self, value: str) -> Tuple[bool, Optional[float], str]:
        """
        验证数字输入
        
        Args:
            value: 用户输入的字符串
            
        Returns:
            (是否有效, 转换后的数值, 错误信息)
        """
        if value is None or value.strip() == '':
            return False, None, "输入不能为空"
        
        value = value.strip()
        
        if self._decimal_separator != '.':
            value = value.replace(self._decimal_separator, '.')
        
        if not self.NUMBER_PATTERN.match(value):
            try:
                num = float(value)
                return True, num, ""
            except ValueError:
                return False, None, f"'{value}' 不是有效的数字格式"
        
        try:
            num = float(value)
            return True, num, ""
        except ValueError:
            return False, None, f"'{value}' 无法转换为数字"
    
    def validate_integer(self, value: str, min_val: Optional[int] = None, 
                         max_val: Optional[int] = None) -> Tuple[bool, Optional[int], str]:
        """
        验证整数输入
        
        Args:
            value: 用户输入的字符串
            min_val: 最小值（可选）
            max_val: 最大值（可选）
            
        Returns:
            (是否有效, 转换后的整数, 错误信息)
        """
        is_valid, num, error = self.validate_number(value)
        
        if not is_valid:
            return False, None, error
        
        if not float(num).is_integer():
            return False, None, f"'{value}' 不是整数"
        
        int_val = int(num)
        
        if min_val is not None and int_val < min_val:
            return False, None, f"输入值 {int_val} 小于最小值 {min_val}"
        
        if max_val is not None and int_val > max_val:
            return False, None, f"输入值 {int_val} 大于最大值 {max_val}"
        
        return True, int_val, ""
    
    def validate_positive_number(self, value: str, 
                                  allow_zero: bool = False) -> Tuple[bool, Optional[float], str]:
        """
        验证正数输入
        
        Args:
            value: 用户输入的字符串
            allow_zero: 是否允许零
            
        Returns:
            (是否有效, 转换后的数值, 错误信息)
        """
        is_valid, num, error = self.validate_number(value)
        
        if not is_valid:
            return False, None, error
        
        if allow_zero:
            if num < 0:
                return False, None, f"输入值必须为非负数，当前: {num}"
        else:
            if num <= 0:
                return False, None, f"输入值必须为正数，当前: {num}"
        
        return True, num, ""
    
    def validate_non_negative_number(self, value: str) -> Tuple[bool, Optional[float], str]:
        """
        验证非负数输入
        
        Args:
            value: 用户输入的字符串
            
        Returns:
            (是否有效, 转换后的数值, 错误信息)
        """
        return self.validate_positive_number(value, allow_zero=True)
    
    def validate_operator(self, op: str) -> Tuple[bool, str]:
        """
        验证运算符
        
        Args:
            op: 运算符字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if op is None or op.strip() == '':
            return False, "运算符不能为空"
        
        op = op.strip().lower()
        
        if op in self.VALID_OPERATORS:
            return True, ""
        
        return False, f"'{op}' 不是有效的运算符"
    
    def validate_menu_choice(self, choice: str, 
                             valid_range: range) -> Tuple[bool, Optional[int], str]:
        """
        验证菜单选择
        
        Args:
            choice: 用户输入的选择
            valid_range: 有效范围
            
        Returns:
            (是否有效, 选择值, 错误信息)
        """
        if choice is None or choice.strip() == '':
            return False, None, "请输入选项编号"
        
        choice = choice.strip()
        
        is_valid, num, error = self.validate_integer(choice)
        
        if not is_valid:
            return False, None, f"请输入有效的数字选项"
        
        if num not in valid_range:
            return False, None, f"选项 {num} 不在有效范围内 ({valid_range.start}-{valid_range.stop - 1})"
        
        return True, num, ""
    
    def parse_expression(self, expression: str) -> Tuple[bool, List[str], str]:
        """
        解析数学表达式
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            (是否有效, 解析后的token列表, 错误信息)
        """
        if expression is None or expression.strip() == '':
            return False, [], "表达式不能为空"
        
        expression = expression.strip()
        
        tokens = []
        current_token = ''
        
        for char in expression:
            if char in '+-*/^%()':
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                tokens.append(char)
            elif char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
        
        for token in tokens:
            if token not in '+-*/^%()':
                is_valid, _, _ = self.validate_number(token)
                if not is_valid and token.lower() not in self.VALID_OPERATORS:
                    return False, [], f"无效的token: '{token}'"
        
        return True, tokens, ""
    
    def format_input(self, value: str) -> str:
        """
        格式化用户输入
        
        Args:
            value: 原始输入
            
        Returns:
            格式化后的字符串
        """
        if value is None:
            return ''
        
        value = value.strip()
        
        if self._decimal_separator != '.':
            value = value.replace(self._decimal_separator, '.')
        
        value = re.sub(r'\s+', ' ', value)
        
        return value
    
    def sanitize_input(self, value: str) -> str:
        """
        清理输入中的危险字符
        
        Args:
            value: 原始输入
            
        Returns:
            清理后的字符串
        """
        if value is None:
            return ''
        
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '`', '|']
        result = value
        
        for char in dangerous_chars:
            result = result.replace(char, '')
        
        return result
    
    def validate_angle_input(self, value: str, 
                             mode: str = 'degree') -> Tuple[bool, Optional[float], str]:
        """
        验证角度输入
        
        Args:
            value: 用户输入的角度值
            mode: 角度模式 ('degree' 或 'radian')
            
        Returns:
            (是否有效, 角度值, 错误信息)
        """
        is_valid, num, error = self.validate_number(value)
        
        if not is_valid:
            return False, None, error
        
        if mode == 'degree':
            pass
        
        return True, num, ""
    
    def validate_base_input(self, value: str) -> Tuple[bool, Optional[float], str]:
        """
        验证对数底数输入
        
        Args:
            value: 用户输入的底数
            
        Returns:
            (是否有效, 底数值, 错误信息)
        """
        is_valid, num, error = self.validate_number(value)
        
        if not is_valid:
            return False, None, error
        
        if num <= 0:
            return False, None, f"对数底数必须大于0，当前: {num}"
        
        if num == 1:
            return False, None, "对数底数不能为1"
        
        return True, num, ""
    
    def validate_power_exponent(self, value: str, 
                                 base: float) -> Tuple[bool, Optional[float], str]:
        """
        验证幂运算指数
        
        Args:
            value: 用户输入的指数
            base: 底数
            
        Returns:
            (是否有效, 指数值, 错误信息)
        """
        is_valid, num, error = self.validate_number(value)
        
        if not is_valid:
            return False, None, error
        
        if base < 0 and not float(num).is_integer():
            return False, None, f"负数的非整数次幂无实数结果: {base}^{num}"
        
        return True, num, ""
    
    def validate_root_index(self, value: str, 
                            radicand: float) -> Tuple[bool, Optional[int], str]:
        """
        验证根指数
        
        Args:
            value: 用户输入的根指数
            radicand: 被开方数
            
        Returns:
            (是否有效, 根指数, 错误信息)
        """
        is_valid, num, error = self.validate_integer(value, min_val=1)
        
        if not is_valid:
            return False, None, error
        
        if radicand < 0 and num % 2 == 0:
            return False, None, f"负数不能开偶次方根: {radicand}的{num}次方根"
        
        return True, num, ""


class LegacyInputParser:
    """
    兼容模式输入解析器
    
    用于解析旧版本计算器的输入格式。
    """
    
    def __init__(self):
        """初始化兼容模式解析器"""
        self._validator = InputValidator()
    
    def parse_legacy_format(self, expression: str) -> Tuple[bool, dict, str]:
        """
        解析旧版本格式表达式
        
        旧版本格式: "数字1 运算符 数字2" 或 "运算符 数字"
        
        Args:
            expression: 表达式字符串
            
        Returns:
            (是否有效, 解析结果字典, 错误信息)
        """
        if expression is None or expression.strip() == '':
            return False, {}, "表达式不能为空"
        
        expression = expression.strip()
        parts = expression.split()
        
        if len(parts) == 2:
            op, num_str = parts
            is_valid, num, error = self._validator.validate_number(num_str)
            if not is_valid:
                return False, {}, error
            return True, {'operator': op.lower(), 'operand': num}, ""
        
        elif len(parts) == 3:
            num1_str, op, num2_str = parts
            is_valid1, num1, error1 = self._validator.validate_number(num1_str)
            is_valid2, num2, error2 = self._validator.validate_number(num2_str)
            
            if not is_valid1:
                return False, {}, error1
            if not is_valid2:
                return False, {}, error2
            
            return True, {
                'operator': op.lower(),
                'operand1': num1,
                'operand2': num2
            }, ""
        
        else:
            return False, {}, f"无法解析表达式: '{expression}'，请使用格式: '数字1 运算符 数字2' 或 '运算符 数字'"


def create_validator(decimal_separator: str = '.') -> InputValidator:
    """
    工厂函数：创建输入校验器实例
    
    Args:
        decimal_separator: 小数分隔符
        
    Returns:
        InputValidator 实例
    """
    return InputValidator(decimal_separator=decimal_separator)
