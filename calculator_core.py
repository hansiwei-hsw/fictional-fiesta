"""
计算器核心运算引擎模块

本模块封装所有数学运算函数，包括基础四则运算和科学运算。
采用函数式编程风格，所有运算函数均为纯函数，便于测试和缓存。

作者: Development Team
版本: 2.0.0
"""

import math
from functools import lru_cache
from typing import Union, Optional, Callable

# 类型别名，提高代码可读性
Number = Union[int, float]


class CalculatorError(Exception):
    """计算器专用异常基类"""
    pass


class DivisionByZeroError(CalculatorError):
    """除零错误"""
    pass


class NegativeNumberError(CalculatorError):
    """负数错误（用于开方、对数等运算）"""
    pass


class InvalidInputError(CalculatorError):
    """无效输入错误"""
    pass


# ==================== 基础四则运算 ====================

def add(a: Number, b: Number) -> Number:
    """
    加法运算
    
    Args:
        a: 第一个操作数
        b: 第二个操作数
    
    Returns:
        两数之和
    """
    return a + b


def subtract(a: Number, b: Number) -> Number:
    """
    减法运算
    
    Args:
        a: 被减数
        b: 减数
    
    Returns:
        两数之差
    """
    return a - b


def multiply(a: Number, b: Number) -> Number:
    """
    乘法运算
    
    Args:
        a: 第一个操作数
        b: 第二个操作数
    
    Returns:
        两数之积
    """
    return a * b


def divide(a: Number, b: Number) -> Number:
    """
    除法运算
    
    Args:
        a: 被除数
        b: 除数
    
    Returns:
        两数之商
    
    Raises:
        DivisionByZeroError: 当除数为零时抛出
    """
    if b == 0:
        raise DivisionByZeroError("除数不能为零")
    return a / b


# ==================== 科学运算 ====================

@lru_cache(maxsize=128)
def sin(angle: float, use_degrees: bool = True) -> float:
    """
    正弦函数
    
    Args:
        angle: 角度值（度数或弧度）
        use_degrees: 是否使用度数，默认为True
    
    Returns:
        正弦值
    """
    if use_degrees:
        angle = math.radians(angle)
    return math.sin(angle)


@lru_cache(maxsize=128)
def cos(angle: float, use_degrees: bool = True) -> float:
    """
    余弦函数
    
    Args:
        angle: 角度值（度数或弧度）
        use_degrees: 是否使用度数，默认为True
    
    Returns:
        余弦值
    """
    if use_degrees:
        angle = math.radians(angle)
    return math.cos(angle)


@lru_cache(maxsize=128)
def tan(angle: float, use_degrees: bool = True) -> float:
    """
    正切函数
    
    Args:
        angle: 角度值（度数或弧度）
        use_degrees: 是否使用度数，默认为True
    
    Returns:
        正切值
    
    Raises:
        InvalidInputError: 当角度为90°+k*180°（度数）或π/2+kπ（弧度）时抛出
    """
    if use_degrees:
        # 检查是否为奇数倍的90度
        if abs(angle % 180 - 90) < 1e-10 or abs(angle % 180 + 90) < 1e-10:
            raise InvalidInputError("正切函数在90°+k·180°处无定义")
        angle = math.radians(angle)
    else:
        # 检查是否为奇数倍的π/2
        if abs(angle % math.pi - math.pi/2) < 1e-10:
            raise InvalidInputError("正切函数在π/2+k·π处无定义")
    return math.tan(angle)


def ln(x: Number) -> float:
    """
    自然对数
    
    Args:
        x: 输入值
    
    Returns:
        ln(x)的值
    
    Raises:
        NegativeNumberError: 当x≤0时抛出
    """
    if x <= 0:
        raise NegativeNumberError("自然对数的输入必须大于0")
    return math.log(x)


def log10(x: Number) -> float:
    """
    常用对数（以10为底）
    
    Args:
        x: 输入值
    
    Returns:
        log₁₀(x)的值
    
    Raises:
        NegativeNumberError: 当x≤0时抛出
    """
    if x <= 0:
        raise NegativeNumberError("对数的输入必须大于0")
    return math.log10(x)


def power(base: Number, exponent: Number) -> Number:
    """
    幂运算
    
    Args:
        base: 底数
        exponent: 指数
    
    Returns:
        base^exponent的值
    """
    # 处理0的负数次方特殊情况
    if base == 0 and exponent < 0:
        raise InvalidInputError("0的负数次方无定义")
    return base ** exponent


def sqrt(x: Number) -> float:
    """
    平方根运算
    
    Args:
        x: 被开方数
    
    Returns:
        √x的值
    
    Raises:
        NegativeNumberError: 当x<0时抛出
    """
    if x < 0:
        raise NegativeNumberError("负数不能开平方")
    return math.sqrt(x)


def factorial(n: int) -> int:
    """
    阶乘运算
    
    Args:
        n: 非负整数
    
    Returns:
        n!的值
    
    Raises:
        InvalidInputError: 当n不是整数时抛出
        NegativeNumberError: 当n<0时抛出
    """
    if not isinstance(n, int):
        raise InvalidInputError("阶乘只接受整数")
    if n < 0:
        raise NegativeNumberError("负数没有阶乘")
    if n > 170:
        raise InvalidInputError("输入过大，阶乘结果超出浮点数表示范围")
    return math.factorial(n)


# ==================== 运算映射表 ====================

# 基础运算操作符映射
BASIC_OPERATIONS: dict[str, Callable] = {
    '+': add,
    '-': subtract,
    '*': multiply,
    '/': divide,
}

# 科学运算函数映射
SCIENTIFIC_OPERATIONS: dict[str, Callable] = {
    'sin': sin,
    'cos': cos,
    'tan': tan,
    'ln': ln,
    'log': log10,
    'pow': power,
    'sqrt': sqrt,
    'fact': factorial,
}

# 所有可用运算
ALL_OPERATIONS = {**BASIC_OPERATIONS, **SCIENTIFIC_OPERATIONS}


def get_operation(name: str) -> Optional[Callable]:
    """
    根据名称获取运算函数
    
    Args:
        name: 运算名称或符号
    
    Returns:
        对应的运算函数，如果不存在则返回None
    """
    return ALL_OPERATIONS.get(name)


def list_operations() -> dict[str, list[str]]:
    """
    列出所有可用运算
    
    Returns:
        包含基础运算和科学运算分类的字典
    """
    return {
        'basic': list(BASIC_OPERATIONS.keys()),
        'scientific': list(SCIENTIFIC_OPERATIONS.keys()),
    }


def clear_cache():
    """清除缓存（用于科学运算函数的LRU缓存）"""
    sin.cache_clear()
    cos.cache_clear()
    tan.cache_clear()
