"""
输入校验模块

本模块负责验证用户输入的合法性，包括数字格式校验、运算符校验等。
提供输入预处理和格式化功能。

作者: Development Team
版本: 2.0.0
"""

import re
from typing import Union, Optional, Tuple

from calculator_core import (
    BASIC_OPERATIONS, 
    SCIENTIFIC_OPERATIONS,
    InvalidInputError
)


class ValidationError(Exception):
    """输入校验错误"""
    pass


class InputValidator:
    """输入校验器类"""
    
    # 合法运算符集合
    VALID_OPERATORS = set(BASIC_OPERATIONS.keys())
    VALID_FUNCTIONS = set(SCIENTIFIC_OPERATIONS.keys())
    
    # 数字正则表达式模式
    NUMBER_PATTERN = re.compile(
        r'^[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?$'
    )
    
    @classmethod
    def is_valid_number(cls, value: str) -> bool:
        """
        检查字符串是否为有效数字
        
        Args:
            value: 待检查的字符串
        
        Returns:
            是否为有效数字
        """
        if not value or not isinstance(value, str):
            return False
        value = value.strip()
        if not value:
            return False
        return bool(cls.NUMBER_PATTERN.match(value))
    
    @classmethod
    def parse_number(cls, value: str) -> Union[int, float]:
        """
        将字符串解析为数字
        
        Args:
            value: 数字字符串
        
        Returns:
            解析后的数字（整数或浮点数）
        
        Raises:
            ValidationError: 当输入不是有效数字时抛出
        """
        if not cls.is_valid_number(value):
            raise ValidationError(f"'{value}' 不是有效的数字")
        
        value = value.strip()
        
        # 尝试解析为整数
        try:
            if '.' not in value and 'e' not in value.lower():
                return int(value)
        except ValueError:
            pass
        
        # 解析为浮点数
        try:
            return float(value)
        except ValueError:
            raise ValidationError(f"无法将 '{value}' 解析为数字")
    
    @classmethod
    def is_valid_operator(cls, operator: str) -> bool:
        """
        检查是否为有效的基础运算符
        
        Args:
            operator: 运算符字符串
        
        Returns:
            是否为有效运算符
        """
        return operator in cls.VALID_OPERATORS
    
    @classmethod
    def is_valid_function(cls, func_name: str) -> bool:
        """
        检查是否为有效的科学运算函数名
        
        Args:
            func_name: 函数名
        
        Returns:
            是否为有效函数名
        """
        return func_name.lower() in cls.VALID_FUNCTIONS
    
    @classmethod
    def validate_basic_operation(
        cls, 
        num1: str, 
        operator: str, 
        num2: str
    ) -> Tuple[Union[int, float], str, Union[int, float]]:
        """
        校验基础四则运算的输入
        
        Args:
            num1: 第一个操作数字符串
            operator: 运算符
            num2: 第二个操作数字符串
        
        Returns:
            解析后的 (数字1, 运算符, 数字2)
        
        Raises:
            ValidationError: 当输入不合法时抛出
        """
        # 检查空输入
        if not num1.strip():
            raise ValidationError("第一个操作数不能为空")
        if not num2.strip():
            raise ValidationError("第二个操作数不能为空")
        
        # 解析数字
        try:
            n1 = cls.parse_number(num1)
        except ValidationError as e:
            raise ValidationError(f"第一个操作数错误: {e}")
        
        try:
            n2 = cls.parse_number(num2)
        except ValidationError as e:
            raise ValidationError(f"第二个操作数错误: {e}")
        
        # 检查运算符
        if not cls.is_valid_operator(operator):
            raise ValidationError(
                f"无效的运算符 '{operator}'，支持的运算符: {', '.join(cls.VALID_OPERATORS)}"
            )
        
        return n1, operator, n2
    
    @classmethod
    def validate_scientific_operation(
        cls, 
        func_name: str, 
        operand: str
    ) -> Tuple[str, Union[int, float]]:
        """
        校验科学运算的输入
        
        Args:
            func_name: 函数名
            operand: 操作数字符串
        
        Returns:
            解析后的 (函数名, 操作数)
        
        Raises:
            ValidationError: 当输入不合法时抛出
        """
        # 标准化函数名
        func_name = func_name.lower().strip()
        
        # 检查空输入
        if not operand.strip():
            raise ValidationError("操作数不能为空")
        
        # 检查函数名
        if not cls.is_valid_function(func_name):
            raise ValidationError(
                f"无效的函数 '{func_name}'，支持的函数: {', '.join(cls.VALID_FUNCTIONS)}"
            )
        
        # 解析数字
        try:
            num = cls.parse_number(operand)
        except ValidationError as e:
            raise ValidationError(f"操作数错误: {e}")
        
        return func_name, num
    
    @classmethod
    def validate_two_operand_scientific(
        cls,
        func_name: str,
        operand1: str,
        operand2: str
    ) -> Tuple[str, Union[int, float], Union[int, float]]:
        """
        校验需要两个操作数的科学运算（如幂运算）
        
        Args:
            func_name: 函数名
            operand1: 第一个操作数字符串
            operand2: 第二个操作数字符串
        
        Returns:
            解析后的 (函数名, 操作数1, 操作数2)
        
        Raises:
            ValidationError: 当输入不合法时抛出
        """
        func_name = func_name.lower().strip()
        
        if not operand1.strip():
            raise ValidationError("第一个操作数不能为空")
        if not operand2.strip():
            raise ValidationError("第二个操作数不能为空")
        
        if func_name not in cls.VALID_FUNCTIONS:
            raise ValidationError(f"无效的函数 '{func_name}'")
        
        try:
            num1 = cls.parse_number(operand1)
        except ValidationError as e:
            raise ValidationError(f"第一个操作数错误: {e}")
        
        try:
            num2 = cls.parse_number(operand2)
        except ValidationError as e:
            raise ValidationError(f"第二个操作数错误: {e}")
        
        return func_name, num1, num2
    
    @classmethod
    def format_input(cls, user_input: str) -> str:
        """
        格式化用户输入（去除多余空格等）
        
        Args:
            user_input: 原始输入字符串
        
        Returns:
            格式化后的字符串
        """
        if not user_input:
            return ""
        # 去除首尾空格，压缩中间多余空格
        return ' '.join(user_input.split())
    
    @classmethod
    def parse_expression(cls, expression: str) -> Optional[Tuple]:
        """
        解析简单表达式（兼容模式用）
        
        支持的格式:
        - "5 + 3" -> ('+', 5, 3)
        - "sin 30" -> ('sin', 30)
        
        Args:
            expression: 表达式字符串
        
        Returns:
            解析结果元组，解析失败返回None
        """
        expression = cls.format_input(expression)
        if not expression:
            return None
        
        parts = expression.split()
        
        # 尝试解析为函数调用: "sin 30"
        if len(parts) == 2:
            func_name, operand = parts
            if cls.is_valid_function(func_name):
                try:
                    num = cls.parse_number(operand)
                    return (func_name.lower(), num)
                except ValidationError:
                    pass
        
        # 尝试解析为基础运算: "5 + 3"
        if len(parts) == 3:
            num1, op, num2 = parts
            if cls.is_valid_operator(op):
                try:
                    n1 = cls.parse_number(num1)
                    n2 = cls.parse_number(num2)
                    return (op, n1, n2)
                except ValidationError:
                    pass
        
        return None


def validate_menu_choice(choice: str, valid_options: list) -> int:
    """
    验证菜单选择
    
    Args:
        choice: 用户输入
        valid_options: 有效选项列表
    
    Returns:
        有效的选项编号
    
    Raises:
        ValidationError: 当输入无效时抛出
    """
    choice = choice.strip()
    
    if not choice:
        raise ValidationError("请输入选项编号")
    
    try:
        num = int(choice)
    except ValueError:
        raise ValidationError(f"'{choice}' 不是有效的数字")
    
    if num not in valid_options:
        raise ValidationError(f"选项 {num} 不在有效范围内 {valid_options}")
    
    return num
