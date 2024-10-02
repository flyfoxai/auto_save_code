from logging_utils import log_info, log_warning, log_error, log_debug
import os
from typing import Dict, Any

class CodeBlockMetadataExtractor:
    """
    代码块元数据提取器类
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化代码块元数据提取器

        :param config: Dict[str, Any], 配置信息字典
        """
        self.config = config
        self.gui = None
        log_info("CodeBlockMetadataExtractor 初始化完成")

    def set_gui(self, gui: Any) -> None:
        """
        设置 GUI 对象

        :param gui: Any, GUI 对象
        :return: None
        """
        self.gui = gui

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        提取文件元数据

        :param file_path: str, 文件路径
        :return: Dict[str, Any], 元数据字典
        """
        log_info(f"开始提取元数据: {file_path}")
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'last_modified': os.path.getmtime(file_path)
        }
        # 可以添加更多元数据提取逻辑
        log_info(f"元数据提取完成: {file_path}")
        return metadata

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置

        :param new_config: Dict[str, Any], 新的配置信息
        :return: None
        """
        self.config = new_config
        log_info("CodeBlockMetadataExtractor 配置已更新")

    def set_structure_info(self, structure_folder: str, root_folder: str) -> None:
        """
        设置结构文件夹和根文件夹信息

        :param structure_folder: str, 结构文件夹路径
        :param root_folder: str, 根文件夹名称
        :return: None
        """
        self.structure_folder = structure_folder
        self.root_folder = root_folder
        log_info(f"设置结构文件夹: {structure_folder}")
        log_info(f"设置根文件夹: {root_folder}")