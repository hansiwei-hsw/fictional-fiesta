"""
main.py - 程序入口与交互控制模块

该模块负责：
- 程序入口点
- 交互式菜单展示
- 用户输入处理
- 功能分发与调用
- 资源管理

遵循PEP8规范，所有函数均添加文档字符串。
"""

import sys
import os
from typing import Optional, Tuple, List

from calculator_core import CalculatorCore, create_calculator
from input_validator import InputValidator, LegacyInputParser, create_validator
from result_formatter import ResultFormatter, create_formatter
from history_manager import HistoryManager, create_history_manager
from config_handler import ConfigHandler, get_config, create_config


class CalculatorApp:
    """
    科学计算器应用程序类
    
    整合所有模块，提供完整的交互式计算器功能。
    """
    
    MENU_WIDTH = 60
    SEPARATOR = "="
    
    def __init__(self):
        """初始化计算器应用程序"""
        self._config = create_config()
        self._calculator = create_calculator(
            angle_mode=self._config.angle_mode,
            use_cache=self._config.use_cache
        )
        self._validator = create_validator()
        self._formatter = create_formatter(
            decimal_places=self._config.decimal_places,
            use_scientific=self._config.use_scientific
        )
        self._history = create_history_manager(
            auto_save=self._config.get('auto_save_history'),
            max_records=self._config.get('max_history_records')
        )
        self._legacy_parser = LegacyInputParser()
        self._running = True
    
    def run(self) -> None:
        """运行计算器主循环"""
        self._show_welcome()
        
        while self._running:
            try:
                self._show_main_menu()
                choice = self._get_user_input("请选择功能")
                
                if choice is None or choice.strip() == '':
                    self._show_error("输入不能为空")
                    continue
                
                self._handle_menu_choice(choice.strip())
                
            except KeyboardInterrupt:
                print("\n")
                self._show_message("检测到中断信号，正在退出...")
                self._running = False
            except Exception as e:
                self._show_error(f"发生未知错误: {str(e)}")
        
        self._cleanup()
    
    def _show_welcome(self) -> None:
        """显示欢迎信息"""
        print("\n" + self.SEPARATOR * self.MENU_WIDTH)
        print(" " * 15 + "Python 科学计算器 v2.0")
        print(" " * 20 + "欢迎使用！")
        print(self.SEPARATOR * self.MENU_WIDTH)
        
        if self._config.get('show_tips'):
            print("\n提示: 输入 'help' 查看帮助，'quit' 或 'exit' 退出程序")
            if self._config.compatibility_mode:
                print("当前运行在兼容模式下，支持旧版本输入格式")
    
    def _show_main_menu(self) -> None:
        """显示主菜单"""
        print("\n" + "-" * self.MENU_WIDTH)
        print("主菜单")
        print("-" * self.MENU_WIDTH)
        
        print("\n【基础运算】")
        print("  1. 加法 (+)")
        print("  2. 减法 (-)")
        print("  3. 乘法 (×)")
        print("  4. 除法 (÷)")
        print("  5. 取模 (%)")
        
        print("\n【科学运算 - 三角函数】")
        print("  6. 正弦 (sin)")
        print("  7. 余弦 (cos)")
        print("  8. 正切 (tan)")
        print("  9. 反正弦 (asin)")
        print("  10. 反余弦 (acos)")
        print("  11. 反正切 (atan)")
        
        print("\n【科学运算 - 对数运算】")
        print("  12. 自然对数 (ln)")
        print("  13. 常用对数 (log10)")
        print("  14. 任意底对数 (log)")
        
        print("\n【科学运算 - 幂运算与开方】")
        print("  15. 幂运算 (x^y)")
        print("  16. 平方根 (√)")
        print("  17. n次方根")
        
        print("\n【科学运算 - 其他】")
        print("  18. 阶乘 (n!)")
        print("  19. 排列数 P(n,r)")
        print("  20. 组合数 C(n,r)")
        print("  21. 绝对值 (abs)")
        print("  22. 自然指数 (e^x)")
        print("  23. 向下取整 (floor)")
        print("  24. 向上取整 (ceil)")
        
        print("\n【系统功能】")
        print("  25. 查看历史记录")
        print("  26. 导出历史记录")
        print("  27. 清空历史记录")
        print("  28. 系统设置")
        print("  29. 查看缓存统计")
        print("  30. 帮助信息")
        
        print("\n  0. 退出程序")
        print("-" * self.MENU_WIDTH)
    
    def _handle_menu_choice(self, choice: str) -> None:
        """
        处理菜单选择
        
        Args:
            choice: 用户输入的选择
        """
        if choice.lower() in ('quit', 'exit', 'q'):
            self._running = False
            return
        
        if choice.lower() == 'help':
            self._show_help()
            return
        
        if choice.lower() == 'config':
            self._show_settings()
            return
        
        handlers = {
            '1': self._handle_add,
            '2': self._handle_subtract,
            '3': self._handle_multiply,
            '4': self._handle_divide,
            '5': self._handle_mod,
            '6': self._handle_sin,
            '7': self._handle_cos,
            '8': self._handle_tan,
            '9': self._handle_asin,
            '10': self._handle_acos,
            '11': self._handle_atan,
            '12': self._handle_ln,
            '13': self._handle_log10,
            '14': self._handle_log,
            '15': self._handle_power,
            '16': self._handle_sqrt,
            '17': self._handle_nth_root,
            '18': self._handle_factorial,
            '19': self._handle_permutation,
            '20': self._handle_combination,
            '21': self._handle_abs,
            '22': self._handle_exp,
            '23': self._handle_floor,
            '24': self._handle_ceil,
            '25': self._show_history,
            '26': self._export_history,
            '27': self._clear_history,
            '28': self._show_settings,
            '29': self._show_cache_stats,
            '30': self._show_help,
            '0': self._exit_app
        }
        
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            if self._config.compatibility_mode:
                self._handle_legacy_input(choice)
            else:
                self._show_error(f"无效的选项: {choice}")
    
    def _handle_legacy_input(self, expression: str) -> None:
        """
        处理兼容模式输入
        
        Args:
            expression: 用户输入的表达式
        """
        is_valid, parsed, error = self._legacy_parser.parse_legacy_format(expression)
        
        if not is_valid:
            self._show_error(error)
            return
        
        operator = parsed.get('operator', '')
        
        if 'operand2' in parsed:
            op1, op2 = parsed['operand1'], parsed['operand2']
            result = self._execute_binary_operation(operator, op1, op2)
        else:
            operand = parsed.get('operand')
            result = self._execute_unary_operation(operator, operand)
        
        if result is not None:
            self._show_result(result)
    
    def _execute_binary_operation(self, operator: str, a: float, b: float) -> Optional[float]:
        """
        执行二元运算
        
        Args:
            operator: 运算符
            a: 第一个操作数
            b: 第二个操作数
            
        Returns:
            运算结果
        """
        operations = {
            '+': lambda: self._calculator.add(a, b),
            '-': lambda: self._calculator.subtract(a, b),
            '*': lambda: self._calculator.multiply(a, b),
            '/': lambda: self._calculator.divide(a, b),
            '%': lambda: self._calculator.mod(a, b),
            '^': lambda: self._calculator.power(a, b),
        }
        
        op_func = operations.get(operator)
        if op_func:
            try:
                result = op_func()
                self._history.add_record(operator, [a, b], result)
                return result
            except Exception as e:
                self._show_error(str(e))
        else:
            self._show_error(f"不支持的运算符: {operator}")
        
        return None
    
    def _execute_unary_operation(self, operator: str, x: float) -> Optional[float]:
        """
        执行一元运算
        
        Args:
            operator: 运算符
            x: 操作数
            
        Returns:
            运算结果
        """
        operations = {
            'sin': lambda: self._calculator.sin(x),
            'cos': lambda: self._calculator.cos(x),
            'tan': lambda: self._calculator.tan(x),
            'asin': lambda: self._calculator.asin(x),
            'acos': lambda: self._calculator.acos(x),
            'atan': lambda: self._calculator.atan(x),
            'ln': lambda: self._calculator.ln(x),
            'log10': lambda: self._calculator.log10(x),
            'sqrt': lambda: self._calculator.sqrt(x),
            'fact': lambda: self._calculator.factorial(int(x)),
            'factorial': lambda: self._calculator.factorial(int(x)),
            'abs': lambda: self._calculator.abs(x),
            'exp': lambda: self._calculator.exp(x),
            'floor': lambda: self._calculator.floor(x),
            'ceil': lambda: self._calculator.ceil(x),
        }
        
        op_func = operations.get(operator.lower())
        if op_func:
            try:
                result = op_func()
                self._history.add_record(operator, [x], result)
                return result
            except Exception as e:
                self._show_error(str(e))
        else:
            self._show_error(f"不支持的运算符: {operator}")
        
        return None
    
    def _get_user_input(self, prompt: str) -> Optional[str]:
        """
        获取用户输入
        
        Args:
            prompt: 提示信息
            
        Returns:
            用户输入的字符串
        """
        try:
            return input(f"{prompt}: ")
        except EOFError:
            return None
    
    def _get_number_input(self, prompt: str, 
                          allow_negative: bool = True,
                          allow_zero: bool = True) -> Optional[float]:
        """
        获取数字输入
        
        Args:
            prompt: 提示信息
            allow_negative: 是否允许负数
            allow_zero: 是否允许零
            
        Returns:
            数字值
        """
        user_input = self._get_user_input(prompt)
        if user_input is None:
            return None
        
        is_valid, num, error = self._validator.validate_number(user_input)
        if not is_valid:
            self._show_error(error)
            return None
        
        if not allow_negative and num < 0:
            self._show_error("输入不能为负数")
            return None
        
        if not allow_zero and num == 0:
            self._show_error("输入不能为零")
            return None
        
        return num
    
    def _get_integer_input(self, prompt: str,
                           min_val: Optional[int] = None,
                           max_val: Optional[int] = None) -> Optional[int]:
        """
        获取整数输入
        
        Args:
            prompt: 提示信息
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            整数值
        """
        user_input = self._get_user_input(prompt)
        if user_input is None:
            return None
        
        is_valid, num, error = self._validator.validate_integer(user_input, min_val, max_val)
        if not is_valid:
            self._show_error(error)
            return None
        
        return num
    
    def _show_result(self, result: float, operation: str = "") -> None:
        """
        显示运算结果
        
        Args:
            result: 运算结果
            operation: 运算描述
        """
        formatted = self._formatter.format(result)
        
        print("\n" + "-" * 40)
        if operation:
            print(f"运算: {operation}")
        print(f"结果: {formatted}")
        print("-" * 40)
    
    def _show_message(self, message: str) -> None:
        """
        显示普通消息
        
        Args:
            message: 消息内容
        """
        print(f"\n[信息] {message}")
    
    def _show_error(self, error: str) -> None:
        """
        显示错误消息
        
        Args:
            error: 错误内容
        """
        print(f"\n[错误] {error}")
    
    def _show_success(self, message: str) -> None:
        """
        显示成功消息
        
        Args:
            message: 消息内容
        """
        print(f"\n[成功] {message}")
    
    # ==================== 基础运算处理函数 ====================
    
    def _handle_add(self) -> None:
        """处理加法运算"""
        a = self._get_number_input("请输入第一个数")
        if a is None:
            return
        b = self._get_number_input("请输入第二个数")
        if b is None:
            return
        
        try:
            result = self._calculator.add(a, b)
            self._history.add_record('加法', [a, b], result)
            self._show_result(result, f"{a} + {b}")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_subtract(self) -> None:
        """处理减法运算"""
        a = self._get_number_input("请输入被减数")
        if a is None:
            return
        b = self._get_number_input("请输入减数")
        if b is None:
            return
        
        try:
            result = self._calculator.subtract(a, b)
            self._history.add_record('减法', [a, b], result)
            self._show_result(result, f"{a} - {b}")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_multiply(self) -> None:
        """处理乘法运算"""
        a = self._get_number_input("请输入第一个数")
        if a is None:
            return
        b = self._get_number_input("请输入第二个数")
        if b is None:
            return
        
        try:
            result = self._calculator.multiply(a, b)
            self._history.add_record('乘法', [a, b], result)
            self._show_result(result, f"{a} × {b}")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_divide(self) -> None:
        """处理除法运算"""
        a = self._get_number_input("请输入被除数")
        if a is None:
            return
        b = self._get_number_input("请输入除数")
        if b is None:
            return
        
        try:
            result = self._calculator.divide(a, b)
            self._history.add_record('除法', [a, b], result)
            self._show_result(result, f"{a} ÷ {b}")
        except ZeroDivisionError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_mod(self) -> None:
        """处理取模运算"""
        a = self._get_number_input("请输入被除数")
        if a is None:
            return
        b = self._get_number_input("请输入除数")
        if b is None:
            return
        
        try:
            result = self._calculator.mod(a, b)
            self._history.add_record('取模', [a, b], result)
            self._show_result(result, f"{a} % {b}")
        except ZeroDivisionError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    # ==================== 三角函数处理函数 ====================
    
    def _handle_sin(self) -> None:
        """处理正弦运算"""
        mode_str = "度" if self._config.angle_mode == 'degree' else "弧度"
        x = self._get_number_input(f"请输入角度值（{mode_str}）")
        if x is None:
            return
        
        try:
            result = self._calculator.sin(x)
            self._history.add_record('sin', [x], result)
            self._show_result(result, f"sin({x}{mode_str})")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_cos(self) -> None:
        """处理余弦运算"""
        mode_str = "度" if self._config.angle_mode == 'degree' else "弧度"
        x = self._get_number_input(f"请输入角度值（{mode_str}）")
        if x is None:
            return
        
        try:
            result = self._calculator.cos(x)
            self._history.add_record('cos', [x], result)
            self._show_result(result, f"cos({x}{mode_str})")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_tan(self) -> None:
        """处理正切运算"""
        mode_str = "度" if self._config.angle_mode == 'degree' else "弧度"
        x = self._get_number_input(f"请输入角度值（{mode_str}）")
        if x is None:
            return
        
        try:
            result = self._calculator.tan(x)
            self._history.add_record('tan', [x], result)
            self._show_result(result, f"tan({x}{mode_str})")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_asin(self) -> None:
        """处理反正弦运算"""
        x = self._get_number_input("请输入值（范围 -1 到 1）")
        if x is None:
            return
        
        try:
            result = self._calculator.asin(x)
            self._history.add_record('asin', [x], result)
            mode_str = "度" if self._config.angle_mode == 'degree' else "弧度"
            self._show_result(result, f"asin({x}) = {result}{mode_str}")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_acos(self) -> None:
        """处理反余弦运算"""
        x = self._get_number_input("请输入值（范围 -1 到 1）")
        if x is None:
            return
        
        try:
            result = self._calculator.acos(x)
            self._history.add_record('acos', [x], result)
            mode_str = "度" if self._config.angle_mode == 'degree' else "弧度"
            self._show_result(result, f"acos({x}) = {result}{mode_str}")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_atan(self) -> None:
        """处理反正切运算"""
        x = self._get_number_input("请输入值")
        if x is None:
            return
        
        try:
            result = self._calculator.atan(x)
            self._history.add_record('atan', [x], result)
            mode_str = "度" if self._config.angle_mode == 'degree' else "弧度"
            self._show_result(result, f"atan({x}) = {result}{mode_str}")
        except Exception as e:
            self._show_error(str(e))
    
    # ==================== 对数运算处理函数 ====================
    
    def _handle_ln(self) -> None:
        """处理自然对数运算"""
        x = self._get_number_input("请输入值（必须大于0）", allow_negative=False, allow_zero=False)
        if x is None:
            return
        
        try:
            result = self._calculator.ln(x)
            self._history.add_record('ln', [x], result)
            self._show_result(result, f"ln({x})")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_log10(self) -> None:
        """处理常用对数运算"""
        x = self._get_number_input("请输入值（必须大于0）", allow_negative=False, allow_zero=False)
        if x is None:
            return
        
        try:
            result = self._calculator.log10(x)
            self._history.add_record('log10', [x], result)
            self._show_result(result, f"log10({x})")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_log(self) -> None:
        """处理任意底对数运算"""
        x = self._get_number_input("请输入真数（必须大于0）", allow_negative=False, allow_zero=False)
        if x is None:
            return
        base = self._get_number_input("请输入底数（必须大于0且不等于1）", allow_negative=False, allow_zero=False)
        if base is None:
            return
        
        if base == 1:
            self._show_error("底数不能为1")
            return
        
        try:
            result = self._calculator.log(x, base)
            self._history.add_record('log', [x, base], result)
            self._show_result(result, f"log_{base}({x})")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    # ==================== 幂运算与开方处理函数 ====================
    
    def _handle_power(self) -> None:
        """处理幂运算"""
        x = self._get_number_input("请输入底数")
        if x is None:
            return
        y = self._get_number_input("请输入指数")
        if y is None:
            return
        
        try:
            result = self._calculator.power(x, y)
            self._history.add_record('幂运算', [x, y], result)
            self._show_result(result, f"{x}^{y}")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_sqrt(self) -> None:
        """处理平方根运算"""
        x = self._get_number_input("请输入值（必须非负）", allow_negative=False)
        if x is None:
            return
        
        try:
            result = self._calculator.sqrt(x)
            self._history.add_record('平方根', [x], result)
            self._show_result(result, f"√{x}")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_nth_root(self) -> None:
        """处理n次方根运算"""
        x = self._get_number_input("请输入被开方数")
        if x is None:
            return
        n = self._get_integer_input("请输入根指数（正整数）", min_val=1)
        if n is None:
            return
        
        try:
            result = self._calculator.nth_root(x, n)
            self._history.add_record(f'{n}次方根', [x], result)
            self._show_result(result, f"{x}的{n}次方根")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    # ==================== 其他运算处理函数 ====================
    
    def _handle_factorial(self) -> None:
        """处理阶乘运算"""
        n = self._get_integer_input("请输入非负整数（最大170）", min_val=0, max_val=170)
        if n is None:
            return
        
        try:
            result = self._calculator.factorial(n)
            self._history.add_record('阶乘', [n], result)
            self._show_result(result, f"{n}!")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_permutation(self) -> None:
        """处理排列数运算"""
        n = self._get_integer_input("请输入总数n", min_val=0)
        if n is None:
            return
        r = self._get_integer_input(f"请输入选取数r（0-{n}）", min_val=0, max_val=n)
        if r is None:
            return
        
        try:
            result = self._calculator.permutation(n, r)
            self._history.add_record('排列数', [n, r], result)
            self._show_result(result, f"P({n}, {r})")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_combination(self) -> None:
        """处理组合数运算"""
        n = self._get_integer_input("请输入总数n", min_val=0)
        if n is None:
            return
        r = self._get_integer_input(f"请输入选取数r（0-{n}）", min_val=0, max_val=n)
        if r is None:
            return
        
        try:
            result = self._calculator.combination(n, r)
            self._history.add_record('组合数', [n, r], result)
            self._show_result(result, f"C({n}, {r})")
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_abs(self) -> None:
        """处理绝对值运算"""
        x = self._get_number_input("请输入数值")
        if x is None:
            return
        
        try:
            result = self._calculator.abs(x)
            self._history.add_record('绝对值', [x], result)
            self._show_result(result, f"|{x}|")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_exp(self) -> None:
        """处理自然指数运算"""
        x = self._get_number_input("请输入指数")
        if x is None:
            return
        
        try:
            result = self._calculator.exp(x)
            self._history.add_record('自然指数', [x], result)
            self._show_result(result, f"e^{x}")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_floor(self) -> None:
        """处理向下取整运算"""
        x = self._get_number_input("请输入数值")
        if x is None:
            return
        
        try:
            result = self._calculator.floor(x)
            self._history.add_record('向下取整', [x], result)
            self._show_result(result, f"floor({x})")
        except Exception as e:
            self._show_error(str(e))
    
    def _handle_ceil(self) -> None:
        """处理向上取整运算"""
        x = self._get_number_input("请输入数值")
        if x is None:
            return
        
        try:
            result = self._calculator.ceil(x)
            self._history.add_record('向上取整', [x], result)
            self._show_result(result, f"ceil({x})")
        except Exception as e:
            self._show_error(str(e))
    
    # ==================== 系统功能处理函数 ====================
    
    def _show_history(self) -> None:
        """显示历史记录"""
        records = self._history.get_all_records()
        
        if not records:
            self._show_message("暂无历史记录")
            return
        
        print("\n" + "=" * self.MENU_WIDTH)
        print("历史记录")
        print("=" * self.MENU_WIDTH)
        
        for i, record in enumerate(records[-20:], 1):
            print(f"{i}. {record}")
        
        if len(records) > 20:
            print(f"\n... 共 {len(records)} 条记录，显示最近 20 条")
        
        print("=" * self.MENU_WIDTH)
    
    def _export_history(self) -> None:
        """导出历史记录"""
        print("\n选择导出格式:")
        print("  1. 文本文件 (.txt)")
        print("  2. CSV文件 (.csv)")
        print("  3. JSON文件 (.json)")
        
        choice = self._get_user_input("请选择格式")
        if choice is None:
            return
        
        if choice == '1':
            file_path = self._get_user_input("请输入导出文件路径（默认: history_export.txt）") or "history_export.txt"
            if self._history.export_to_txt(file_path):
                self._show_success(f"历史记录已导出到: {file_path}")
            else:
                self._show_error("导出失败，请检查文件路径权限")
        elif choice == '2':
            file_path = self._get_user_input("请输入导出文件路径（默认: history_export.csv）") or "history_export.csv"
            if self._history.export_to_csv(file_path):
                self._show_success(f"历史记录已导出到: {file_path}")
            else:
                self._show_error("导出失败，请检查文件路径权限")
        elif choice == '3':
            file_path = self._get_user_input("请输入导出文件路径（默认: history_export.json）") or "history_export.json"
            if self._history.save():
                self._show_success(f"历史记录已保存到: {file_path}")
            else:
                self._show_error("导出失败，请检查文件路径权限")
        else:
            self._show_error("无效的选择")
    
    def _clear_history(self) -> None:
        """清空历史记录"""
        confirm = self._get_user_input("确认清空所有历史记录？(y/n)")
        if confirm and confirm.lower() == 'y':
            self._history.clear_all()
            self._show_success("历史记录已清空")
        else:
            self._show_message("操作已取消")
    
    def _show_settings(self) -> None:
        """显示系统设置"""
        while True:
            print("\n" + "=" * self.MENU_WIDTH)
            print("系统设置")
            print("=" * self.MENU_WIDTH)
            print(f"  1. 角度模式: {'角度' if self._config.angle_mode == 'degree' else '弧度'}")
            print(f"  2. 小数位数: {self._config.decimal_places}")
            print(f"  3. 科学计数法: {'开启' if self._config.use_scientific else '关闭'}")
            print(f"  4. 缓存机制: {'开启' if self._config.use_cache else '关闭'}")
            print(f"  5. 兼容模式: {'开启' if self._config.compatibility_mode else '关闭'}")
            print(f"  6. 自动保存历史: {'开启' if self._config.get('auto_save_history') else '关闭'}")
            print(f"  7. 显示提示: {'开启' if self._config.get('show_tips') else '关闭'}")
            print("  8. 恢复默认设置")
            print("  0. 返回主菜单")
            print("=" * self.MENU_WIDTH)
            
            choice = self._get_user_input("请选择设置项")
            if choice is None or choice == '0':
                break
            
            self._handle_settings_choice(choice)
    
    def _handle_settings_choice(self, choice: str) -> None:
        """
        处理设置选项
        
        Args:
            choice: 用户选择
        """
        if choice == '1':
            current = self._config.angle_mode
            new_mode = 'radian' if current == 'degree' else 'degree'
            self._config.angle_mode = new_mode
            self._calculator.angle_mode = new_mode
            self._show_success(f"角度模式已切换为: {'角度' if new_mode == 'degree' else '弧度'}")
        
        elif choice == '2':
            places = self._get_integer_input("请输入小数位数（0-15）", min_val=0, max_val=15)
            if places is not None:
                self._config.decimal_places = places
                self._formatter.decimal_places = places
                self._show_success(f"小数位数已设置为: {places}")
        
        elif choice == '3':
            current = self._config.use_scientific
            self._config.use_scientific = not current
            self._formatter.use_scientific = not current
            self._show_success(f"科学计数法已{'开启' if not current else '关闭'}")
        
        elif choice == '4':
            current = self._config.use_cache
            self._config.use_cache = not current
            self._show_success(f"缓存机制已{'开启' if not current else '关闭'}")
        
        elif choice == '5':
            current = self._config.compatibility_mode
            self._config.compatibility_mode = not current
            self._show_success(f"兼容模式已{'开启' if not current else '关闭'}")
        
        elif choice == '6':
            current = self._config.get('auto_save_history')
            self._config.set('auto_save_history', not current)
            self._show_success(f"自动保存历史已{'开启' if not current else '关闭'}")
        
        elif choice == '7':
            current = self._config.get('show_tips')
            self._config.set('show_tips', not current)
            self._show_success(f"显示提示已{'开启' if not current else '关闭'}")
        
        elif choice == '8':
            confirm = self._get_user_input("确认恢复默认设置？(y/n)")
            if confirm and confirm.lower() == 'y':
                self._config.reset_to_default()
                self._calculator.angle_mode = self._config.angle_mode
                self._formatter.decimal_places = self._config.decimal_places
                self._formatter.use_scientific = self._config.use_scientific
                self._show_success("已恢复默认设置")
            else:
                self._show_message("操作已取消")
    
    def _show_cache_stats(self) -> None:
        """显示缓存统计"""
        stats = self._calculator.get_cache_stats()
        
        print("\n" + "=" * self.MENU_WIDTH)
        print("缓存统计")
        print("=" * self.MENU_WIDTH)
        print(f"  缓存命中次数: {stats['hits']}")
        print(f"  缓存未命中次数: {stats['misses']}")
        print(f"  命中率: {stats['hit_rate']:.2%}")
        print(f"  当前缓存大小: {stats['cache_size']}")
        print("=" * self.MENU_WIDTH)
        
        clear = self._get_user_input("是否清空缓存？(y/n)")
        if clear and clear.lower() == 'y':
            self._calculator.clear_cache()
            self._show_success("缓存已清空")
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        print("\n" + "=" * self.MENU_WIDTH)
        print("帮助信息")
        print("=" * self.MENU_WIDTH)
        print("\n【基础运算】")
        print("  支持加、减、乘、除、取模等基础四则运算")
        
        print("\n【科学运算】")
        print("  - 三角函数: sin, cos, tan, asin, acos, atan")
        print("  - 对数运算: ln(自然对数), log10(常用对数), log(任意底)")
        print("  - 幂运算: x^y, √x, n次方根")
        print("  - 其他: 阶乘, 排列数, 组合数, 绝对值等")
        
        print("\n【快捷命令】")
        print("  help    - 显示帮助信息")
        print("  config  - 打开系统设置")
        print("  quit/exit - 退出程序")
        
        print("\n【兼容模式】")
        print("  开启后支持旧版本输入格式:")
        print("  - 二元运算: '数字1 运算符 数字2'")
        print("  - 一元运算: '运算符 数字'")
        print("  例如: '5 + 3', 'sin 30', 'sqrt 16'")
        
        print("\n【角度模式】")
        print("  - 角度模式: 输入角度值（如 sin 30 表示 sin(30°)）")
        print("  - 弧度模式: 输入弧度值（如 sin 1.57 表示 sin(1.57 rad)）")
        
        print("\n" + "=" * self.MENU_WIDTH)
    
    def _exit_app(self) -> None:
        """退出应用程序"""
        self._running = False
    
    def _cleanup(self) -> None:
        """清理资源"""
        if self._history.is_modified():
            self._history.save()
        
        self._config.save()
        
        print("\n" + "=" * self.MENU_WIDTH)
        print("感谢使用 Python 科学计算器 v2.0！")
        print("再见！")
        print("=" * self.MENU_WIDTH + "\n")


def main():
    """程序入口点"""
    try:
        app = CalculatorApp()
        app.run()
    except Exception as e:
        print(f"\n程序发生严重错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
