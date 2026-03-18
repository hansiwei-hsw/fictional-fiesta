"""
calculator_core.py - 核心运算引擎模块

该模块封装所有运算函数，包括：
- 基础四则运算
- 科学运算（三角函数、对数、幂运算、阶乘、开方等）
- 缓存机制优化

遵循PEP8规范，所有函数均添加文档字符串。
"""

import math
from functools import lru_cache
from typing import Union, Tuple, Optional


class CalculatorCore:
    """
    科学计算器核心引擎类
    
    支持基础四则运算和科学运算，内置缓存机制优化性能。
    """
    
    def __init__(self, angle_mode: str = 'degree', use_cache: bool = True):
        """
        初始化计算器核心
        
        Args:
            angle_mode: 角度模式，'degree'（角度）或 'radian'（弧度）
            use_cache: 是否启用缓存机制
        """
        self._angle_mode = angle_mode
        self._use_cache = use_cache
        self._cache = {} if use_cache else None
        self._cache_hits = 0
        self._cache_misses = 0
    
    @property
    def angle_mode(self) -> str:
        """获取当前角度模式"""
        return self._angle_mode
    
    @angle_mode.setter
    def angle_mode(self, mode: str) -> None:
        """
        设置角度模式
        
        Args:
            mode: 'degree' 或 'radian'
        
        Raises:
            ValueError: 当模式不是有效值时
        """
        if mode not in ('degree', 'radian'):
            raise ValueError(f"无效的角度模式: {mode}，请使用 'degree' 或 'radian'")
        self._angle_mode = mode
        if self._use_cache:
            self._cache.clear()
    
    def _to_radian(self, value: float) -> float:
        """
        将角度转换为弧度（如果当前模式为角度）
        
        Args:
            value: 输入值
            
        Returns:
            转换后的弧度值
        """
        if self._angle_mode == 'degree':
            return math.radians(value)
        return value
    
    def _get_cache_key(self, func_name: str, *args) -> Tuple:
        """
        生成缓存键
        
        Args:
            func_name: 函数名称
            *args: 函数参数
            
        Returns:
            缓存键元组
        """
        return (func_name, self._angle_mode, *args)
    
    def _get_from_cache(self, key: Tuple) -> Optional[float]:
        """
        从缓存获取结果
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的结果，如果不存在返回None
        """
        if not self._use_cache:
            return None
        
        if key in self._cache:
            self._cache_hits += 1
            return self._cache[key]
        
        self._cache_misses += 1
        return None
    
    def _set_cache(self, key: Tuple, value: float) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 要缓存的值
        """
        if self._use_cache:
            self._cache[key] = value
    
    def get_cache_stats(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            包含缓存命中、未命中次数和命中率的字典
        """
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        return {
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_rate': hit_rate,
            'cache_size': len(self._cache) if self._cache else 0
        }
    
    def clear_cache(self) -> None:
        """清空缓存"""
        if self._use_cache and self._cache:
            self._cache.clear()
            self._cache_hits = 0
            self._cache_misses = 0
    
    # ==================== 基础四则运算 ====================
    
    def add(self, a: float, b: float) -> float:
        """
        加法运算
        
        Args:
            a: 第一个操作数
            b: 第二个操作数
            
        Returns:
            a + b 的结果
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """
        减法运算
        
        Args:
            a: 被减数
            b: 减数
            
        Returns:
            a - b 的结果
        """
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """
        乘法运算
        
        Args:
            a: 第一个操作数
            b: 第二个操作数
            
        Returns:
            a * b 的结果
        """
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """
        除法运算
        
        Args:
            a: 被除数
            b: 除数
            
        Returns:
            a / b 的结果
            
        Raises:
            ZeroDivisionError: 当除数为0时
        """
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        return a / b
    
    # ==================== 三角函数 ====================
    
    def sin(self, x: float) -> float:
        """
        正弦函数
        
        Args:
            x: 角度或弧度值（取决于当前角度模式）
            
        Returns:
            sin(x) 的值
        """
        cache_key = self._get_cache_key('sin', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        radian = self._to_radian(x)
        result = math.sin(radian)
        self._set_cache(cache_key, result)
        return result
    
    def cos(self, x: float) -> float:
        """
        余弦函数
        
        Args:
            x: 角度或弧度值（取决于当前角度模式）
            
        Returns:
            cos(x) 的值
        """
        cache_key = self._get_cache_key('cos', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        radian = self._to_radian(x)
        result = math.cos(radian)
        self._set_cache(cache_key, result)
        return result
    
    def tan(self, x: float) -> float:
        """
        正切函数
        
        Args:
            x: 角度或弧度值（取决于当前角度模式）
            
        Returns:
            tan(x) 的值
            
        Raises:
            ValueError: 当x为90°+k*180°（正切无定义）时
        """
        cache_key = self._get_cache_key('tan', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        radian = self._to_radian(x)
        
        if self._angle_mode == 'degree':
            if abs(x % 180) == 90:
                raise ValueError(f"正切函数在 {x}° 处无定义")
        else:
            tolerance = 1e-10
            if abs(math.cos(radian)) < tolerance:
                raise ValueError(f"正切函数在 {x} 弧度处无定义")
        
        result = math.tan(radian)
        self._set_cache(cache_key, result)
        return result
    
    # ==================== 反三角函数 ====================
    
    def asin(self, x: float) -> float:
        """
        反正弦函数
        
        Args:
            x: 输入值，范围 [-1, 1]
            
        Returns:
            arcsin(x) 的值（角度或弧度）
            
        Raises:
            ValueError: 当x超出 [-1, 1] 范围时
        """
        if x < -1 or x > 1:
            raise ValueError(f"反正弦函数输入必须在 [-1, 1] 范围内，当前输入: {x}")
        
        cache_key = self._get_cache_key('asin', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.asin(x)
        if self._angle_mode == 'degree':
            result = math.degrees(result)
        self._set_cache(cache_key, result)
        return result
    
    def acos(self, x: float) -> float:
        """
        反余弦函数
        
        Args:
            x: 输入值，范围 [-1, 1]
            
        Returns:
            arccos(x) 的值（角度或弧度）
            
        Raises:
            ValueError: 当x超出 [-1, 1] 范围时
        """
        if x < -1 or x > 1:
            raise ValueError(f"反余弦函数输入必须在 [-1, 1] 范围内，当前输入: {x}")
        
        cache_key = self._get_cache_key('acos', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.acos(x)
        if self._angle_mode == 'degree':
            result = math.degrees(result)
        self._set_cache(cache_key, result)
        return result
    
    def atan(self, x: float) -> float:
        """
        反正切函数
        
        Args:
            x: 输入值
            
        Returns:
            arctan(x) 的值（角度或弧度）
        """
        cache_key = self._get_cache_key('atan', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.atan(x)
        if self._angle_mode == 'degree':
            result = math.degrees(result)
        self._set_cache(cache_key, result)
        return result
    
    # ==================== 对数运算 ====================
    
    def ln(self, x: float) -> float:
        """
        自然对数（以e为底）
        
        Args:
            x: 输入值，必须大于0
            
        Returns:
            ln(x) 的值
            
        Raises:
            ValueError: 当x <= 0时
        """
        if x <= 0:
            raise ValueError(f"对数函数输入必须大于0，当前输入: {x}")
        
        cache_key = self._get_cache_key('ln', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.log(x)
        self._set_cache(cache_key, result)
        return result
    
    def log10(self, x: float) -> float:
        """
        常用对数（以10为底）
        
        Args:
            x: 输入值，必须大于0
            
        Returns:
            log10(x) 的值
            
        Raises:
            ValueError: 当x <= 0时
        """
        if x <= 0:
            raise ValueError(f"对数函数输入必须大于0，当前输入: {x}")
        
        cache_key = self._get_cache_key('log10', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.log10(x)
        self._set_cache(cache_key, result)
        return result
    
    def log(self, x: float, base: float) -> float:
        """
        任意底对数
        
        Args:
            x: 输入值，必须大于0
            base: 底数，必须大于0且不等于1
            
        Returns:
            log_base(x) 的值
            
        Raises:
            ValueError: 当参数不满足条件时
        """
        if x <= 0:
            raise ValueError(f"对数函数输入必须大于0，当前输入: {x}")
        if base <= 0 or base == 1:
            raise ValueError(f"对数底数必须大于0且不等于1，当前底数: {base}")
        
        cache_key = self._get_cache_key('log', x, base)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.log(x) / math.log(base)
        self._set_cache(cache_key, result)
        return result
    
    # ==================== 幂运算与开方 ====================
    
    def power(self, x: float, y: float) -> float:
        """
        幂运算 x^y
        
        Args:
            x: 底数
            y: 指数
            
        Returns:
            x^y 的值
            
        Raises:
            ValueError: 当底数为负数且指数为非整数时
        """
        if x < 0 and not y.is_integer():
            raise ValueError(f"负数的非整数次幂无实数结果: {x}^{y}")
        
        cache_key = self._get_cache_key('power', x, y)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.pow(x, y)
        self._set_cache(cache_key, result)
        return result
    
    def sqrt(self, x: float) -> float:
        """
        平方根
        
        Args:
            x: 输入值，必须非负
            
        Returns:
            √x 的值
            
        Raises:
            ValueError: 当x为负数时
        """
        if x < 0:
            raise ValueError(f"平方根输入不能为负数，当前输入: {x}")
        
        cache_key = self._get_cache_key('sqrt', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.sqrt(x)
        self._set_cache(cache_key, result)
        return result
    
    def nth_root(self, x: float, n: int) -> float:
        """
        n次方根
        
        Args:
            x: 被开方数
            n: 根指数
            
        Returns:
            x的n次方根
            
        Raises:
            ValueError: 当参数不满足条件时
        """
        if n == 0:
            raise ValueError("根指数不能为0")
        if n < 0:
            raise ValueError("根指数必须为正整数")
        if x < 0 and n % 2 == 0:
            raise ValueError(f"负数不能开偶次方根: {x}的{n}次方根")
        
        cache_key = self._get_cache_key('nth_root', x, n)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        if x >= 0:
            result = x ** (1 / n)
        else:
            result = -((-x) ** (1 / n))
        
        self._set_cache(cache_key, result)
        return result
    
    # ==================== 阶乘与组合 ====================
    
    def factorial(self, n: int) -> int:
        """
        阶乘运算
        
        Args:
            n: 非负整数
            
        Returns:
            n! 的值
            
        Raises:
            ValueError: 当n为负数或非整数时
        """
        if not isinstance(n, (int, float)) or (isinstance(n, float) and not n.is_integer()):
            raise ValueError(f"阶乘输入必须为整数，当前输入: {n}")
        
        n = int(n)
        
        if n < 0:
            raise ValueError(f"阶乘输入不能为负数，当前输入: {n}")
        
        if n > 170:
            raise ValueError(f"阶乘结果过大，最大支持170!，当前输入: {n}")
        
        cache_key = self._get_cache_key('factorial', n)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.factorial(n)
        self._set_cache(cache_key, result)
        return result
    
    def permutation(self, n: int, r: int) -> int:
        """
        排列数 P(n, r) = n! / (n-r)!
        
        Args:
            n: 总数
            r: 选取数
            
        Returns:
            排列数
            
        Raises:
            ValueError: 当参数不满足条件时
        """
        if n < 0 or r < 0:
            raise ValueError("排列数参数必须为非负整数")
        if r > n:
            raise ValueError(f"选取数不能大于总数: r={r} > n={n}")
        
        return self.factorial(n) // self.factorial(n - r)
    
    def combination(self, n: int, r: int) -> int:
        """
        组合数 C(n, r) = n! / (r! * (n-r)!)
        
        Args:
            n: 总数
            r: 选取数
            
        Returns:
            组合数
            
        Raises:
            ValueError: 当参数不满足条件时
        """
        if n < 0 or r < 0:
            raise ValueError("组合数参数必须为非负整数")
        if r > n:
            raise ValueError(f"选取数不能大于总数: r={r} > n={n}")
        
        return self.factorial(n) // (self.factorial(r) * self.factorial(n - r))
    
    # ==================== 其他数学函数 ====================
    
    def abs(self, x: float) -> float:
        """
        绝对值
        
        Args:
            x: 输入值
            
        Returns:
            |x| 的值
        """
        return abs(x)
    
    def exp(self, x: float) -> float:
        """
        自然指数 e^x
        
        Args:
            x: 指数
            
        Returns:
            e^x 的值
        """
        cache_key = self._get_cache_key('exp', x)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = math.exp(x)
        self._set_cache(cache_key, result)
        return result
    
    def mod(self, a: float, b: float) -> float:
        """
        取模运算
        
        Args:
            a: 被除数
            b: 除数
            
        Returns:
            a % b 的值
            
        Raises:
            ZeroDivisionError: 当除数为0时
        """
        if b == 0:
            raise ZeroDivisionError("取模运算除数不能为零")
        return a % b
    
    def floor(self, x: float) -> int:
        """
        向下取整
        
        Args:
            x: 输入值
            
        Returns:
            不大于x的最大整数
        """
        return math.floor(x)
    
    def ceil(self, x: float) -> int:
        """
        向上取整
        
        Args:
            x: 输入值
            
        Returns:
            不小于x的最小整数
        """
        return math.ceil(x)
    
    def round_num(self, x: float, digits: int = 0) -> float:
        """
        四舍五入
        
        Args:
            x: 输入值
            digits: 保留小数位数
            
        Returns:
            四舍五入后的值
        """
        return round(x, digits)


def create_calculator(angle_mode: str = 'degree', use_cache: bool = True) -> CalculatorCore:
    """
    工厂函数：创建计算器实例
    
    Args:
        angle_mode: 角度模式，'degree' 或 'radian'
        use_cache: 是否启用缓存
        
    Returns:
        CalculatorCore 实例
    """
    return CalculatorCore(angle_mode=angle_mode, use_cache=use_cache)
