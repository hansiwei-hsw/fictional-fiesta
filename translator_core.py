"""
translator_core.py - 核心翻译引擎模块

该模块负责：
- 多翻译引擎API对接（百度/有道/谷歌）
- 翻译类型判断
- 结果解析
- 网络请求处理

遵循PEP8规范，所有函数均添加文档字符串。
"""

import hashlib
import random
import time
import re
from typing import Dict, Optional, Any, Tuple, List, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    import requests  # type: ignore[misc]

try:
    import requests  # type: ignore[misc]
except ImportError:
    requests = None


class TranslationError(Exception):
    """翻译错误异常"""
    pass


class NetworkError(TranslationError):
    """网络错误异常"""
    pass


class APIError(TranslationError):
    """API错误异常"""
    pass


class BaseTranslator(ABC):
    """
    翻译器基类
    
    定义翻译器接口规范。
    """
    
    def __init__(self, config: Dict, timeout: int = 10, retry_times: int = 3):
        """
        初始化翻译器
        
        Args:
            config: 引擎配置字典
            timeout: 请求超时时间（秒）
            retry_times: 重试次数
        """
        self._config = config
        self._timeout = timeout
        self._retry_times = retry_times
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译结果字典
        """
        pass
    
    @abstractmethod
    def detect_language(self, text: str) -> Optional[str]:
        """
        检测语言
        
        Args:
            text: 待检测文本
            
        Returns:
            语言代码
        """
        pass
    
    def _request_with_retry(self, method: str, url: str, 
                            **kwargs) -> Any:
        """
        带重试的请求
        
        Args:
            method: 请求方法
            url: 请求URL
            **kwargs: 请求参数
            
        Returns:
            响应对象
            
        Raises:
            NetworkError: 网络错误
        """
        if requests is None:
            raise NetworkError("requests库未安装，请运行: pip install requests")
        
        kwargs.setdefault('timeout', self._timeout)
        
        last_error = None
        for attempt in range(self._retry_times):
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                last_error = NetworkError(f"请求超时，已重试 {attempt + 1} 次")
            except requests.exceptions.ConnectionError:
                last_error = NetworkError("网络连接失败，请检查网络")
            except requests.exceptions.HTTPError as e:
                last_error = APIError(f"HTTP错误: {e.response.status_code}")
            except Exception as e:
                last_error = NetworkError(f"请求失败: {str(e)}")
            
            if attempt < self._retry_times - 1:
                time.sleep(1 * (attempt + 1))
        
        raise last_error


class BaiduTranslator(BaseTranslator):
    """
    百度翻译引擎
    
    百度翻译API实现。
    """
    
    API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    LANGUAGE_MAP = {
        'zh': 'zh',
        'en': 'en',
        'auto': 'auto',
        '中文': 'zh',
        '英文': 'en',
        '自动': 'auto'
    }
    
    def __init__(self, config: Dict, timeout: int = 10, retry_times: int = 3):
        """
        初始化百度翻译器
        
        Args:
            config: 配置字典，需包含 app_id 和 secret_key
            timeout: 超时时间
            retry_times: 重试次数
        """
        super().__init__(config, timeout, retry_times)
        self._app_id = config.get('app_id', '')
        self._secret_key = config.get('secret_key', '')
    
    def translate(self, text: str, source_lang: str = 'auto', 
                  target_lang: str = 'en') -> Dict:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言（默认自动检测）
            target_lang: 目标语言（默认英文）
            
        Returns:
            翻译结果字典
        """
        if not self._app_id or not self._secret_key:
            raise APIError("百度翻译API未配置，请设置 app_id 和 secret_key")
        
        source_lang = self._normalize_lang(source_lang)
        target_lang = self._normalize_lang(target_lang)
        
        salt = str(random.randint(32768, 65536))
        sign = self._generate_sign(text, salt)
        
        params = {
            'q': text,
            'from': source_lang,
            'to': target_lang,
            'appid': self._app_id,
            'salt': salt,
            'sign': sign
        }
        
        response = self._request_with_retry('GET', self.API_URL, params=params)
        result = response.json()
        
        return self._parse_response(result, text)
    
    def _normalize_lang(self, lang: str) -> str:
        """
        标准化语言代码
        
        Args:
            lang: 语言代码或名称
            
        Returns:
            标准化的语言代码
        """
        lang = lang.lower().strip()
        return self.LANGUAGE_MAP.get(lang, lang)
    
    def _generate_sign(self, text: str, salt: str) -> str:
        """
        生成签名
        
        Args:
            text: 待翻译文本
            salt: 随机数
            
        Returns:
            签名字符串
        """
        sign_str = f"{self._app_id}{text}{salt}{self._secret_key}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    def _parse_response(self, result: Dict, original_text: str) -> Dict:
        """
        解析API响应
        
        Args:
            result: API返回的JSON
            original_text: 原始文本
            
        Returns:
            标准化的翻译结果
        """
        if 'error_code' in result:
            error_code = result['error_code']
            error_msg = result.get('error_msg', '未知错误')
            raise APIError(f"百度翻译API错误 [{error_code}]: {error_msg}")
        
        if 'trans_result' not in result:
            raise APIError("百度翻译API返回格式异常")
        
        trans_result = result['trans_result']
        
        translated_text = '\n'.join([item['dst'] for item in trans_result])
        
        detected_lang = result.get('from', 'auto')
        
        return {
            'source_text': original_text,
            'translated_text': translated_text,
            'source_lang': detected_lang,
            'target_lang': result.get('to', 'en'),
            'engine': 'baidu',
            'additional_data': {
                'raw_result': trans_result
            }
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        检测语言
        
        Args:
            text: 待检测文本
            
        Returns:
            语言代码
        """
        try:
            result = self.translate(text, source_lang='auto', target_lang='zh')
            return result.get('source_lang')
        except Exception:
            return None


class YoudaoTranslator(BaseTranslator):
    """
    有道翻译引擎
    
    有道翻译API实现。
    """
    
    API_URL = "https://openapi.youdao.com/api"
    LANGUAGE_MAP = {
        'zh': 'zh-CHS',
        'en': 'en',
        'auto': 'auto',
        '中文': 'zh-CHS',
        '英文': 'en',
        '自动': 'auto'
    }
    
    def __init__(self, config: Dict, timeout: int = 10, retry_times: int = 3):
        """
        初始化有道翻译器
        
        Args:
            config: 配置字典，需包含 app_key 和 app_secret
            timeout: 超时时间
            retry_times: 重试次数
        """
        super().__init__(config, timeout, retry_times)
        self._app_key = config.get('app_key', '')
        self._app_secret = config.get('app_secret', '')
    
    def translate(self, text: str, source_lang: str = 'auto',
                  target_lang: str = 'en') -> Dict:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译结果字典
        """
        if not self._app_key or not self._app_secret:
            raise APIError("有道翻译API未配置，请设置 app_key 和 app_secret")
        
        source_lang = self._normalize_lang(source_lang)
        target_lang = self._normalize_lang(target_lang)
        
        curtime = str(int(time.time()))
        salt = str(random.randint(1, 65536))
        sign = self._generate_sign(text, salt, curtime)
        
        params = {
            'q': text,
            'from': source_lang,
            'to': target_lang,
            'appKey': self._app_key,
            'salt': salt,
            'sign': sign,
            'signType': 'v3',
            'curtime': curtime
        }
        
        response = self._request_with_retry('GET', self.API_URL, params=params)
        result = response.json()
        
        return self._parse_response(result, text)
    
    def _normalize_lang(self, lang: str) -> str:
        """标准化语言代码"""
        lang = lang.lower().strip()
        return self.LANGUAGE_MAP.get(lang, lang)
    
    def _generate_sign(self, text: str, salt: str, curtime: str) -> str:
        """生成签名"""
        input_text = text if len(text) <= 20 else text[:10] + str(len(text)) + text[-10:]
        sign_str = f"{self._app_key}{input_text}{salt}{curtime}{self._app_secret}"
        return hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    
    def _parse_response(self, result: Dict, original_text: str) -> Dict:
        """解析API响应"""
        error_code = result.get('errorCode')
        if error_code and error_code != '0':
            raise APIError(f"有道翻译API错误 [{error_code}]")
        
        translations = result.get('translation', [])
        translated_text = '\n'.join(translations) if translations else ''
        
        basic = result.get('basic', {})
        web = result.get('web', [])
        
        return {
            'source_text': original_text,
            'translated_text': translated_text,
            'source_lang': result.get('l', 'auto').split('2')[0],
            'target_lang': result.get('l', 'en').split('2')[-1] if '2' in result.get('l', '') else 'en',
            'engine': 'youdao',
            'additional_data': {
                'phonetic': basic.get('phonetic', ''),
                'uk_phonetic': basic.get('uk-phonetic', ''),
                'us_phonetic': basic.get('us-phonetic', ''),
                'explains': basic.get('explains', []),
                'web_translations': web
            }
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """检测语言"""
        try:
            result = self.translate(text, source_lang='auto', target_lang='zh-CHS')
            return result.get('source_lang')
        except Exception:
            return None


class GoogleTranslator(BaseTranslator):
    """
    谷歌翻译引擎
    
    谷歌翻译API实现（模拟）。
    """
    
    API_URL = "https://translation.googleapis.com/language/translate/v2"
    LANGUAGE_MAP = {
        'zh': 'zh-CN',
        'en': 'en',
        'auto': 'auto',
        '中文': 'zh-CN',
        '英文': 'en'
    }
    
    def __init__(self, config: Dict, timeout: int = 10, retry_times: int = 3):
        """
        初始化谷歌翻译器
        
        Args:
            config: 配置字典，需包含 api_key
            timeout: 超时时间
            retry_times: 重试次数
        """
        super().__init__(config, timeout, retry_times)
        self._api_key = config.get('api_key', '')
    
    def translate(self, text: str, source_lang: str = 'auto',
                  target_lang: str = 'en') -> Dict:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            翻译结果字典
        """
        if not self._api_key:
            raise APIError("谷歌翻译API未配置，请设置 api_key")
        
        source_lang = self._normalize_lang(source_lang)
        target_lang = self._normalize_lang(target_lang)
        
        url = f"{self.API_URL}?key={self._api_key}"
        
        data = {
            'q': text,
            'source': source_lang if source_lang != 'auto' else None,
            'target': target_lang,
            'format': 'text'
        }
        
        data = {k: v for k, v in data.items() if v is not None}
        
        response = self._request_with_retry('POST', url, json=data)
        result = response.json()
        
        return self._parse_response(result, text)
    
    def _normalize_lang(self, lang: str) -> str:
        """标准化语言代码"""
        lang = lang.lower().strip()
        return self.LANGUAGE_MAP.get(lang, lang)
    
    def _parse_response(self, result: Dict, original_text: str) -> Dict:
        """解析API响应"""
        if 'error' in result:
            error = result['error']
            raise APIError(f"谷歌翻译API错误: {error.get('message', '未知错误')}")
        
        translations = result.get('data', {}).get('translations', [])
        translated_text = '\n'.join([t.get('translatedText', '') for t in translations])
        
        detected_lang = translations[0].get('detectedSourceLanguage', 'auto') if translations else 'auto'
        
        return {
            'source_text': original_text,
            'translated_text': translated_text,
            'source_lang': detected_lang,
            'target_lang': 'en',
            'engine': 'google',
            'additional_data': {}
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """检测语言"""
        try:
            result = self.translate(text, source_lang='auto', target_lang='zh-CN')
            return result.get('source_lang')
        except Exception:
            return None


class TranslatorCore:
    """
    翻译核心引擎类
    
    整合多个翻译引擎，提供统一的翻译接口。
    """
    
    ENGINE_MAP = {
        'baidu': BaiduTranslator,
        'youdao': YoudaoTranslator,
        'google': GoogleTranslator
    }
    
    def __init__(self, config_handler, cache_manager=None):
        """
        初始化翻译核心引擎
        
        Args:
            config_handler: 配置管理器实例
            cache_manager: 缓存管理器实例（可选）
        """
        self._config = config_handler
        self._cache = cache_manager
        self._translators: Dict[str, BaseTranslator] = {}
    
    def _get_translator(self, engine: Optional[str] = None) -> BaseTranslator:
        """
        获取翻译器实例
        
        Args:
            engine: 引擎名称
            
        Returns:
            翻译器实例
        """
        engine = engine or self._config.current_engine
        
        if engine not in self._translators:
            if engine not in self.ENGINE_MAP:
                raise TranslationError(f"不支持的翻译引擎: {engine}")
            
            engine_config = self._config.get_engine_config(engine)
            timeout = self._config.get('timeout', 10)
            retry_times = self._config.get('retry_times', 3)
            
            translator_class = self.ENGINE_MAP[engine]
            self._translators[engine] = translator_class(
                config=engine_config,
                timeout=timeout,
                retry_times=retry_times
            )
        
        return self._translators[engine]
    
    def translate(self, text: str, source_lang: str = 'auto',
                  target_lang: str = None, engine: Optional[str] = None) -> Dict:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            
        Returns:
            翻译结果字典
        """
        if not text or not text.strip():
            raise TranslationError("翻译文本不能为空")
        
        engine = engine or self._config.current_engine
        
        if target_lang is None:
            target_lang = self._detect_target_lang(text, source_lang)
        
        if self._cache:
            cached = self._cache.get(text, source_lang, target_lang, engine)
            if cached:
                return {
                    'source_text': cached.source_text,
                    'translated_text': cached.translated_text,
                    'source_lang': cached.source_lang,
                    'target_lang': cached.target_lang,
                    'engine': cached.engine,
                    'additional_data': cached.additional_data,
                    'from_cache': True
                }
        
        translator = self._get_translator(engine)
        result = translator.translate(text, source_lang, target_lang)
        result['from_cache'] = False
        
        if self._cache:
            self._cache.set(
                source_text=text,
                translated_text=result['translated_text'],
                source_lang=result['source_lang'],
                target_lang=result['target_lang'],
                engine=engine,
                additional_data=result.get('additional_data')
            )
        
        return result
    
    def _detect_target_lang(self, text: str, source_lang: str) -> str:
        """
        自动检测目标语言
        
        Args:
            text: 文本
            source_lang: 源语言
            
        Returns:
            目标语言
        """
        if source_lang == 'auto':
            if self._is_chinese(text):
                return 'en'
            else:
                return 'zh'
        elif source_lang in ('zh', '中文'):
            return 'en'
        else:
            return 'zh'
    
    def _is_chinese(self, text: str) -> bool:
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
    
    def detect_language(self, text: str, engine: Optional[str] = None) -> Optional[str]:
        """
        检测语言
        
        Args:
            text: 文本
            engine: 翻译引擎
            
        Returns:
            语言代码
        """
        translator = self._get_translator(engine)
        return translator.detect_language(text)
    
    def batch_translate(self, texts: List[str], source_lang: str = 'auto',
                        target_lang: str = None, engine: Optional[str] = None,
                        chunk_size: int = 5) -> List[Dict]:
        """
        批量翻译
        
        Args:
            texts: 文本列表
            source_lang: 源语言
            target_lang: 目标语言
            engine: 翻译引擎
            chunk_size: 分块大小
            
        Returns:
            翻译结果列表
        """
        results = []
        
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i + chunk_size]
            
            for text in chunk:
                try:
                    result = self.translate(text, source_lang, target_lang, engine)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'source_text': text,
                        'translated_text': '',
                        'error': str(e)
                    })
            
            if i + chunk_size < len(texts):
                time.sleep(0.5)
        
        return results
    
    def switch_engine(self, engine: str) -> bool:
        """
        切换翻译引擎
        
        Args:
            engine: 引擎名称
            
        Returns:
            是否切换成功
        """
        try:
            self._config.current_engine = engine
            return True
        except ValueError:
            return False
    
    def get_available_engines(self) -> List[str]:
        """
        获取可用引擎列表
        
        Returns:
            可用引擎名称列表
        """
        return self._config.get_available_engines()


def create_translator(config_handler, cache_manager=None) -> TranslatorCore:
    """
    工厂函数：创建翻译核心引擎实例
    
    Args:
        config_handler: 配置管理器
        cache_manager: 缓存管理器
        
    Returns:
        TranslatorCore 实例
    """
    return TranslatorCore(config_handler, cache_manager)
