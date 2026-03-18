"""
history_manager.py - 历史记录模块

该模块负责：
- 保存运算记录
- 读取历史记录
- 清空历史记录
- 导出历史记录到文件

遵循PEP8规范，所有函数均添加文档字符串。
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path


class HistoryRecord:
    """
    历史记录条目类
    
    表示单条运算记录。
    """
    
    def __init__(self, operation: str, operands: List[Union[int, float]], 
                 result: Union[int, float], timestamp: Optional[str] = None):
        """
        初始化历史记录条目
        
        Args:
            operation: 运算类型
            operands: 操作数列表
            result: 运算结果
            timestamp: 时间戳（可选，默认为当前时间）
        """
        self.operation = operation
        self.operands = operands
        self.result = result
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            包含所有属性的字典
        """
        return {
            'operation': self.operation,
            'operands': self.operands,
            'result': self.result,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HistoryRecord':
        """
        从字典创建历史记录条目
        
        Args:
            data: 包含记录数据的字典
            
        Returns:
            HistoryRecord 实例
        """
        return cls(
            operation=data['operation'],
            operands=data['operands'],
            result=data['result'],
            timestamp=data.get('timestamp')
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        operands_str = ', '.join(str(op) for op in self.operands)
        if len(self.operands) == 1:
            return f"[{self.timestamp}] {self.operation}({operands_str}) = {self.result}"
        elif len(self.operands) == 2:
            return f"[{self.timestamp}] {self.operands[0]} {self.operation} {self.operands[1]} = {self.result}"
        return f"[{self.timestamp}] {self.operation}({operands_str}) = {self.result}"
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"HistoryRecord({self.operation}, {self.operands}, {self.result})"


class HistoryManager:
    """
    历史记录管理器类
    
    管理运算历史记录的增删改查和持久化。
    """
    
    DEFAULT_FILE = "calculator_history.json"
    MAX_RECORDS = 1000
    
    def __init__(self, history_file: Optional[str] = None, 
                 max_records: int = 1000,
                 auto_save: bool = True):
        """
        初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径（可选）
            max_records: 最大记录数
            auto_save: 是否自动保存
        """
        self._history: List[HistoryRecord] = []
        self._history_file = history_file or self.DEFAULT_FILE
        self._max_records = max_records
        self._auto_save = auto_save
        self._modified = False
        
        self._load_history()
    
    @property
    def history_file(self) -> str:
        """获取历史记录文件路径"""
        return self._history_file
    
    @history_file.setter
    def history_file(self, path: str) -> None:
        """
        设置历史记录文件路径
        
        Args:
            path: 新的文件路径
        """
        self._history_file = path
    
    def add_record(self, operation: str, operands: List[Union[int, float]], 
                   result: Union[int, float]) -> HistoryRecord:
        """
        添加历史记录
        
        Args:
            operation: 运算类型
            operands: 操作数列表
            result: 运算结果
            
        Returns:
            新创建的历史记录条目
        """
        record = HistoryRecord(operation, operands, result)
        
        if len(self._history) >= self._max_records:
            self._history.pop(0)
        
        self._history.append(record)
        self._modified = True
        
        if self._auto_save:
            self.save()
        
        return record
    
    def get_all_records(self) -> List[HistoryRecord]:
        """
        获取所有历史记录
        
        Returns:
            历史记录列表
        """
        return self._history.copy()
    
    def get_record(self, index: int) -> Optional[HistoryRecord]:
        """
        获取指定索引的历史记录
        
        Args:
            index: 记录索引
            
        Returns:
            历史记录条目，如果不存在返回None
        """
        if 0 <= index < len(self._history):
            return self._history[index]
        return None
    
    def get_last_record(self) -> Optional[HistoryRecord]:
        """
        获取最后一条记录
        
        Returns:
            最后一条历史记录，如果为空返回None
        """
        if self._history:
            return self._history[-1]
        return None
    
    def get_records_by_operation(self, operation: str) -> List[HistoryRecord]:
        """
        按运算类型筛选记录
        
        Args:
            operation: 运算类型
            
        Returns:
            匹配的历史记录列表
        """
        return [r for r in self._history if r.operation.lower() == operation.lower()]
    
    def get_records_by_date(self, date_str: str) -> List[HistoryRecord]:
        """
        按日期筛选记录
        
        Args:
            date_str: 日期字符串（格式：YYYY-MM-DD）
            
        Returns:
            匹配的历史记录列表
        """
        return [r for r in self._history if r.timestamp.startswith(date_str)]
    
    def search_records(self, keyword: str) -> List[HistoryRecord]:
        """
        搜索历史记录
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的历史记录列表
        """
        keyword = keyword.lower()
        results = []
        for record in self._history:
            if (keyword in record.operation.lower() or
                any(keyword in str(op) for op in record.operands) or
                keyword in str(record.result)):
                results.append(record)
        return results
    
    def delete_record(self, index: int) -> bool:
        """
        删除指定索引的记录
        
        Args:
            index: 记录索引
            
        Returns:
            是否删除成功
        """
        if 0 <= index < len(self._history):
            del self._history[index]
            self._modified = True
            if self._auto_save:
                self.save()
            return True
        return False
    
    def clear_all(self) -> None:
        """清空所有历史记录"""
        self._history.clear()
        self._modified = True
        if self._auto_save:
            self.save()
    
    def count(self) -> int:
        """
        获取记录数量
        
        Returns:
            记录数量
        """
        return len(self._history)
    
    def is_empty(self) -> bool:
        """
        检查是否为空
        
        Returns:
            是否为空
        """
        return len(self._history) == 0
    
    def _load_history(self) -> None:
        """从文件加载历史记录"""
        if not os.path.exists(self._history_file):
            return
        
        try:
            with open(self._history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._history = [HistoryRecord.from_dict(item) for item in data]
            self._modified = False
            
        except (json.JSONDecodeError, IOError, KeyError) as e:
            self._history = []
    
    def save(self) -> bool:
        """
        保存历史记录到文件
        
        Returns:
            是否保存成功
        """
        try:
            data = [record.to_dict() for record in self._history]
            
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self._modified = False
            return True
            
        except IOError as e:
            return False
    
    def export_to_txt(self, file_path: str, 
                      include_header: bool = True) -> bool:
        """
        导出历史记录到文本文件
        
        Args:
            file_path: 导出文件路径
            include_header: 是否包含文件头
            
        Returns:
            是否导出成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if include_header:
                    f.write("=" * 60 + "\n")
                    f.write("计算器历史记录导出\n")
                    f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"记录总数: {len(self._history)}\n")
                    f.write("=" * 60 + "\n\n")
                
                for i, record in enumerate(self._history, 1):
                    f.write(f"{i}. {str(record)}\n")
                
                if include_header:
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("导出完成\n")
            
            return True
            
        except IOError as e:
            return False
    
    def export_to_csv(self, file_path: str) -> bool:
        """
        导出历史记录到CSV文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("序号,时间戳,运算类型,操作数,结果\n")
                
                for i, record in enumerate(self._history, 1):
                    operands_str = ';'.join(str(op) for op in record.operands)
                    f.write(f"{i},{record.timestamp},{record.operation},"
                           f"\"{operands_str}\",{record.result}\n")
            
            return True
            
        except IOError as e:
            return False
    
    def get_statistics(self) -> Dict:
        """
        获取历史记录统计信息
        
        Returns:
            统计信息字典
        """
        if not self._history:
            return {
                'total': 0,
                'operations': {},
                'first_record': None,
                'last_record': None
            }
        
        operation_counts: Dict[str, int] = {}
        for record in self._history:
            op = record.operation
            operation_counts[op] = operation_counts.get(op, 0) + 1
        
        return {
            'total': len(self._history),
            'operations': operation_counts,
            'first_record': self._history[0].timestamp,
            'last_record': self._history[-1].timestamp
        }
    
    def __len__(self) -> int:
        """返回记录数量"""
        return len(self._history)
    
    def __iter__(self):
        """迭代支持"""
        return iter(self._history)
    
    def __getitem__(self, index: int) -> HistoryRecord:
        """索引访问支持"""
        return self._history[index]


def create_history_manager(history_file: Optional[str] = None,
                           max_records: int = 1000,
                           auto_save: bool = True) -> HistoryManager:
    """
    工厂函数：创建历史记录管理器实例
    
    Args:
        history_file: 历史记录文件路径
        max_records: 最大记录数
        auto_save: 是否自动保存
        
    Returns:
        HistoryManager 实例
    """
    return HistoryManager(
        history_file=history_file,
        max_records=max_records,
        auto_save=auto_save
    )
