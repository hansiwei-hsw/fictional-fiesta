"""
历史记录管理模块

本模块负责管理计算历史记录，包括保存、读取、清空、导出等功能。
支持内存缓存和文件持久化存储。

作者: Development Team
版本: 2.0.0
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class HistoryRecord:
    """历史记录数据类"""
    timestamp: str
    operation: str
    expression: str
    result: str
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryRecord':
        """从字典创建"""
        return cls(**data)
    
    def __str__(self) -> str:
        """字符串表示"""
        status = "✓" if self.success else "✗"
        if self.success:
            return f"[{self.timestamp}] {status} {self.expression} = {self.result}"
        else:
            return f"[{self.timestamp}] {status} {self.expression} -> 错误: {self.error_message}"


class HistoryManager:
    """历史记录管理器类"""
    
    # 默认历史文件路径
    DEFAULT_HISTORY_FILE = "calculator_history.json"
    
    # 最大历史记录数（防止内存占用过高）
    MAX_HISTORY_SIZE = 1000
    
    def __init__(self, history_file: str = None, max_size: int = None):
        """
        初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
            max_size: 最大历史记录数
        """
        self.history_file = history_file or self.DEFAULT_HISTORY_FILE
        self.max_size = max_size or self.MAX_HISTORY_SIZE
        self._records: List[HistoryRecord] = []
        self._load_history()
    
    def _load_history(self):
        """从文件加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._records = [
                        HistoryRecord.from_dict(record) 
                        for record in data.get('records', [])
                    ]
            except (json.JSONDecodeError, IOError, KeyError) as e:
                print(f"警告: 加载历史记录失败 - {e}")
                self._records = []
    
    def _save_history(self):
        """保存历史记录到文件"""
        try:
            data = {
                'version': '2.0.0',
                'last_updated': datetime.now().isoformat(),
                'records': [record.to_dict() for record in self._records]
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"警告: 保存历史记录失败 - {e}")
    
    def add_record(
        self, 
        operation: str, 
        expression: str, 
        result: str,
        success: bool = True,
        error_message: str = None
    ) -> HistoryRecord:
        """
        添加历史记录
        
        Args:
            operation: 运算名称
            expression: 表达式
            result: 结果
            success: 是否成功
            error_message: 错误信息（失败时）
        
        Returns:
            创建的记录
        """
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
    
    def get_history(self, limit: int = None) -> List[HistoryRecord]:
        """
        获取历史记录
        
        Args:
            limit: 返回的最大记录数，None表示全部
        
        Returns:
            历史记录列表（按时间倒序）
        """
        records = list(reversed(self._records))
        if limit:
            records = records[:limit]
        return records
    
    def get_successful_records(self, limit: int = None) -> List[HistoryRecord]:
        """
        获取成功的历史记录
        
        Args:
            limit: 返回的最大记录数
        
        Returns:
            成功的历史记录列表
        """
        records = [r for r in reversed(self._records) if r.success]
        if limit:
            records = records[:limit]
        return records
    
    def clear_history(self) -> int:
        """
        清空历史记录
        
        Returns:
            清空的记录数
        """
        count = len(self._records)
        self._records = []
        self._save_history()
        return count
    
    def export_to_txt(self, filename: str = None) -> str:
        """
        导出历史记录为文本文件
        
        Args:
            filename: 导出文件名，默认使用当前时间命名
        
        Returns:
            导出的文件路径
        """
        if filename is None:
            filename = f"calculator_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("科学计算器 v2.0 - 历史记录导出\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                if not self._records:
                    f.write("暂无历史记录\n")
                else:
                    for i, record in enumerate(self._records, 1):
                        f.write(f"{i}. {record}\n")
                
                f.write("\n" + "=" * 60 + "\n")
                f.write(f"总计: {len(self._records)} 条记录\n")
            
            return filename
        except IOError as e:
            raise IOError(f"导出失败: {e}")
    
    def search_history(self, keyword: str) -> List[HistoryRecord]:
        """
        搜索历史记录
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的历史记录列表
        """
        keyword = keyword.lower()
        return [
            r for r in self._records 
            if keyword in r.expression.lower() or 
               keyword in r.operation.lower() or
               keyword in r.result.lower()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取历史统计信息
        
        Returns:
            统计信息字典
        """
        total = len(self._records)
        successful = sum(1 for r in self._records if r.success)
        failed = total - successful
        
        # 统计各运算使用次数
        operation_counts = {}
        for r in self._records:
            op = r.operation
            operation_counts[op] = operation_counts.get(op, 0) + 1
        
        # 排序获取最常用的运算
        top_operations = sorted(
            operation_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            'total_records': total,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            'top_operations': top_operations,
        }
    
    def __len__(self) -> int:
        """返回历史记录数量"""
        return len(self._records)
    
    def __iter__(self):
        """迭代器支持"""
        return iter(self._records)


# 全局历史管理器实例
_history_manager: Optional[HistoryManager] = None


def get_history_manager() -> HistoryManager:
    """获取全局历史管理器实例"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager


def set_history_manager(manager: HistoryManager):
    """设置全局历史管理器实例"""
    global _history_manager
    _history_manager = manager
