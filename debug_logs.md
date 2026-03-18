# Python科学计算器 v2.0 - 调试日志

> **文档说明**: 本文档记录了科学计算器v2.0开发过程中的关键调试问题，包含Bug现象、复现步骤、根因分析和修复方案。

---

## 调试记录总览

| 轮次 | 问题类型 | 涉及模块 | 严重程度 | 状态 |
|------|----------|----------|----------|------|
| 1 | 三角函数角度/弧度转换错误 | calculator_core.py | 高 | ✅ 已修复 |
| 2 | 阶乘负数输入崩溃 | calculator_core.py + input_validator.py | 高 | ✅ 已修复 |
| 3 | 历史记录重复保存 | history_manager.py | 中 | ✅ 已修复 |
| 4 | 兼容模式切换后运算错误 | main.py + config_handler.py | 中 | ✅ 已修复 |
| 5 | 小数位数配置不生效 | result_formatter.py | 低 | ✅ 已修复 |

---

## 第一轮调试：三角函数角度/弧度转换错误

### Bug现象
输入 `sin(30°)` 期望返回 `0.5`，但实际返回 `-0.9880316240928618`（这是30弧度的正弦值）。

### 复现步骤
1. 启动计算器
2. 选择三角函数运算（菜单2）
3. 选择sin函数（选项1）
4. 输入角度值 `30`
5. 观察结果

### 根因分析
**定位文件**: `calculator_core.py`

**问题代码**:
```python
def sin(angle: float, use_degrees: bool = True) -> float:
    """正弦函数"""
    if use_degrees:
        angle = math.radians(angle)  # 这里正确
    return math.sin(angle)
```

**问题分析**:
- 函数本身的实现是正确的
- 问题在于 `main.py` 中调用时没有正确传递 `use_degrees` 参数
- 配置模块中的角度模式设置没有被正确读取

**实际错误代码** (main.py):
```python
# 错误：没有传递 use_degrees 参数
result = sin(float(angle))  # 使用了默认的 use_degrees=True，但配置已切换
```

### 修复方案

**修改文件**: `main.py`

**修复代码**:
```python
# 修复：从配置中读取角度模式并传递
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
```

**同时增强 config_handler.py 的验证**:
```python
def _validate_config(self):
    """验证并修正配置值"""
    # 验证角度模式
    if self._config.angle_mode not in self.VALID_ANGLE_MODES:
        self._config.angle_mode = 'degrees'
```

### 验证结果
- ✅ 输入 `sin(30°)` 返回 `0.5`
- ✅ 切换到弧度模式后，输入 `sin(0.5236)` 返回约 `0.5`
- ✅ 配置持久化正确

### 预防措施
1. 添加配置值验证逻辑，确保非法配置值被自动修正
2. 所有依赖配置的函数调用必须显式传递配置参数
3. 添加单元测试覆盖角度/弧度切换场景

---

## 第二轮调试：阶乘负数输入崩溃

### Bug现象
输入负数进行阶乘运算时，程序抛出未捕获的异常并崩溃退出，而不是优雅地显示错误信息。

### 复现步骤
1. 启动计算器
2. 选择阶乘运算（菜单5）
3. 输入 `-5`
4. 程序崩溃，显示 `ValueError: factorial() not defined for negative values`

### 根因分析
**定位文件**: `calculator_core.py` 第 165 行

**问题代码**:
```python
def factorial(n: int) -> int:
    """阶乘运算"""
    if not isinstance(n, int):
        raise InvalidInputError("阶乘只接受整数")
    # 缺少负数检查！
    return math.factorial(n)  # math.factorial 会抛出 ValueError
```

**问题分析**:
- 代码只检查了输入是否为整数，但没有检查是否为非负数
- Python 的 `math.factorial()` 函数对负数会抛出 `ValueError`，而不是我们定义的 `CalculatorError`
- 上层调用者只捕获 `CalculatorError`，导致 `ValueError` 未被捕获

### 修复方案

**修改文件**: `calculator_core.py`

**修复代码**:
```python
def factorial(n: int) -> int:
    """
    阶乘运算
    
    Args:
        n: 非负整数
    
    Returns:
        n!的值
    
    Raises:
        InvalidInputError: 当n不是整数或超出范围时抛出
        NegativeNumberError: 当n<0时抛出
    """
    if not isinstance(n, int):
        raise InvalidInputError("阶乘只接受整数")
    if n < 0:
        raise NegativeNumberError("负数没有阶乘")
    if n > 170:
        raise InvalidInputError("输入过大，阶乘结果超出浮点数表示范围")
    return math.factorial(n)
```

**同时增强 input_validator.py 的前置校验**:
```python
@classmethod
def validate_scientific_operation(cls, func_name: str, operand: str):
    """校验科学运算的输入"""
    # ... 其他代码 ...
    
    # 对阶乘进行特殊校验
    if func_name == 'fact' and num < 0:
        raise ValidationError("阶乘不接受负数")
    
    return func_name, num
```

### 验证结果
- ✅ 输入 `-5` 显示友好错误信息: "负数没有阶乘"
- ✅ 输入 `171` 显示友好错误信息: "输入过大，阶乘结果超出浮点数表示范围"
- ✅ 程序不再崩溃，继续正常运行

### 预防措施
1. 所有调用外部库函数前进行前置条件检查
2. 将外部异常转换为本项目定义的异常类型
3. 在输入校验层增加业务规则校验
4. 编写边界值测试用例

---

## 第三轮调试：历史记录重复保存

### Bug现象
同一次计算会被记录两次在历史记录中，导致历史记录列表出现重复条目。

### 复现步骤
1. 启动计算器
2. 进行任意计算（如 5 + 3）
3. 查看历史记录（菜单6）
4. 观察到同一计算出现两次

### 根因分析
**定位文件**: `history_manager.py` + `main.py`

**问题代码** (main.py):
```python
def handle_basic_operation(self):
    try:
        # ... 计算逻辑 ...
        self.history.add_record(...)  # 第一次保存
        
    except (ValidationError, CalculatorError) as e:
        print(f"错误: {e}")
        self.history.add_record(...)  # 异常时第二次保存
```

**问题分析**:
- 正常计算流程中，结果会被保存一次
- 但在某些情况下，计算成功后也会进入异常处理块（如警告信息被误判）
- 更深层的问题是 `add_record` 方法没有检查重复记录

**另一个问题** (history_manager.py):
```python
def add_record(self, ...):
    record = HistoryRecord(...)
    self._records.append(record)
    self._save_history()  # 每次添加都写文件，性能差且可能导致重复
```

### 修复方案

**修改文件**: `history_manager.py`

**修复代码**:
```python
def add_record(self, operation: str, expression: str, result: str,
               success: bool = True, error_message: str = None) -> HistoryRecord:
    """
    添加历史记录
    
    增加重复检测：如果最后一条记录与当前记录完全相同，则不添加
    """
    # 检查是否与最后一条记录重复（1秒内，相同表达式）
    if self._records:
        last = self._records[-1]
        if (last.expression == expression and 
            last.success == success and
            last.operation == operation):
            # 检查时间差（1秒内认为是重复）
            from datetime import datetime
            last_time = datetime.fromisoformat(last.timestamp.replace(' ', 'T'))
            current_time = datetime.now()
            if (current_time - last_time).total_seconds() < 1:
                return last  # 返回已有记录，不添加新记录
    
    record = HistoryRecord(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        operation=operation,
        expression=expression,
        result=result,
        success=success,
        error_message=error_message
    )
    
    self._records.append(record)
    
    # 限制历史记录数量
    if len(self._records) > self.max_size:
        self._records = self._records[-self.max_size:]
    
    self._save_history()
    return record
```

**同时修复 main.py 的逻辑**:
```python
def handle_basic_operation(self):
    expression = ""
    try:
        # ... 输入和计算 ...
        expression = f"{n1} {op} {n2}"
        # ... 计算结果 ...
        
        print(f"结果: {expression} = {formatted_result}")
        self.history.add_record(
            operation="基础运算",
            expression=expression,
            result=formatted_result
        )
        
    except (ValidationError, CalculatorError) as e:
        print(f"错误: {e}")
        # 只在有表达式时才记录失败
        if expression:
            self.history.add_record(
                operation="基础运算",
                expression=expression,
                result="",
                success=False,
                error_message=str(e)
            )
```

### 验证结果
- ✅ 同一次计算只记录一次
- ✅ 快速重复相同计算会被检测为重复
- ✅ 失败的计算也能正确记录

### 预防措施
1. 在数据层增加重复检测机制
2. 业务层确保异常处理块不会重复记录
3. 添加防抖机制，防止用户快速重复操作
4. 使用唯一标识符或时间戳进行重复检测

---

## 第四轮调试：兼容模式切换后运算错误

### Bug现象
在兼容模式下进行计算后，切换回标准模式，发现角度模式设置被意外修改。

### 复现步骤
1. 启动计算器
2. 查看当前角度模式（显示"角度"）
3. 进入兼容模式（菜单8）
4. 进行一次计算（如 sin 30）
5. 输入 exit 返回主菜单
6. 查看当前角度模式（显示"弧度"）

### 根因分析
**定位文件**: `config_handler.py`

**问题代码**:
```python
def toggle_angle_mode(self) -> str:
    """切换角度模式"""
    if self._config.angle_mode == 'degrees':
        self._config.angle_mode = 'radians'
    else:
        self._config.angle_mode = 'degrees'
    self._save_config()
    return self._config.angle_mode
```

**问题分析**:
- 在开发调试过程中，为了测试方便，在兼容模式的退出逻辑中临时添加了切换角度模式的代码
- 该调试代码忘记删除，导致每次退出兼容模式都会切换角度模式
- 这是一个典型的"调试代码遗留"问题

**实际错误代码** (main.py):
```python
def handle_compatibility_mode(self):
    while True:
        # ... 计算逻辑 ...
        
        if user_input.lower() in ['exit', 'quit']:
            # 调试代码，忘记删除！
            self.config.toggle_angle_mode()  # ❌ 不应该在这里切换
            break
```

### 修复方案

**修改文件**: `main.py`

**修复代码**:
```python
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
                # 修复：删除调试代码，直接退出
                break  # ✅ 直接退出，不切换任何设置
            
            # ... 其他代码 ...
```

### 验证结果
- ✅ 进入并退出兼容模式后，角度模式保持不变
- ✅ 所有配置设置在模式切换后保持一致
- ✅ 配置持久化正确

### 预防措施
1. 建立代码审查清单，检查是否遗留调试代码
2. 使用 `TODO` 或 `FIXME` 标记临时代码
3. 提交前进行完整的回归测试
4. 使用版本控制，方便追踪调试代码的添加位置

---

## 第五轮调试：小数位数配置不生效

### Bug现象
在设置菜单中修改小数位数后，计算结果的小数位数没有立即更新。

### 复现步骤
1. 启动计算器
2. 进行计算 10 / 3，显示 `3.3333`（默认4位小数）
3. 进入设置（菜单7）
4. 修改小数位数为 2
5. 再次计算 10 / 3，仍然显示 `3.3333` 而不是 `3.33`

### 根因分析
**定位文件**: `main.py` + `result_formatter.py`

**问题代码** (main.py):
```python
def handle_settings(self):
    # ...
    elif setting_choice == 2:
        places = input("请输入小数位数 (0-10): ").strip()
        places = int(places)
        self.config.decimal_places = places
        # 忘记更新 formatter！
        print(f"小数位数已设置为: {places}")
```

**问题分析**:
- 配置已更新并保存到文件
- 但 `ScientificCalculator` 类中的 `self.formatter` 实例仍然使用旧的配置
- `ResultFormatter` 实例在初始化时读取配置，之后不会自动同步

### 修复方案

**修改文件**: `main.py`

**修复代码**:
```python
def handle_settings(self):
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
                # 修复：同步更新 formatter
                self.formatter.set_decimal_places(places)  # ✅ 关键修复
                print(f"\n  ✅ 小数位数已设置为: {places}")
            elif setting_choice == 3:
                new_mode = self.config.toggle_compatibility_mode()
                print(f"\n  ✅ 兼容模式: {'开启' if new_mode else '关闭'}")
            elif setting_choice == 4:
                self.formatter.toggle_scientific_notation()
                print(f"\n  ✅ 自动科学计数法: {'开启' if self.formatter.auto_scientific else '关闭'}")
            # ... 其他设置项 ...
```

**同时增强 result_formatter.py 的同步机制**:
```python
class ResultFormatter:
    def set_decimal_places(self, places: int):
        """
        设置小数位数
        
        Args:
            places: 小数位数（0-10）
        """
        if not isinstance(places, int) or places < 0 or places > 10:
            raise ValueError("小数位数必须在0-10之间")
        self.decimal_places = places
```

### 验证结果
- ✅ 修改小数位数后立即生效
- ✅ 配置持久化正确，重启后保持设置
- ✅ 边界值（0位和10位）测试通过

### 预防措施
1. 配置变更时，确保所有依赖该配置的组件都同步更新
2. 使用观察者模式或事件机制实现配置自动同步
3. 编写集成测试验证配置变更流程
4. 添加配置变更的日志记录，便于问题追踪

---

## 调试总结

### 问题分类统计

| 问题类型 | 数量 | 占比 |
|----------|------|------|
| 参数传递错误 | 1 | 20% |
| 边界条件处理 | 1 | 20% |
| 重复数据处理 | 1 | 20% |
| 调试代码遗留 | 1 | 20% |
| 状态同步问题 | 1 | 20% |

### 经验教训

1. **参数传递要显式**: 依赖配置的函数调用必须显式传递参数，避免依赖默认值
2. **边界条件要完整**: 所有数值运算都要考虑边界值（负数、零、极大值等）
3. **重复数据要检测**: 数据层应该具备基本的重复检测能力
4. **调试代码要清理**: 建立代码审查机制，确保调试代码不会进入生产环境
5. **状态同步要及时**: 配置变更时，确保所有相关组件同步更新

### 后续改进建议

1. 引入单元测试框架（如 pytest），覆盖所有运算函数
2. 添加日志记录模块，便于问题追踪
3. 实现配置热重载机制
4. 增加性能监控，检测缓存命中率
