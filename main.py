"""
Python科学计算器 v2.0 - 主程序入口

本程序是一个面向科研/工程人员的科学计算器，支持基础四则运算
和多种科学运算功能。

功能特性:
- 基础四则运算: + - * /
- 科学运算: sin, cos, tan, ln, log, pow, sqrt, factorial
- 交互式菜单操作
- 历史记录管理
- 配置持久化
- 兼容模式支持

作者: Development Team
版本: 2.0.0
"""

import sys
import os

# 导入各模块
from calculator_core import (
    add, subtract, multiply, divide,
    sin, cos, tan, ln, log10, power, sqrt, factorial,
    CalculatorError, DivisionByZeroError, 
    NegativeNumberError, InvalidInputError,
    list_operations, clear_cache
)
from input_validator import (
    InputValidator, ValidationError, validate_menu_choice
)
from result_formatter import ResultFormatter, format_result
from history_manager import HistoryManager, get_history_manager
from config_handler import ConfigHandler, get_config_handler


class ScientificCalculator:
    """科学计算器主类"""
    
    def __init__(self):
        """初始化计算器"""
        self.config = get_config_handler()
        self.history = get_history_manager()
        self.formatter = ResultFormatter(
            decimal_places=self.config.decimal_places,
            auto_scientific=self.config.auto_scientific
        )
        self.running = False
    
    def display_welcome(self):
        """显示欢迎信息"""
        print("\n" + "=" * 60)
        print("       🧮 Python科学计算器 v2.0")
        print("=" * 60)
        print("  面向科研/工程人员的专业计算工具")
        print("  支持基础四则运算 + 10+ 种科学运算")
        print("=" * 60)
    
    def display_menu(self):
        """显示主菜单"""
        print("\n" + "-" * 60)
        print("【主菜单】")
        print("-" * 60)
        print("  1. 基础运算 (+, -, *, /)")
        print("  2. 三角函数 (sin, cos, tan)")
        print("  3. 对数运算 (ln, log)")
        print("  4. 幂运算与开方 (x^y, √x)")
        print("  5. 阶乘 (n!)")
        print("  6. 查看历史记录")
        print("  7. 系统设置")
        print("  8. 兼容模式 (旧版输入方式)")
        print("  0. 退出程序")
        print("-" * 60)
        mode = "兼容模式" if self.config.compatibility_mode else "标准模式"
        angle = "角度" if self.config.use_degrees else "弧度"
        print(f"  当前: {mode} | 角度单位: {angle} | 小数位: {self.config.decimal_places}")
        print("-" * 60)
    
    def display_basic_operations_menu(self):
        """显示基础运算菜单"""
        print("\n【基础运算】")
        print("  支持的运算符: + (加), - (减), * (乘), / (除)")
        print("  输入格式: 数字1 [运算符] 数字2")
        print("  示例: 5 + 3")
    
    def display_trigonometric_menu(self):
        """显示三角函数菜单"""
        print("\n【三角函数】")
        print(f"  当前角度模式: {'角度(°)' if self.config.use_degrees else '弧度'}")
        print("  1. sin (正弦)")
        print("  2. cos (余弦)")
        print("  3. tan (正切)")
    
    def display_logarithm_menu(self):
        """显示对数运算菜单"""
        print("\n【对数运算】")
        print("  1. ln (自然对数)")
        print("  2. log (常用对数, 以10为底)")
    
    def display_power_menu(self):
        """显示幂运算菜单"""
        print("\n【幂运算与开方】")
        print("  1. x^y (幂运算)")
        print("  2. √x (平方根)")
    
    def display_settings_menu(self):
        """显示设置菜单"""
        print("\n【系统设置】")
        print("  1. 切换角度/弧度模式")
        print("  2. 设置小数位数")
        print("  3. 切换兼容模式")
        print("  4. 切换科学计数法")
        print("  5. 清空历史记录")
        print("  6. 导出历史记录")
        print("  7. 查看统计信息")
        print("  8. 重置所有设置")
        print("  0. 返回主菜单")
    
    def display_history(self):
        """显示历史记录"""
        records = self.history.get_history(limit=20)
        
        print("\n" + "=" * 60)
        print("【历史记录】")
        print("=" * 60)
        
        if not records:
            print("  暂无历史记录")
        else:
            for i, record in enumerate(records, 1):
                print(f"  {record}")
        
        print("=" * 60)
        input("\n按回车键返回主菜单...")
    
    def handle_basic_operation(self):
        """处理基础运算"""
        self.display_basic_operations_menu()
        
        try:
            num1 = input("请输入第一个数字: ").strip()
            operator = input("请输入运算符 (+, -, *, /): ").strip()
            num2 = input("请输入第二个数字: ").strip()
            
            n1, op, n2 = InputValidator.validate_basic_operation(num1, operator, num2)
            
            if op == '+':
                result = add(n1, n2)
            elif op == '-':
                result = subtract(n1, n2)
            elif op == '*':
                result = multiply(n1, n2)
            elif op == '/':
                result = divide(n1, n2)
            else:
                raise InvalidInputError(f"未知运算符: {op}")
            
            formatted_result = self.formatter.format(result)
            expression = f"{n1} {op} {n2}"
            
            print(f"\n  ✅ 结果: {expression} = {formatted_result}")
            
            self.history.add_record(
                operation="基础运算",
                expression=expression,
                result=formatted_result
            )
            
        except (ValidationError, CalculatorError) as e:
            print(f"\n  ❌ 错误: {e}")
            self.history.add_record(
                operation="基础运算",
                expression=f"{num1} {operator} {num2}",
                result="",
                success=False,
                error_message=str(e)
            )
    
    def handle_trigonometric(self):
        """处理三角函数运算"""
        self.display_trigonometric_menu()
        
        try:
            choice = input("\n请选择函数 (1-3): ").strip()
            func_choice = validate_menu_choice(choice, [1, 2, 3])
            
            angle_input = input(f"请输入角度值 ({'度数' if self.config.use_degrees else '弧度'}): ").strip()
            _, angle = InputValidator.validate_scientific_operation("sin", angle_input)
            
            use_degrees = self.config.use_degrees
            
            if func_choice == 1:
                result = sin(float(angle), use_degrees)
                func_name = "sin"
            elif func_choice == 2:
                result = cos(float(angle), use_degrees)
                func_name = "cos"
            else:
                result = tan(float(angle), use_degrees)
                func_name = "tan"
            
            formatted_result = self.formatter.format(result)
            unit = "°" if use_degrees else " rad"
            expression = f"{func_name}({angle}{unit})"
            
            print(f"\n  ✅ 结果: {expression} = {formatted_result}")
            
            self.history.add_record(
                operation="三角函数",
                expression=expression,
                result=formatted_result
            )
            
        except (ValidationError, CalculatorError) as e:
            print(f"\n  ❌ 错误: {e}")
            self.history.add_record(
                operation="三角函数",
                expression=f"三角函数计算",
                result="",
                success=False,
                error_message=str(e)
            )
    
    def handle_logarithm(self):
        """处理对数运算"""
        self.display_logarithm_menu()
        
        try:
            choice = input("\n请选择函数 (1-2): ").strip()
            func_choice = validate_menu_choice(choice, [1, 2])
            
            num_input = input("请输入数字 (x > 0): ").strip()
            _, num = InputValidator.validate_scientific_operation("ln", num_input)
            
            if func_choice == 1:
                result = ln(num)
                func_name = "ln"
            else:
                result = log10(num)
                func_name = "log"
            
            formatted_result = self.formatter.format(result)
            expression = f"{func_name}({num})"
            
            print(f"\n  ✅ 结果: {expression} = {formatted_result}")
            
            self.history.add_record(
                operation="对数运算",
                expression=expression,
                result=formatted_result
            )
            
        except (ValidationError, CalculatorError) as e:
            print(f"\n  ❌ 错误: {e}")
            self.history.add_record(
                operation="对数运算",
                expression="对数计算",
                result="",
                success=False,
                error_message=str(e)
            )
    
    def handle_power(self):
        """处理幂运算和开方"""
        self.display_power_menu()
        
        try:
            choice = input("\n请选择运算 (1-2): ").strip()
            func_choice = validate_menu_choice(choice, [1, 2])
            
            if func_choice == 1:
                base_input = input("请输入底数 (x): ").strip()
                exp_input = input("请输入指数 (y): ").strip()
                _, base, exp = InputValidator.validate_two_operand_scientific(
                    "pow", base_input, exp_input
                )
                result = power(base, exp)
                expression = f"{base}^{exp}"
            else:
                num_input = input("请输入被开方数 (x ≥ 0): ").strip()
                _, num = InputValidator.validate_scientific_operation("sqrt", num_input)
                result = sqrt(num)
                expression = f"√{num}"
            
            formatted_result = self.formatter.format(result)
            
            print(f"\n  ✅ 结果: {expression} = {formatted_result}")
            
            self.history.add_record(
                operation="幂运算/开方",
                expression=expression,
                result=formatted_result
            )
            
        except (ValidationError, CalculatorError) as e:
            print(f"\n  ❌ 错误: {e}")
            self.history.add_record(
                operation="幂运算/开方",
                expression="幂运算/开方计算",
                result="",
                success=False,
                error_message=str(e)
            )
    
    def handle_factorial(self):
        """处理阶乘运算"""
        print("\n【阶乘运算】")
        print("  计算 n! (n必须是非负整数, n ≤ 170)")
        
        try:
            num_input = input("请输入 n: ").strip()
            _, num = InputValidator.validate_scientific_operation("fact", num_input)
            
            # 确保是整数
            if not isinstance(num, int) and not num == int(num):
                raise ValidationError("阶乘只接受整数")
            num = int(num)
            
            result = factorial(num)
            expression = f"{num}!"
            formatted_result = self.formatter.format(result)
            
            print(f"\n  ✅ 结果: {expression} = {formatted_result}")
            
            self.history.add_record(
                operation="阶乘",
                expression=expression,
                result=formatted_result
            )
            
        except (ValidationError, CalculatorError) as e:
            print(f"\n  ❌ 错误: {e}")
            self.history.add_record(
                operation="阶乘",
                expression="阶乘计算",
                result="",
                success=False,
                error_message=str(e)
            )
    
    def handle_settings(self):
        """处理系统设置"""
        while True:
            self.display_settings_menu()
            
            try:
                choice = input("\n请选择设置项 (0-8): ").strip()
                setting_choice = validate_menu_choice(choice, list(range(9)))
                
                if setting_choice == 0:
                    break
                elif setting_choice == 1:
                    new_mode = self.config.toggle_angle_mode()
                    print(f"\n  ✅ 已切换到: {'角度' if new_mode == 'degrees' else '弧度'}模式")
                elif setting_choice == 2:
                    places = input("请输入小数位数 (0-10): ").strip()
                    places = int(places)
                    self.config.decimal_places = places
                    self.formatter.set_decimal_places(places)
                    print(f"\n  ✅ 小数位数已设置为: {places}")
                elif setting_choice == 3:
                    new_mode = self.config.toggle_compatibility_mode()
                    print(f"\n  ✅ 兼容模式: {'开启' if new_mode else '关闭'}")
                elif setting_choice == 4:
                    self.formatter.toggle_scientific_notation()
                    print(f"\n  ✅ 自动科学计数法: {'开启' if self.formatter.auto_scientific else '关闭'}")
                elif setting_choice == 5:
                    count = self.history.clear_history()
                    print(f"\n  ✅ 已清空 {count} 条历史记录")
                elif setting_choice == 6:
                    filename = input("请输入导出文件名 (默认: calculator_history.txt): ").strip()
                    if not filename:
                        filename = None
                    exported_file = self.history.export_to_txt(filename)
                    print(f"\n  ✅ 历史记录已导出到: {exported_file}")
                elif setting_choice == 7:
                    stats = self.history.get_statistics()
                    print("\n【统计信息】")
                    print(f"  总记录数: {stats['total_records']}")
                    print(f"  成功: {stats['successful']}")
                    print(f"  失败: {stats['failed']}")
                    print(f"  成功率: {stats['success_rate']}")
                    if stats['top_operations']:
                        print("  常用运算:")
                        for op, count in stats['top_operations']:
                            print(f"    - {op}: {count}次")
                elif setting_choice == 8:
                    confirm = input("确定要重置所有设置吗? (y/n): ").strip().lower()
                    if confirm == 'y':
                        self.config.reset_to_defaults()
                        self.formatter = ResultFormatter()
                        print("\n  ✅ 所有设置已重置为默认值")
                
                if setting_choice != 0:
                    input("\n按回车键继续...")
                    
            except (ValidationError, ValueError) as e:
                print(f"\n  ❌ 错误: {e}")
                input("\n按回车键继续...")
    
    def handle_compatibility_mode(self):
        """处理兼容模式（旧版输入方式）"""
        print("\n" + "=" * 60)
        print("【兼容模式】")
        print("=" * 60)
        print("  支持格式:")
        print("    基础运算: 5 + 3")
        print("    科学运算: sin 30")
        print("  输入 'exit' 返回主菜单")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q', '返回']:
                    break
                
                if not user_input:
                    continue
                
                parsed = InputValidator.parse_expression(user_input)
                
                if parsed is None:
                    print("  ❌ 格式错误，请使用: '数字 运算符 数字' 或 '函数 数字'")
                    continue
                
                if len(parsed) == 3:
                    # 基础运算
                    op, n1, n2 = parsed
                    if op == '+':
                        result = add(n1, n2)
                    elif op == '-':
                        result = subtract(n1, n2)
                    elif op == '*':
                        result = multiply(n1, n2)
                    elif op == '/':
                        result = divide(n1, n2)
                    else:
                        raise InvalidInputError(f"未知运算符: {op}")
                    
                    expression = f"{n1} {op} {n2}"
                else:
                    # 科学运算
                    func_name, num = parsed
                    use_degrees = self.config.use_degrees
                    
                    if func_name == 'sin':
                        result = sin(float(num), use_degrees)
                    elif func_name == 'cos':
                        result = cos(float(num), use_degrees)
                    elif func_name == 'tan':
                        result = tan(float(num), use_degrees)
                    elif func_name == 'ln':
                        result = ln(num)
                    elif func_name == 'log':
                        result = log10(num)
                    elif func_name == 'sqrt':
                        result = sqrt(num)
                    else:
                        raise InvalidInputError(f"兼容模式暂不支持函数: {func_name}")
                    
                    expression = f"{func_name}({num})"
                
                formatted_result = self.formatter.format(result)
                print(f"  = {formatted_result}")
                
                self.history.add_record(
                    operation="兼容模式",
                    expression=user_input,
                    result=formatted_result
                )
                
            except (ValidationError, CalculatorError) as e:
                print(f"  ❌ 错误: {e}")
                self.history.add_record(
                    operation="兼容模式",
                    expression=user_input,
                    result="",
                    success=False,
                    error_message=str(e)
                )
            except Exception as e:
                print(f"  ❌ 未知错误: {e}")
    
    def run(self):
        """运行计算器主循环"""
        self.running = True
        
        if self.config.show_welcome_message:
            self.display_welcome()
        
        while self.running:
            try:
                self.display_menu()
                choice = input("请选择功能 (0-8): ").strip()
                
                try:
                    menu_choice = validate_menu_choice(choice, list(range(9)))
                except ValidationError as e:
                    print(f"\n  ❌ 输入错误: {e}")
                    continue
                
                if menu_choice == 0:
                    self.running = False
                    print("\n  感谢使用科学计算器 v2.0，再见！")
                    
                elif menu_choice == 1:
                    self.handle_basic_operation()
                elif menu_choice == 2:
                    self.handle_trigonometric()
                elif menu_choice == 3:
                    self.handle_logarithm()
                elif menu_choice == 4:
                    self.handle_power()
                elif menu_choice == 5:
                    self.handle_factorial()
                elif menu_choice == 6:
                    self.display_history()
                elif menu_choice == 7:
                    self.handle_settings()
                elif menu_choice == 8:
                    self.handle_compatibility_mode()
                
            except KeyboardInterrupt:
                print("\n\n  检测到中断信号，正在退出...")
                self.running = False
            except Exception as e:
                print(f"\n  ❌ 程序错误: {e}")
        
        # 清理资源
        clear_cache()
        print("  资源已清理，程序结束。")


def main():
    """程序入口函数"""
    try:
        calculator = ScientificCalculator()
        calculator.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
