import logging
from code_block_detector import CodeBlockDetector
from code_block_metadata_extractor import CodeBlockMetadataExtractor
import os
import inspect
import time
from typing import Dict, Any, List, Tuple, Optional
from logging_utils import log_info, log_warning, log_error, log_debug

class CodeBlockProcessor:
    """
    代码块处理器类，用于处理和管理代码块的检测和元数据提取
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化代码块处理器

        :param config: Dict[str, Any], 配置信息字典
        """
        self.config = config
        self.code_block_detector = CodeBlockDetector(config)
        self.metadata_extractor = CodeBlockMetadataExtractor(config)
        self.gui = None
        self.structure_folder = None
        self.root_folder = None
        log_info("CodeBlockProcessor 初始化完成")

    def set_gui(self, gui: Any) -> None:
        """
        设置 GUI 对象

        :param gui: Any, GUI 对象，用于更新界面信息
        :return: None
        """
        self.gui = gui
        self.code_block_detector.set_gui(gui)
        self.metadata_extractor.set_gui(gui)

    def extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        提取单个文件的元数据

        :param file_path: str, 文件路径
        :return: Dict[str, Any], 包含文件元数据的字典
        :return: Dict[str, Any], 处理结果字典，包含元数据和代码块信息
        """
        log_info(f"开始处理文件: {file_path}")
        result = {
            'metadata': self.metadata_extractor.extract_metadata(file_path),
            'code_blocks': self.code_block_detector.detect_code_blocks(file_path)
        }
        log_info(f"文件处理完成: {file_path}")
        return result

    def process_files(self, input_dir: str, output_dir: str, file_types: List[str], gui: Any, structure_folder: str, root_folder: str) -> Tuple[int, int, int]:
        """
        处理指定目录下的所有文件

        :param input_dir: str, 输入目录
        :param output_dir: str, 输出目录
        :param file_types: List[str], 要处理的文件类型列表
        :param gui: Any, GUI对象，用于更新进度和日志
        :param structure_folder: str, 结构文件夹路径
        :param root_folder: str, 根文件夹名称
        :return: Tuple[int, int, int], 元组 (总文件数, 处理的文件数, 代码块数)
        """
        self.set_structure_info(structure_folder, root_folder)
        
        total_files = 0
        processed_files = 0
        code_block_count = 0

        log_info(f"开始处理文件 - 输入目录: {input_dir}, 输出目录: {output_dir}")
        log_info(f"处理的文件类型: {', '.join(file_types)}")

        if not os.path.isdir(input_dir):
            log_error(f"输入目录不存在或不是一个有效的目录: {input_dir}")
            return total_files, processed_files, code_block_count

        # 预处理文件类型列表
        processed_file_types = [ft.lower().lstrip('.') for ft in file_types]
        log_info(f"处理后的文件类型列表: {processed_file_types}")

        # 只扫描 input_dir 中的文件，不包括子目录
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        log_info(f"正在扫描目录: {input_dir}")
        log_info(f"当前目录中的文件数量: {len(files)}")
        
        for file in files:
            file_extension = os.path.splitext(file)[1].lower().lstrip('.')
            if file_extension in processed_file_types or (not file_extension and '' in processed_file_types):
                total_files += 1
                file_path = os.path.join(input_dir, file)
                log_info(f"处理文件: {file_path}")
                
                try:
                    code_blocks = self.code_block_detector.detect_code_blocks(file_path)
                    
                    if code_blocks:
                        processed_files += 1
                        code_block_count += len(code_blocks)
                        log_info(f"文件 {file_path} 处理完成，发现 {len(code_blocks)} 个代码块")
                    else:
                        log_info(f"文件 {file_path} 中未发现代码块")
                except Exception as e:
                    log_error(f"处理文件时出错 {file_path}: {str(e)}")
            else:
                log_info(f"跳过不匹配的文件: {file} (扩展名: {file_extension})")

        log_info(f"目录 {input_dir} 扫描完成")
        log_info(f"文件处理完成 - 总文件数: {total_files}, 处理的文件数: {processed_files}, 提取的代码块数: {code_block_count}")
        return total_files, processed_files, code_block_count

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置

        :param new_config: Dict[str, Any], 新的配置信息
        :return: None
        """
        self.config = new_config
        self.code_block_detector.update_config(new_config)
        self.metadata_extractor.update_config(new_config)
        log_info("CodeBlockProcessor 配置已更新")

    def set_structure_info(self, structure_folder: str, root_folder: str) -> None:
        """
        设置结构文件夹和根文件夹信息

        :param structure_folder: str, 结构文件夹路径
        :param root_folder: str, 根文件夹名称
        :return: None
        """
        self.code_block_detector.set_structure_info(structure_folder, root_folder)
        log_info(f"结构信息已设置 - structure_folder: {structure_folder}, root_folder: {root_folder}")