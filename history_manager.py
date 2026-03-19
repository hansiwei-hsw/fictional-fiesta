"""
history_manager.py - 历史记录模块

该模块负责：
- 离线保存翻译记录
- 读取历史记录
- 清空历史记录
- 导出历史记录
- 加密存储

遵循PEP8规范，所有函数均添加文档字符串。
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path


class HistoryEncryption:
    """
    历史记录加密工具类
    
    使用简单的Base64+哈希混淆进行加密。
    """
    
    _KEY_SALT = "history_v1.0_salt"
    
    @classmethod
    def encrypt(cls, data: str) -> str:
        """
        加密字符串
        
        Args:
            data: 原始字符串
            
        Returns:
            加密后的字符串
        """
        key = hashlib.sha256(cls._KEY_SALT.encode()).digest()
        data_bytes = data.encode('utf-8')
        xored = bytes([data_bytes[i] ^ key[i % len(key)] for i in range(len(data_bytes))])
        return base64.b64encode(xored).decode('utf-8')
    
    @classmethod
    def decrypt(cls, data: str) -> str:
        """
        解密字符串
        
        Args:
            data: 加密后的字符串
            
        Returns:
            原始字符串
        """
        try:
            key = hashlib.sha256(cls._KEY_SALT.encode()).digest()
            data_bytes = base64.b64decode(data.encode('utf-8'))
            xored = bytes([data_bytes[i] ^ key[i % len(key)] for i in range(len(data_bytes))])
            return xored.decode('utf-8')
        except Exception:
            return ""


class HistoryRecord:
    """
    历史记录条目类
    
    表示单条翻译记录。
    """
    
    def __init__(self, source_text: str, translated_text: str,
                 source_lang: str, target_lang: str, engine: str,
                 timestamp: Optional[str] = None,
                 additional_data: Optional[Dict] = None):
        """
        初始化历史记录条目
        
        Args:
            source_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            timestamp: 时间戳
            additional_data: 附加数据
        """
        self.source_text = source_text
        self.translated_text = translated_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.engine = engine
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.additional_data = additional_data or {}
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            包含所有属性的字典
        """
        return {
            'source_text': self.source_text,
            'translated_text': self.translated_text,
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'engine': self.engine,
            'timestamp': self.timestamp,
            'additional_data': self.additional_data
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
            source_text=data['source_text'],
            translated_text=data['translated_text'],
            source_lang=data['source_lang'],
            target_lang=data['target_lang'],
            engine=data['engine'],
            timestamp=data.get('timestamp'),
            additional_data=data.get('additional_data')
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.timestamp}] {self.source_text[:30]} → {self.translated_text[:30]}"
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"HistoryRecord({self.source_text[:20]}...)"


class HistoryManager:
    """
    历史记录管理器类
    
    管理翻译历史记录的增删改查和持久化。
    """
    
    DEFAULT_FILE = "translator_history.json"
    MAX_RECORDS = 500
    
    def __init__(self, history_file: Optional[str] = None,
                 max_records: int = 500,
                 auto_save: bool = True,
                 encrypt: bool = True):
        """
        初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
            max_records: 最大记录数
            auto_save: 是否自动保存
            encrypt: 是否加密存储
        """
        self._history: List[HistoryRecord] = []
        self._history_file = history_file or self.DEFAULT_FILE
        self._max_records = max_records
        self._auto_save = auto_save
        self._encrypt = encrypt
        self._modified = False
        
        self._load_history()
    
    def add_record(self, source_text: str, translated_text: str,
                   source_lang: str, target_lang: str, engine: str,
                   additional_data: Optional[Dict] = None) -> HistoryRecord:
        """
        添加历史记录
        
        Args:
            source_text: 原文
            translated_text: 译文
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            additional_data: 附加数据
            
        Returns:
            新创建的历史记录条目
        """
        record = HistoryRecord(
            source_text=source_text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            engine=engine,
            additional_data=additional_data
        )
        
        if self._is_duplicate(record):
            return self._get_existing_record(record)
        
        if len(self._history) >= self._max_records:
            self._history.pop(0)
        
        self._history.append(record)
        self._modified = True
        
        if self._auto_save:
            self.save()
        
        return record
    
    def _is_duplicate(self, record: HistoryRecord) -> bool:
        """
        检查是否重复记录
        
        Args:
            record: 历史记录条目
            
        Returns:
            是否重复
        """
        for existing in self._history:
            if (existing.source_text == record.source_text and
                existing.source_lang == record.source_lang and
                existing.target_lang == record.target_lang and
                existing.engine == record.engine):
                return True
        return False
    
    def _get_existing_record(self, record: HistoryRecord) -> HistoryRecord:
        """
        获取已存在的记录
        
        Args:
            record: 历史记录条目
            
        Returns:
            已存在的记录
        """
        for existing in self._history:
            if (existing.source_text == record.source_text and
                existing.source_lang == record.source_lang and
                existing.target_lang == record.target_lang and
                existing.engine == record.engine):
                return existing
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
            历史记录条目
        """
        if 0 <= index < len(self._history):
            return self._history[index]
        return None
    
    def get_last_record(self) -> Optional[HistoryRecord]:
        """
        获取最后一条记录
        
        Returns:
            最后一条历史记录
        """
        if self._history:
            return self._history[-1]
        return None
    
    def get_records_by_date(self, date_str: str) -> List[HistoryRecord]:
        """
        按日期筛选记录
        
        Args:
            date_str: 日期字符串（格式：YYYY-MM-DD）
            
        Returns:
            匹配的历史记录列表
        """
        return [r for r in self._history if r.timestamp.startswith(date_str)]
    
    def get_records_by_engine(self, engine: str) -> List[HistoryRecord]:
        """
        按引擎筛选记录
        
        Args:
            engine: 翻译引擎
            
        Returns:
            匹配的历史记录列表
        """
        return [r for r in self._history if r.engine.lower() == engine.lower()]
    
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
            if (keyword in record.source_text.lower() or
                keyword in record.translated_text.lower()):
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
                content = f.read()
            
            if self._encrypt:
                content = HistoryEncryption.decrypt(content)
                if not content:
                    return
            
            data = json.loads(content)
            
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
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            if self._encrypt:
                json_data = HistoryEncryption.encrypt(json_data)
            
            with open(self._history_file, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            self._modified = False
            return True
            
        except IOError as e:
            return False
    
    def export_to_txt(self, file_path: str) -> bool:
        """
        导出历史记录到文本文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("翻译历史记录导出\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"记录总数: {len(self._history)}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, record in enumerate(self._history, 1):
                    f.write(f"[{i}] {record.timestamp}\n")
                    f.write(f"原文 ({record.source_lang}): {record.source_text}\n")
                    f.write(f"译文 ({record.target_lang}): {record.translated_text}\n")
                    f.write(f"引擎: {record.engine}\n")
                    f.write("-" * 60 + "\n")
            
            return True
            
        except IOError:
            return False
    
    def export_to_json(self, file_path: str) -> bool:
        """
        导出历史记录到JSON文件
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            data = [record.to_dict() for record in self._history]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except IOError:
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
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write("序号,时间,源语言,目标语言,原文,译文,引擎\n")
                
                for i, record in enumerate(self._history, 1):
                    source = record.source_text.replace('"', '""')
                    translated = record.translated_text.replace('"', '""')
                    f.write(f'{i},{record.timestamp},{record.source_lang},'
                           f'{record.target_lang},"{source}","{translated}",'
                           f'{record.engine}\n')
            
            return True
            
        except IOError:
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
                'engines': {},
                'languages': {},
                'first_record': None,
                'last_record': None
            }
        
        engine_counts: Dict[str, int] = {}
        language_counts: Dict[str, int] = {}
        
        for record in self._history:
            engine_counts[record.engine] = engine_counts.get(record.engine, 0) + 1
            
            lang_pair = f"{record.source_lang}->{record.target_lang}"
            language_counts[lang_pair] = language_counts.get(lang_pair, 0) + 1
        
        return {
            'total': len(self._history),
            'engines': engine_counts,
            'languages': language_counts,
            'first_record': self._history[0].timestamp,
            'last_record': self._history[-1].timestamp
        }
    
    def is_modified(self) -> bool:
        """
        检查是否已修改
        
        Returns:
            是否已修改
        """
        return self._modified
    
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
                           max_records: int = 500,
                           auto_save: bool = True,
                           encrypt: bool = True) -> HistoryManager:
    """
    工厂函数：创建历史记录管理器实例
    
    Args:
        history_file: 历史记录文件路径
        max_records: 最大记录数
        auto_save: 是否自动保存
        encrypt: 是否加密存储
        
    Returns:
        HistoryManager 实例
    """
    return HistoryManager(
        history_file=history_file,
        max_records=max_records,
        auto_save=auto_save,
        encrypt=encrypt
    )
