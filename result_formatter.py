"""
result_formatter.py - 结果格式化模块

该模块负责：
- 格式化翻译结果
- 词性/例句排版
- 发音链接解析
- 结果展示优化

遵循PEP8规范，所有函数均添加文档字符串。
"""

from typing import Dict, Optional, List, Any
from datetime import datetime


class ResultFormatter:
    """
    结果格式化器类
    
    提供多种格式化选项，优化翻译结果展示。
    """
    
    TERMINAL_WIDTH = 60
    
    def __init__(self, show_pronunciation: bool = True,
                 show_examples: bool = True,
                 show_part_of_speech: bool = True):
        """
        初始化结果格式化器
        
        Args:
            show_pronunciation: 是否显示发音
            show_examples: 是否显示例句
            show_part_of_speech: 是否显示词性
        """
        self._show_pronunciation = show_pronunciation
        self._show_examples = show_examples
        self._show_part_of_speech = show_part_of_speech
    
    def format(self, result: Dict, mode: str = 'professional') -> str:
        """
        格式化翻译结果
        
        Args:
            result: 翻译结果字典
            mode: 显示模式 ('professional' 或 'simple')
            
        Returns:
            格式化后的字符串
        """
        if mode == 'simple':
            return self._format_simple(result)
        return self._format_professional(result)
    
    def _format_simple(self, result: Dict) -> str:
        """
        极简模式格式化
        
        Args:
            result: 翻译结果字典
            
        Returns:
            简洁的翻译结果
        """
        translated_text = result.get('translated_text', '')
        return translated_text
    
    def _format_professional(self, result: Dict) -> str:
        """
        专业模式格式化
        
        Args:
            result: 翻译结果字典
            
        Returns:
            详细的翻译结果
        """
        lines = []
        
        lines.append("=" * self.TERMINAL_WIDTH)
        lines.append("翻译结果")
        lines.append("=" * self.TERMINAL_WIDTH)
        
        source_text = result.get('source_text', '')
        translated_text = result.get('translated_text', '')
        source_lang = result.get('source_lang', 'auto')
        target_lang = result.get('target_lang', 'en')
        engine = result.get('engine', 'unknown')
        from_cache = result.get('from_cache', False)
        
        lines.append(f"\n【原文】({self._get_lang_name(source_lang)})")
        lines.append(self._wrap_text(source_text))
        
        lines.append(f"\n【译文】({self._get_lang_name(target_lang)})")
        lines.append(self._wrap_text(translated_text))
        
        additional_data = result.get('additional_data', {})
        
        if self._show_pronunciation and additional_data:
            pronunciation = self._format_pronunciation(additional_data)
            if pronunciation:
                lines.append(f"\n【发音】")
                lines.append(pronunciation)
        
        if self._show_part_of_speech and additional_data:
            explains = self._format_explains(additional_data)
            if explains:
                lines.append(f"\n【释义】")
                lines.append(explains)
        
        if self._show_examples and additional_data:
            examples = self._format_examples(additional_data)
            if examples:
                lines.append(f"\n【例句】")
                lines.append(examples)
        
        lines.append(f"\n【翻译引擎】{self._get_engine_name(engine)}")
        
        if from_cache:
            lines.append("【缓存状态】命中缓存")
        
        lines.append("=" * self.TERMINAL_WIDTH)
        
        return '\n'.join(lines)
    
    def _get_lang_name(self, lang_code: str) -> str:
        """
        获取语言名称
        
        Args:
            lang_code: 语言代码
            
        Returns:
            语言名称
        """
        lang_map = {
            'zh': '中文',
            'en': '英文',
            'auto': '自动检测',
            'zh-CHS': '中文简体',
            'zh-CN': '中文简体'
        }
        return lang_map.get(lang_code, lang_code)
    
    def _get_engine_name(self, engine_code: str) -> str:
        """
        获取引擎名称
        
        Args:
            engine_code: 引擎代码
            
        Returns:
            引擎名称
        """
        engine_map = {
            'baidu': '百度翻译',
            'youdao': '有道翻译',
            'google': '谷歌翻译'
        }
        return engine_map.get(engine_code, engine_code)
    
    def _wrap_text(self, text: str, width: int = 50) -> str:
        """
        文本换行
        
        Args:
            text: 原始文本
            width: 每行宽度
            
        Returns:
            换行后的文本
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= width:
                wrapped_lines.append(line)
            else:
                while len(line) > width:
                    wrapped_lines.append(line[:width])
                    line = line[width:]
                if line:
                    wrapped_lines.append(line)
        
        return '\n'.join(wrapped_lines)
    
    def _format_pronunciation(self, additional_data: Dict) -> str:
        """
        格式化发音信息
        
        Args:
            additional_data: 附加数据
            
        Returns:
            发音信息字符串
        """
        parts = []
        
        phonetic = additional_data.get('phonetic', '')
        if phonetic:
            parts.append(f"国际音标: [{phonetic}]")
        
        uk_phonetic = additional_data.get('uk_phonetic', '')
        us_phonetic = additional_data.get('us_phonetic', '')
        
        if uk_phonetic or us_phonetic:
            if uk_phonetic:
                parts.append(f"英式: [{uk_phonetic}]")
            if us_phonetic:
                parts.append(f"美式: [{us_phonetic}]")
        
        return '  '.join(parts) if parts else ""
    
    def _format_explains(self, additional_data: Dict) -> str:
        """
        格式化释义信息
        
        Args:
            additional_data: 附加数据
            
        Returns:
            释义信息字符串
        """
        explains = additional_data.get('explains', [])
        
        if not explains:
            return ""
        
        lines = []
        for i, explain in enumerate(explains, 1):
            lines.append(f"  {i}. {explain}")
        
        return '\n'.join(lines)
    
    def _format_examples(self, additional_data: Dict) -> str:
        """
        格式化例句信息
        
        Args:
            additional_data: 附加数据
            
        Returns:
            例句信息字符串
        """
        web_translations = additional_data.get('web_translations', [])
        
        if not web_translations:
            return ""
        
        lines = []
        for i, item in enumerate(web_translations[:3], 1):
            key = item.get('key', '')
            values = item.get('value', [])
            
            if key:
                lines.append(f"  {i}. {key}")
                for value in values[:2]:
                    lines.append(f"     → {value}")
        
        return '\n'.join(lines)
    
    def format_batch_results(self, results: List[Dict]) -> str:
        """
        格式化批量翻译结果
        
        Args:
            results: 翻译结果列表
            
        Returns:
            格式化后的字符串
        """
        lines = []
        lines.append("=" * self.TERMINAL_WIDTH)
        lines.append("批量翻译结果")
        lines.append("=" * self.TERMINAL_WIDTH)
        
        for i, result in enumerate(results, 1):
            source = result.get('source_text', '')
            translated = result.get('translated_text', '')
            error = result.get('error', '')
            
            lines.append(f"\n[{i}] {source}")
            
            if error:
                lines.append(f"    错误: {error}")
            else:
                lines.append(f"    → {translated}")
        
        lines.append("\n" + "=" * self.TERMINAL_WIDTH)
        
        return '\n'.join(lines)
    
    def format_error(self, error_message: str, 
                     error_code: Optional[str] = None) -> str:
        """
        格式化错误信息
        
        Args:
            error_message: 错误信息
            error_code: 错误代码
            
        Returns:
            格式化后的错误字符串
        """
        if error_code:
            return f"[错误 {error_code}] {error_message}"
        return f"[错误] {error_message}"
    
    def format_history_entry(self, entry: Dict, index: int) -> str:
        """
        格式化历史记录条目
        
        Args:
            entry: 历史记录条目
            index: 序号
            
        Returns:
            格式化后的字符串
        """
        source = entry.get('source_text', '')
        translated = entry.get('translated_text', '')
        timestamp = entry.get('timestamp', '')
        engine = entry.get('engine', '')
        
        lines = [
            f"[{index}] {timestamp}",
            f"    原文: {source[:50]}{'...' if len(source) > 50 else ''}",
            f"    译文: {translated[:50]}{'...' if len(translated) > 50 else ''}",
            f"    引擎: {self._get_engine_name(engine)}"
        ]
        
        return '\n'.join(lines)
    
    def format_cache_stats(self, stats: Dict) -> str:
        """
        格式化缓存统计信息
        
        Args:
            stats: 统计信息字典
            
        Returns:
            格式化后的字符串
        """
        lines = []
        lines.append("=" * self.TERMINAL_WIDTH)
        lines.append("缓存统计")
        lines.append("=" * self.TERMINAL_WIDTH)
        lines.append(f"  总缓存数: {stats.get('total_entries', 0)}")
        lines.append(f"  有效缓存: {stats.get('valid_entries', 0)}")
        lines.append(f"  过期缓存: {stats.get('expired_entries', 0)}")
        lines.append(f"  最大容量: {stats.get('max_size', 0)}")
        lines.append(f"  命中次数: {stats.get('hits', 0)}")
        lines.append(f"  未命中次数: {stats.get('misses', 0)}")
        lines.append(f"  命中率: {stats.get('hit_rate', 0):.2%}")
        lines.append("=" * self.TERMINAL_WIDTH)
        
        return '\n'.join(lines)
    
    def format_language_selection(self) -> str:
        """
        格式化语言选择菜单
        
        Returns:
            语言选择菜单字符串
        """
        lines = []
        lines.append("\n选择语言:")
        lines.append("  1. 自动检测")
        lines.append("  2. 中文 → 英文")
        lines.append("  3. 英文 → 中文")
        lines.append("  0. 返回")
        
        return '\n'.join(lines)


def create_formatter(show_pronunciation: bool = True,
                     show_examples: bool = True,
                     show_part_of_speech: bool = True) -> ResultFormatter:
    """
    工厂函数：创建结果格式化器实例
    
    Args:
        show_pronunciation: 是否显示发音
        show_examples: 是否显示例句
        show_part_of_speech: 是否显示词性
        
    Returns:
        ResultFormatter 实例
    """
    return ResultFormatter(
        show_pronunciation=show_pronunciation,
        show_examples=show_examples,
        show_part_of_speech=show_part_of_speech
    )
