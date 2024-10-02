import logging
import configparser
import re
import os
import inspect
import time
import sys
from typing import List, Dict, Any, Optional
from file_structure_extractor import FileStructureExtractor
from logging_utils import log_info, log_warning, log_error, log_debug

class CodeBlockDetector:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化代码块检测器

        :param config: Dict[str, Any], 配置信息字典
        """
        self.config = config
        log_info("CodeBlockDetector 初始化开始")
        
        self.start_marker = config.get('code_block_detection', 'start_marker', fallback='```')
        self.end_marker = config.get('code_block_detection', 'end_marker', fallback='```')
        self.min_occurrences = config.getint('code_block_detection', 'min_occurrences', fallback=2)
        self.indentation_level = config.getint('code_block_detection', 'indentation_level', fallback=4)
        self.file_types = self._get_file_types_from_config()
        
        log_info("CodeBlockDetector 初始化完成")
        log_info(f"将处理以下文件类型: {', '.join(self.file_types)}")
        log_info(f"文件类型列表长度: {len(self.file_types)}")
        self.gui = None
        self.structure_folder = None
        self.root_folder = None

    def _get_file_types_from_config(self) -> List[str]:
        """
        从配置中获取文件类型列表

        :return: List[str], 文件类型列表
        """
        try:
            file_types_str = self.config.get('FileTypes', 'types')
        except (configparser.NoSectionError, configparser.NoOptionError):
            file_types_str = ''
        
        log_info(f"从配置文件读取到的原始文件类型字符串: '{file_types_str}'")
        file_types = [ft.strip().lower().lstrip('.') for ft in file_types_str.split(',') if ft.strip()]
        log_info(f"处理后的文件类型列表: {file_types}")
        return file_types

    def update_file_types(self, new_file_types_str: str) -> None:
        """
        更新文件类型列表

        :param new_file_types_str: str, 新的文件类型字符串，以逗号分隔
        """
        self.config.set('FileTypes', 'types', new_file_types_str)
        self.file_types = self._get_file_types_from_config()
        log_info(f"文件类型已更新: {', '.join(self.file_types)}")

    def set_gui(self, gui: Any) -> None:
        """
        设置GUI对象

        :param gui: Any, GUI对象
        """
        self.gui = gui

    def log_info(self, message: str, level: str = "info", important: bool = False) -> None:
        """
        记录日志信息

        :param message: str, 日志消息
        :param level: str, 日志级别，默认为 "info"
        :param important: bool, 是否为重要信息，默认为 False
        """
        caller = inspect.currentframe().f_back
        func_name = caller.f_code.co_name
        file_name = os.path.basename(caller.f_code.co_filename)
        log_message = f"[{file_name}:{func_name}] {message}"

        if level == "error":
            log_error(log_message)
        elif level == "warning":
            log_warning(log_message)
        else:
            log_info(log_message)

        if important and hasattr(self, 'gui') and self.gui is not None:
            self.gui.log_info(message, level)

    def detect_code_blocks(self, file_path: str) -> List[Dict[str, Any]]:
        """
        检测指定文件中的代码块

        :param file_path: str, 文件路径
        :return: List[Dict[str, Any]], 检测到的代码块列表
        """
        log_info(f"开始检测代码块，路径: {file_path}")
        log_info(f"使用 structure_folder: {self.structure_folder}")
        log_info(f"使用 root_folder: {self.root_folder}")
        
        log_info(f"开始检测代码块，工作路径: {os.path.abspath(file_path)}", important=True)
        self.code_blocks = []

        if not os.path.isfile(file_path):
            log_error(f"错误: {file_path} 不是一个有效的文件", important=True)
            return self.code_blocks

        if not self.is_valid_file_type(file_path):
            log_info(f"跳过文件: {file_path} (不是配置中指定的文件类型)")
            return self.code_blocks

        self.process_file(file_path)

        log_info(f"代码块检测完成: {file_path}", important=True)
        log_info(f"共检测到 {len(self.code_blocks)} 个代码块", important=True)
        
        if self.code_blocks:
            self.save_code_blocks(os.path.dirname(file_path))
            
            for block_file_path, lang, code in self.code_blocks:
                if self.gui:
                    self.gui.display_code_block(block_file_path, lang, code)
        else:
            log_info("未检测到任何代码块，跳过保存操作", important=True)
        
        return self.code_blocks

    def process_file(self, file_path: str) -> None:
        """
        处理单个文件，查找其中的代码块

        :param file_path: str, 文件路径
        """
        log_info(f"开始处理文件: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.lines = file.readlines()
            log_info(f"成功读取文件 {file_path}，共 {len(self.lines)} 行")
        except Exception as e:
            log_error(f"读取文件 {file_path} 时出错: {str(e)}")
            return

        self.current_line = 0
        while self.current_line < len(self.lines):
            log_info(f"正在处理第 {self.current_line + 1} 行")
            self.find_code_block_start(file_path)
            self.current_line += 1

    def is_valid_file_type(self, filename: str) -> bool:
        """
        检查文件是否是配置中指定的类型

        :param filename: str, 文件名
        :return: bool, 是否为有效文件类型
        """
        file_extension = os.path.splitext(filename)[1].lower().lstrip('.')
        log_info(f"检查文件类型: {filename}, 扩展名: {file_extension}")
        log_info(f"当前有效的文件类型列表: {self.file_types}")
        is_valid = file_extension in self.file_types
        log_info(f"文件 {filename} 是否为有效类型: {is_valid}")
        if not is_valid:
            log_info(f"文件类型 '{file_extension}' 不在有效列表中")
        return is_valid

    def find_code_block_start(self, file_path: str) -> None:
        """
        查找代码块的起始标记

        :param file_path: str, 文件路径
        """
        log_info(f"开始查找代码块起始标记，当前行: {self.current_line + 1}")
        while self.current_line < len(self.lines):
            if self.lines[self.current_line].startswith(self.start_marker):
                code_start = self.lines[self.current_line]
                lang = code_start.strip('`').strip()
                log_info(f"在第 {self.current_line + 1} 行找到代码块开始标记，语言: {lang}")
                
                potential_file_path = self.find_file_path()
                
                if potential_file_path:
                    log_info(f"找到相关文件路径: {potential_file_path}")
                    self.current_line += 1
                    self.extract_code_content(file_path, potential_file_path, lang)
                    return
                else:
                    log_info(f"未找到相关文件路径，跳过此代码块")
                    self.current_line += 1
            else:
                self.current_line += 1

    def find_file_path(self) -> Optional[str]:
        """
        查找相关文件路径

        :return: Optional[str], 找到的文件路径，如果未找到则返回 None
        """
        log_info("开始查找相关文件路径")
        for i in range(1, 3):  # 只向上搜索1到2行
            if self.current_line - i >= 0:
                line = self.lines[self.current_line - i]
                file_path_pattern = r'^##\s+(.*?/.*?\.[a-zA-Z]{1,3})$'
                match = re.match(file_path_pattern, line)
                if match:
                    log_info(f"在第 {self.current_line - i + 1} 行找到文件路径")
                    return match.group(1).strip()
        log_info("未找到相关文件路径")
        return None

    def extract_code_content(self, current_file_path: str, potential_file_path: str, lang: str) -> None:
        """
        提取代码内容

        :param current_file_path: str, 当前文件路径
        :param potential_file_path: str, 潜在的件路径
        :param lang: str, 代码语言
        """
        log_info(f"开始提取代码内容，当前行: {self.current_line + 1}")
        code_lines = []
        start_line = self.current_line
        while self.current_line < len(self.lines) and not self.lines[self.current_line].startswith(self.end_marker):
            code_lines.append(self.lines[self.current_line])
            self.current_line += 1

        if self.current_line < len(self.lines) and self.lines[self.current_line].startswith(self.end_marker):
            code = ''.join(code_lines)
            self.code_blocks.append((potential_file_path, lang, code))
            log_info(f"提取代码块成功: {potential_file_path}")
            log_info(f"代码块范围: 第 {start_line + 1} 行到第 {self.current_line} 行")
            log_info(f"代码块长度: {len(code_lines)} 行")
        else:
            log_warning(f"警告: 未找到代码块结束标记: {current_file_path}")

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置

        :param new_config: Dict[str, Any], 新的配置信息
        """
        log_info("更新 CodeBlockDetector 配置")
        for section, options in new_config.items():
            if section.upper() != 'DEFAULT':
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for option, value in options.items():
                    self.config.set(section, option, str(value))
            else:
                for option, value in options.items():
                    self.config.set(section, option, str(value))

        self.start_marker = self.config.get('code_block_detection', 'start_marker', fallback=self.start_marker)
        self.end_marker = self.config.get('code_block_detection', 'end_marker', fallback=self.end_marker)
        self.min_occurrences = self.config.getint('code_block_detection', 'min_occurrences', fallback=self.min_occurrences)
        self.indentation_level = self.config.getint('code_block_detection', 'indentation_level', fallback=self.indentation_level)
        self.file_types = self._get_file_types_from_config()
        log_info("CodeBlockDetector 配置已更新")
        log_info(f"更新后将处理以下文件类型: {', '.join(self.file_types)}")
        log_info(f"更新后文件类型列表长度: {len(self.file_types)}")
            
    def save_code_blocks(self, base_path: str) -> None:
        """
        保存检测到的代码块

        :param base_path: str, 基础路径
        """
        log_info(f"准备保存代码块，基础路径: {base_path}")
        log_info(f"使用 structure_folder: {self.structure_folder}")
        log_info(f"使用 root_folder: {self.root_folder}")

        if not self.structure_folder or not self.root_folder:
            log_error("错误: 文件结构信息未设置", important=True)
            return

        log_info("开始保存代码块到文件", important=True)
        log_info(f"基础路径: {os.path.abspath(base_path)}")
        
        full_path = os.path.join(base_path, self.structure_folder, self.root_folder)
        log_info(f"调整后的基础路径: {os.path.abspath(full_path)}")
        
        for relative_path, lang, code in self.code_blocks:
            try:
                full_path = os.path.abspath(os.path.join(full_path, relative_path.lstrip('/')))
                
                log_info(f"处理代码块:")
                log_info(f"  相对路径: {relative_path}")
                log_info(f"  完整路径: {full_path}")
                log_info(f"  语言: {lang}")
                
                dir_path = os.path.dirname(full_path)
                os.makedirs(dir_path, exist_ok=True)
                
                file_exists = os.path.exists(full_path)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    if not file_exists:
                        f.write(f"# 此文件不是文件结构中指定的文件，当前保存路径是：{full_path}\n")
                    f.write(f"# File: {relative_path}\n")
                    f.write(f"# Language: {lang}\n")
                    f.write(code)
                
                log_info(f"成功保存代码块到文件: {full_path}", important=True)
                if not file_exists:
                    log_info(f"新创建的文件: {full_path}", important=True)
                log_info(f"文件大小: {os.path.getsize(full_path)} 字节")
            except Exception as e:
                log_error(f"保存代码块到文件时出错:", important=True)
                log_error(f"  目标路径: {full_path}")
                log_error(f"  错误信息: {str(e)}")

    def set_structure_info(self, structure_folder: str, root_folder: str) -> None:
        """
        设置结构文件夹和根文件夹信息

        :param structure_folder: str, 结构文件夹路径
        :param root_folder: str, 根文件夹名称
        """
        self.structure_folder = structure_folder
        self.root_folder = root_folder