"""
input_validator.py - 输入校验模块

该模块负责：
- 验证翻译文本合法性
- 语种选择验证
- 批量输入格式验证
- 特殊字符处理

遵循PEP8规范，所有函数均添加文档字符串。
"""

import re
from typing import Tuple, Optional, List


class ValidationError(Exception):
    """验证错误异常"""
    pass


class InputValidator:
    """
    输入校验器类
    
    提供各种输入验证功能。
    """
    
    MAX_TEXT_LENGTH = 5000
    MIN_TEXT_LENGTH = 1
    
    VALID_LANGUAGES = {
        'zh', 'en', 'auto',
        '中文', '英文', '自动',
        'chinese', 'english'
    }
    
    LANGUAGE_MAP = {
        '中文': 'zh',
        '英文': 'en',
        '自动': 'auto',
        'chinese': 'zh',
        'english': 'en'
    }
    
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
    ]
    
    def __init__(self, max_length: int = 5000):
        """
        初始化输入校验器
        
        Args:
            max_length: 最大文本长度
        """
        self._max_length = max_length
    
    def validate_text(self, text: str) -> Tuple[bool, str, str]:
        """
        验证翻译文本
        
        Args:
            text: 待验证文本
            
        Returns:
            (是否有效, 处理后的文本, 错误信息)
        """
        if text is None:
            return False, "", "输入不能为空"
        
        text = text.strip()
        
        if not text:
            return False, "", "输入不能为空"
        
        if len(text) < self.MIN_TEXT_LENGTH:
            return False, "", f"输入文本过短，最少需要 {self.MIN_TEXT_LENGTH} 个字符"
        
        if len(text) > self._max_length:
            return False, "", f"输入文本过长，最多支持 {self._max_length} 个字符"
        
        sanitized = self._sanitize_text(text)
        
        return True, sanitized, ""
    
    def _sanitize_text(self, text: str) -> str:
        """
        清理文本中的危险字符
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        result = text
        
        for pattern in self.DANGEROUS_PATTERNS:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.DOTALL)
        
        result = result.replace('\r\n', '\n').replace('\r', '\n')
        
        return result
    
    def validate_language(self, lang: str) -> Tuple[bool, str, str]:
        """
        验证语言选择
        
        Args:
            lang: 语言代码或名称
            
        Returns:
            (是否有效, 标准化的语言代码, 错误信息)
        """
        if lang is None or not lang.strip():
            return True, 'auto', ""
        
        lang = lang.strip().lower()
        
        if lang in self.LANGUAGE_MAP:
            return True, self.LANGUAGE_MAP[lang], ""
        
        if lang in self.VALID_LANGUAGES:
            return True, lang, ""
        
        return False, "", f"无效的语言选择: {lang}，支持的选项: {self.VALID_LANGUAGES}"
    
    def validate_source_target_lang(self, source_lang: str, 
                                     target_lang: str) -> Tuple[bool, str]:
        """
        验证源语言和目标语言组合
        
        Args:
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            (是否有效, 错误信息)
        """
        _, source_code, _ = self.validate_language(source_lang)
        _, target_code, _ = self.validate_language(target_lang)
        
        if source_code != 'auto' and source_code == target_code:
            return False, "源语言和目标语言不能相同"
        
        return True, ""
    
    def detect_text_type(self, text: str) -> str:
        """
        检测文本类型
        
        Args:
            text: 文本
            
        Returns:
            文本类型 ('word', 'sentence', 'paragraph')
        """
        text = text.strip()
        
        if '\n' in text:
            return 'paragraph'
        
        if ' ' in text:
            return 'sentence'
        
        return 'word'
    
    def is_chinese(self, text: str) -> bool:
        """
        判断文本是否为中文
        
        Args:
            text: 文本
            
        Returns:
            是否为中文
        """
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        chinese_chars = len(chinese_pattern.findall(text))
        return chinese_chars > len(text) * 0.3
    
    def is_english(self, text: str) -> bool:
        """
        判断文本是否为英文
        
        Args:
            text: 文本
            
        Returns:
            是否为英文
        """
        english_pattern = re.compile(r'[a-zA-Z]')
        english_chars = len(english_pattern.findall(text))
        return english_chars > len(text) * 0.3
    
    def suggest_target_lang(self, text: str, source_lang: str = 'auto') -> str:
        """
        建议目标语言
        
        Args:
            text: 文本
            source_lang: 源语言
            
        Returns:
            建议的目标语言
        """
        if source_lang == 'zh':
            return 'en'
        elif source_lang == 'en':
            return 'zh'
        
        if self.is_chinese(text):
            return 'en'
        elif self.is_english(text):
            return 'zh'
        
        return 'zh'
    
    def validate_batch_input(self, texts: List[str]) -> Tuple[bool, List[str], List[str]]:
        """
        验证批量输入
        
        Args:
            texts: 文本列表
            
        Returns:
            (是否全部有效, 有效的文本列表, 错误信息列表)
        """
        valid_texts = []
        errors = []
        
        for i, text in enumerate(texts):
            is_valid, processed_text, error = self.validate_text(text)
            
            if is_valid:
                valid_texts.append(processed_text)
            else:
                errors.append(f"第 {i + 1} 项: {error}")
        
        return len(errors) == 0, valid_texts, errors
    
    def parse_file_input(self, file_content: str, 
                         delimiter: str = '\n') -> Tuple[bool, List[str], str]:
        """
        解析文件输入
        
        Args:
            file_content: 文件内容
            delimiter: 分隔符
            
        Returns:
            (是否有效, 文本列表, 错误信息)
        """
        if not file_content or not file_content.strip():
            return False, [], "文件内容为空"
        
        lines = file_content.split(delimiter)
        texts = [line.strip() for line in lines if line.strip()]
        
        if not texts:
            return False, [], "未找到有效的翻译内容"
        
        return self.validate_batch_input(texts)
    
    def format_text_for_api(self, text: str) -> str:
        """
        格式化文本用于API调用
        
        Args:
            text: 原始文本
            
        Returns:
            格式化后的文本
        """
        text = text.strip()
        
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        text = re.sub(r' {2,}', ' ', text)
        
        return text
    
    def truncate_text(self, text: str, max_length: int = None) -> Tuple[str, bool]:
        """
        截断文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            (截断后的文本, 是否被截断)
        """
        max_length = max_length or self._max_length
        
        if len(text) <= max_length:
            return text, False
        
        return text[:max_length], True
    
    def count_words(self, text: str) -> int:
        """
        统计单词数（英文）或字符数（中文）
        
        Args:
            text: 文本
            
        Returns:
            单词数或字符数
        """
        text = text.strip()
        
        if self.is_chinese(text):
            chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
            return len(chinese_pattern.findall(text))
        else:
            words = text.split()
            return len(words)
    
    def validate_menu_choice(self, choice: str, 
                             valid_range: range) -> Tuple[bool, Optional[int], str]:
        """
        验证菜单选择
        
        Args:
            choice: 用户输入的选择
            valid_range: 有效范围
            
        Returns:
            (是否有效, 选择值, 错误信息)
        """
        if choice is None or choice.strip() == '':
            return False, None, "请输入选项编号"
        
        choice = choice.strip()
        
        try:
            num = int(choice)
        except ValueError:
            return False, None, f"请输入有效的数字选项"
        
        if num not in valid_range:
            return False, None, f"选项 {num} 不在有效范围内 ({valid_range.start}-{valid_range.stop - 1})"
        
        return True, num, ""


class SimpleInputParser:
    """
    极简模式输入解析器
    
    用于解析极简模式的输入格式。
    """
    
    def __init__(self):
        """初始化极简模式解析器"""
        self._validator = InputValidator()
    
    def parse(self, user_input: str) -> Tuple[bool, dict, str]:
        """
        解析用户输入
        
        支持格式：
        - 直接输入文本（自动检测语言）
        - "en:hello" 或 "zh:你好"（指定目标语言）
        - "en>zh:hello"（指定源语言和目标语言）
        
        Args:
            user_input: 用户输入
            
        Returns:
            (是否有效, 解析结果字典, 错误信息)
        """
        if not user_input or not user_input.strip():
            return False, {}, "输入不能为空"
        
        user_input = user_input.strip()
        
        if ':' in user_input:
            return self._parse_with_colon(user_input)
        
        return self._parse_simple(user_input)
    
    def _parse_simple(self, text: str) -> Tuple[bool, dict, str]:
        """
        解析简单格式（纯文本）
        
        Args:
            text: 文本
            
        Returns:
            解析结果
        """
        is_valid, processed_text, error = self._validator.validate_text(text)
        
        if not is_valid:
            return False, {}, error
        
        target_lang = self._validator.suggest_target_lang(processed_text)
        
        return True, {
            'text': processed_text,
            'source_lang': 'auto',
            'target_lang': target_lang
        }, ""
    
    def _parse_with_colon(self, user_input: str) -> Tuple[bool, dict, str]:
        """
        解析带冒号的格式
        
        Args:
            user_input: 用户输入
            
        Returns:
            解析结果
        """
        parts = user_input.split(':', 1)
        
        if len(parts) != 2:
            return False, {}, "格式错误，请使用 '目标语言:文本' 或 '源语言>目标语言:文本'"
        
        lang_part = parts[0].strip()
        text = parts[1].strip()
        
        is_valid, processed_text, error = self._validator.validate_text(text)
        if not is_valid:
            return False, {}, error
        
        if '>' in lang_part:
            lang_parts = lang_part.split('>')
            if len(lang_parts) == 2:
                source_lang = lang_parts[0].strip()
                target_lang = lang_parts[1].strip()
                
                _, source_code, _ = self._validator.validate_language(source_lang)
                _, target_code, _ = self._validator.validate_language(target_lang)
                
                return True, {
                    'text': processed_text,
                    'source_lang': source_code,
                    'target_lang': target_code
                }, ""
        
        _, target_code, _ = self._validator.validate_language(lang_part)
        
        return True, {
            'text': processed_text,
            'source_lang': 'auto',
            'target_lang': target_code or 'zh'
        }, ""


def create_validator(max_length: int = 5000) -> InputValidator:
    """
    工厂函数：创建输入校验器实例
    
    Args:
        max_length: 最大文本长度
        
    Returns:
        InputValidator 实例
    """
    return InputValidator(max_length=max_length)
