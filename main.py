"""
main.py - 程序入口与交互控制模块

该模块负责：
- 程序入口点
- 交互式菜单展示
- 模式切换
- 功能分发与调用
- 资源管理

遵循PEP8规范，所有函数均添加文档字符串。
"""

import sys
import os
from typing import Optional, List

from config_handler import ConfigHandler, create_config
from cache_manager import CacheManager, create_cache_manager
from translator_core import TranslatorCore, TranslationError, NetworkError, APIError
from input_validator import InputValidator, SimpleInputParser, create_validator
from result_formatter import ResultFormatter, create_formatter
from history_manager import HistoryManager, create_history_manager


class TranslatorApp:
    """
    智能翻译应用程序类
    
    整合所有模块，提供完整的交互式翻译功能。
    """
    
    MENU_WIDTH = 60
    SEPARATOR = "="
    
    def __init__(self):
        """初始化翻译应用程序"""
        self._config = create_config()
        self._cache = create_cache_manager(
            max_size=self._config.get('max_cache_size', 1000),
            expire_hours=self._config.get('cache_expire_hours', 24),
            auto_save=True
        )
        self._validator = create_validator()
        self._formatter = create_formatter(
            show_pronunciation=self._config.get('show_pronunciation', True),
            show_examples=self._config.get('show_examples', True),
            show_part_of_speech=self._config.get('show_part_of_speech', True)
        )
        self._history = create_history_manager(
            auto_save=self._config.get('auto_save_history', True),
            max_records=self._config.get('max_history_records', 500)
        )
        self._translator = TranslatorCore(self._config, self._cache)
        self._simple_parser = SimpleInputParser()
        self._running = True
    
    def run(self) -> None:
        """运行翻译器主循环"""
        self._show_welcome()
        
        while self._running:
            try:
                if self._config.mode == 'simple':
                    self._run_simple_mode()
                else:
                    self._run_professional_mode()
                    
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
        print(" " * 15 + "Python 智能英语翻译小程序 v1.0")
        print(" " * 20 + "欢迎使用！")
        print(self.SEPARATOR * self.MENU_WIDTH)
        
        engine_name = self._get_engine_display_name(self._config.current_engine)
        mode_name = "极简模式" if self._config.mode == 'simple' else "专业模式"
        print(f"\n当前翻译引擎: {engine_name}")
        print(f"当前模式: {mode_name}")
        print("\n提示: 输入 'help' 查看帮助，'quit' 或 'exit' 退出程序")
        print("       输入 'mode' 切换专业/极简模式")
    
    def _run_simple_mode(self) -> None:
        """运行极简模式"""
        print("\n" + "-" * self.MENU_WIDTH)
        user_input = input("请输入要翻译的文本: ").strip()
        
        if not user_input:
            return
        
        if user_input.lower() in ('quit', 'exit', 'q'):
            self._running = False
            return
        
        if user_input.lower() == 'help':
            self._show_help()
            return
        
        if user_input.lower() == 'mode':
            self._toggle_mode()
            return
        
        if user_input.lower() == 'menu':
            self._config.mode = 'professional'
            self._config.save()
            return
        
        is_valid, parsed, error = self._simple_parser.parse(user_input)
        
        if not is_valid:
            self._show_error(error)
            return
        
        self._do_translate(
            parsed['text'],
            parsed['source_lang'],
            parsed['target_lang']
        )
    
    def _run_professional_mode(self) -> None:
        """运行专业模式"""
        self._show_main_menu()
        choice = self._get_user_input("请选择功能")
        
        if choice is None or choice.strip() == '':
            self._show_error("输入不能为空")
            return
        
        self._handle_menu_choice(choice.strip())
    
    def _show_main_menu(self) -> None:
        """显示主菜单"""
        print("\n" + "-" * self.MENU_WIDTH)
        print("主菜单")
        print("-" * self.MENU_WIDTH)
        
        print("\n【翻译功能】")
        print("  1. 英译中")
        print("  2. 中译英")
        print("  3. 自动检测翻译")
        print("  4. 批量翻译")
        
        print("\n【系统功能】")
        print("  5. 切换翻译引擎")
        print("  6. 查看历史记录")
        print("  7. 导出历史记录")
        print("  8. 清空历史记录")
        print("  9. 查看缓存统计")
        print("  10. 清空缓存")
        print("  11. 系统设置")
        print("  12. 帮助信息")
        
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
        
        if choice.lower() == 'mode':
            self._toggle_mode()
            return
        
        handlers = {
            '1': lambda: self._handle_translate('en', 'zh'),
            '2': lambda: self._handle_translate('zh', 'en'),
            '3': lambda: self._handle_translate('auto', None),
            '4': self._handle_batch_translate,
            '5': self._handle_switch_engine,
            '6': self._show_history,
            '7': self._export_history,
            '8': self._clear_history,
            '9': self._show_cache_stats,
            '10': self._clear_cache,
            '11': self._show_settings,
            '12': self._show_help,
            '0': self._exit_app
        }
        
        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            self._show_error(f"无效的选项: {choice}")
    
    def _handle_translate(self, source_lang: str, target_lang: Optional[str]) -> None:
        """
        处理翻译请求
        
        Args:
            source_lang: 源语言
            target_lang: 目标语言
        """
        text = self._get_user_input("请输入要翻译的文本")
        if text is None or not text.strip():
            self._show_error("翻译文本不能为空")
            return
        
        self._do_translate(text.strip(), source_lang, target_lang)
    
    def _do_translate(self, text: str, source_lang: str, 
                      target_lang: Optional[str]) -> None:
        """
        执行翻译
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
        """
        is_valid, processed_text, error = self._validator.validate_text(text)
        if not is_valid:
            self._show_error(error)
            return
        
        if target_lang is None:
            target_lang = self._validator.suggest_target_lang(processed_text, source_lang)
        
        try:
            self._show_message("正在翻译...")
            
            result = self._translator.translate(
                text=processed_text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            formatted = self._formatter.format(result, self._config.mode)
            print(formatted)
            
            self._history.add_record(
                source_text=result['source_text'],
                translated_text=result['translated_text'],
                source_lang=result['source_lang'],
                target_lang=result['target_lang'],
                engine=result['engine'],
                additional_data=result.get('additional_data')
            )
            
        except NetworkError as e:
            self._show_error(f"网络错误: {str(e)}")
        except APIError as e:
            self._show_error(f"API错误: {str(e)}")
        except TranslationError as e:
            self._show_error(f"翻译错误: {str(e)}")
        except Exception as e:
            self._show_error(f"未知错误: {str(e)}")
    
    def _handle_batch_translate(self) -> None:
        """处理批量翻译"""
        print("\n请输入要翻译的文本（每行一条，输入空行结束）:")
        texts = []
        
        while True:
            line = input()
            if not line.strip():
                break
            texts.append(line.strip())
        
        if not texts:
            self._show_error("未输入任何文本")
            return
        
        source_lang = self._get_user_input("请输入源语言（默认auto）") or 'auto'
        target_lang = self._get_user_input("请输入目标语言（默认自动）") or None
        
        is_valid, valid_texts, errors = self._validator.validate_batch_input(texts)
        
        if errors:
            for error in errors:
                self._show_error(error)
        
        if not valid_texts:
            return
        
        try:
            self._show_message(f"正在批量翻译 {len(valid_texts)} 条文本...")
            
            results = self._translator.batch_translate(
                texts=valid_texts,
                source_lang=source_lang,
                target_lang=target_lang
            )
            
            print(self._formatter.format_batch_results(results))
            
            for result in results:
                if 'error' not in result:
                    self._history.add_record(
                        source_text=result['source_text'],
                        translated_text=result['translated_text'],
                        source_lang=result['source_lang'],
                        target_lang=result['target_lang'],
                        engine=result['engine']
                    )
            
        except Exception as e:
            self._show_error(f"批量翻译失败: {str(e)}")
    
    def _handle_switch_engine(self) -> None:
        """处理切换翻译引擎"""
        available_engines = self._translator.get_available_engines()
        
        if not available_engines:
            self._show_error("没有可用的翻译引擎，请先配置API密钥")
            return
        
        print("\n可用的翻译引擎:")
        for i, engine in enumerate(available_engines, 1):
            current = " (当前)" if engine == self._config.current_engine else ""
            print(f"  {i}. {self._get_engine_display_name(engine)}{current}")
        
        choice = self._get_user_input("请选择引擎")
        if choice is None:
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(available_engines):
                new_engine = available_engines[index]
                self._translator.switch_engine(new_engine)
                self._show_success(f"已切换到 {self._get_engine_display_name(new_engine)}")
            else:
                self._show_error("无效的选择")
        except ValueError:
            self._show_error("请输入有效的数字")
    
    def _show_history(self) -> None:
        """显示历史记录"""
        records = self._history.get_all_records()
        
        if not records:
            self._show_message("暂无历史记录")
            return
        
        print("\n" + self.SEPARATOR * self.MENU_WIDTH)
        print("历史记录（最近20条）")
        print(self.SEPARATOR * self.MENU_WIDTH)
        
        for i, record in enumerate(records[-20:], 1):
            print(self._formatter.format_history_entry(record.to_dict(), i))
        
        if len(records) > 20:
            print(f"\n... 共 {len(records)} 条记录")
        
        print(self.SEPARATOR * self.MENU_WIDTH)
    
    def _export_history(self) -> None:
        """导出历史记录"""
        if self._history.is_empty():
            self._show_message("暂无历史记录可导出")
            return
        
        print("\n选择导出格式:")
        print("  1. 文本文件 (.txt)")
        print("  2. CSV文件 (.csv)")
        print("  3. JSON文件 (.json)")
        
        choice = self._get_user_input("请选择格式")
        if choice is None:
            return
        
        exporters = {
            '1': ('txt', self._history.export_to_txt),
            '2': ('csv', self._history.export_to_csv),
            '3': ('json', self._history.export_to_json)
        }
        
        if choice not in exporters:
            self._show_error("无效的选择")
            return
        
        ext, exporter = exporters[choice]
        default_file = f"translation_history.{ext}"
        file_path = self._get_user_input(f"请输入导出文件路径（默认: {default_file})") or default_file
        
        if exporter(file_path):
            self._show_success(f"历史记录已导出到: {file_path}")
        else:
            self._show_error("导出失败，请检查文件路径权限")
    
    def _clear_history(self) -> None:
        """清空历史记录"""
        confirm = self._get_user_input("确认清空所有历史记录？(y/n)")
        if confirm and confirm.lower() == 'y':
            self._history.clear_all()
            self._show_success("历史记录已清空")
        else:
            self._show_message("操作已取消")
    
    def _show_cache_stats(self) -> None:
        """显示缓存统计"""
        stats = self._cache.get_stats()
        print(self._formatter.format_cache_stats(stats))
    
    def _clear_cache(self) -> None:
        """清空缓存"""
        confirm = self._get_user_input("确认清空所有缓存？(y/n)")
        if confirm and confirm.lower() == 'y':
            self._cache.clear()
            self._show_success("缓存已清空")
        else:
            self._show_message("操作已取消")
    
    def _show_settings(self) -> None:
        """显示系统设置"""
        while True:
            print("\n" + self.SEPARATOR * self.MENU_WIDTH)
            print("系统设置")
            print(self.SEPARATOR * self.MENU_WIDTH)
            print(f"  1. 当前引擎: {self._get_engine_display_name(self._config.current_engine)}")
            print(f"  2. 当前模式: {'极简模式' if self._config.mode == 'simple' else '专业模式'}")
            print(f"  3. 缓存启用: {'是' if self._config.get('cache_enabled') else '否'}")
            print(f"  4. 自动保存历史: {'是' if self._config.get('auto_save_history') else '否'}")
            print(f"  5. 显示发音: {'是' if self._config.get('show_pronunciation') else '否'}")
            print(f"  6. 显示例句: {'是' if self._config.get('show_examples') else '否'}")
            print(f"  7. 配置API密钥")
            print("  8. 恢复默认设置")
            print("  0. 返回主菜单")
            print(self.SEPARATOR * self.MENU_WIDTH)
            
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
            self._handle_switch_engine()
        
        elif choice == '2':
            self._toggle_mode()
        
        elif choice == '3':
            current = self._config.get('cache_enabled')
            self._config.set('cache_enabled', not current)
            self._show_success(f"缓存已{'启用' if not current else '禁用'}")
        
        elif choice == '4':
            current = self._config.get('auto_save_history')
            self._config.set('auto_save_history', not current)
            self._show_success(f"自动保存历史已{'启用' if not current else '禁用'}")
        
        elif choice == '5':
            current = self._config.get('show_pronunciation')
            self._config.set('show_pronunciation', not current)
            self._formatter._show_pronunciation = not current
            self._show_success(f"显示发音已{'启用' if not current else '禁用'}")
        
        elif choice == '6':
            current = self._config.get('show_examples')
            self._config.set('show_examples', not current)
            self._formatter._show_examples = not current
            self._show_success(f"显示例句已{'启用' if not current else '禁用'}")
        
        elif choice == '7':
            self._configure_api_keys()
        
        elif choice == '8':
            confirm = self._get_user_input("确认恢复默认设置？(y/n)")
            if confirm and confirm.lower() == 'y':
                self._config.reset_to_default()
                self._show_success("已恢复默认设置")
            else:
                self._show_message("操作已取消")
    
    def _configure_api_keys(self) -> None:
        """配置API密钥"""
        print("\n选择要配置的翻译引擎:")
        print("  1. 百度翻译")
        print("  2. 有道翻译")
        print("  3. 谷歌翻译")
        
        choice = self._get_user_input("请选择")
        if choice is None:
            return
        
        engine_map = {'1': 'baidu', '2': 'youdao', '3': 'google'}
        
        if choice not in engine_map:
            self._show_error("无效的选择")
            return
        
        engine = engine_map[choice]
        
        if engine == 'baidu':
            app_id = self._get_user_input("请输入百度翻译 App ID")
            secret_key = self._get_user_input("请输入百度翻译 Secret Key")
            if app_id and secret_key:
                self._config.set_engine_config(engine, {
                    'app_id': app_id,
                    'secret_key': secret_key,
                    'enabled': True
                })
                self._show_success("百度翻译配置成功")
        
        elif engine == 'youdao':
            app_key = self._get_user_input("请输入有道翻译 App Key")
            app_secret = self._get_user_input("请输入有道翻译 App Secret")
            if app_key and app_secret:
                self._config.set_engine_config(engine, {
                    'app_key': app_key,
                    'app_secret': app_secret,
                    'enabled': True
                })
                self._show_success("有道翻译配置成功")
        
        elif engine == 'google':
            api_key = self._get_user_input("请输入谷歌翻译 API Key")
            if api_key:
                self._config.set_engine_config(engine, {
                    'api_key': api_key,
                    'enabled': True
                })
                self._show_success("谷歌翻译配置成功")
    
    def _toggle_mode(self) -> None:
        """切换模式"""
        current = self._config.mode
        new_mode = 'simple' if current == 'professional' else 'professional'
        self._config.mode = new_mode
        self._show_success(f"已切换到{'极简模式' if new_mode == 'simple' else '专业模式'}")
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        print("\n" + self.SEPARATOR * self.MENU_WIDTH)
        print("帮助信息")
        print(self.SEPARATOR * self.MENU_WIDTH)
        
        print("\n【翻译功能】")
        print("  支持英译中、中译英双向翻译")
        print("  支持单词、句子、段落翻译")
        print("  支持批量翻译")
        
        print("\n【翻译引擎】")
        print("  - 百度翻译: 需配置 App ID 和 Secret Key")
        print("  - 有道翻译: 需配置 App Key 和 App Secret")
        print("  - 谷歌翻译: 需配置 API Key")
        
        print("\n【快捷命令】")
        print("  help    - 显示帮助信息")
        print("  mode    - 切换专业/极简模式")
        print("  quit/exit - 退出程序")
        
        print("\n【极简模式】")
        print("  直接输入文本即可翻译")
        print("  支持格式:")
        print("    - hello          (自动检测翻译)")
        print("    - en:你好        (指定目标语言)")
        print("    - en>zh:hello    (指定源语言和目标语言)")
        
        print("\n" + self.SEPARATOR * self.MENU_WIDTH)
    
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
    
    def _get_engine_display_name(self, engine: str) -> str:
        """
        获取引擎显示名称
        
        Args:
            engine: 引擎代码
            
        Returns:
            引擎显示名称
        """
        names = {
            'baidu': '百度翻译',
            'youdao': '有道翻译',
            'google': '谷歌翻译'
        }
        return names.get(engine, engine)
    
    def _show_message(self, message: str) -> None:
        """显示普通消息"""
        print(f"\n[信息] {message}")
    
    def _show_error(self, error: str) -> None:
        """显示错误消息"""
        print(f"\n[错误] {error}")
    
    def _show_success(self, message: str) -> None:
        """显示成功消息"""
        print(f"\n[成功] {message}")
    
    def _exit_app(self) -> None:
        """退出应用程序"""
        self._running = False
    
    def _cleanup(self) -> None:
        """清理资源"""
        if self._history.is_modified():
            self._history.save()
        
        if self._cache:
            self._cache.save()
        
        self._config.save()
        
        print("\n" + self.SEPARATOR * self.MENU_WIDTH)
        print("感谢使用 Python 智能英语翻译小程序 v1.0！")
        print("再见！")
        print(self.SEPARATOR * self.MENU_WIDTH + "\n")


def main():
    """程序入口点"""
    try:
        app = TranslatorApp()
        app.run()
    except Exception as e:
        print(f"\n程序发生严重错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
