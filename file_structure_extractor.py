import os
from datetime import datetime
from file_structure_detector import FileStructureDetector
import traceback
from typing import Dict, Any, Tuple, Optional
from logging_utils import log_info, log_warning, log_error, log_debug

class FileStructureExtractor:
    """
    文件结构提取器类，用于提取和保存文件结构
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化文件结构提取器

        :param config: Dict[str, Any], 配置信息，包含输出目录等设置
        """
        self.config = config
        self.file_structure_detector = FileStructureDetector(config)
        self.gui = None
        self.structure_folder = None
        self.root_folder = None
        log_info("FileStructureExtractor 初始化完成")

    def set_gui(self, gui: Any) -> None:
        """
        设置 GUI 对象

        :param gui: Any, GUI 对象，用于更新界面信息
        :return: None
        """
        self.gui = gui
        self.file_structure_detector.set_gui(gui)

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置信息

        :param new_config: Dict[str, Any], 新的配置信息
        :return: None
        """
        self.config = new_config
        self.file_structure_detector.update_config(new_config)
        log_info("FileStructureExtractor 配置已更新")

    def extract_file_structure(self, directory: str) -> str:
        """
        提取文件结构

        :param directory: str, 要提取结构的目录
        :return: str, 提取的结构
        """
        log_info(f"开始提取文件结构，目录: {directory}")
        structure = self.file_structure_detector.detect_structure(directory)
        log_info("文件结构提取完成")
        
        log_info("开始打印文件结构信息:")
        self._print_structure(structure)
        
        return structure

    def _print_structure(self, structure: str, indent: str = "") -> None:
        """
        打印文件结构信息

        :param structure: str, 文件结构
        :param indent: str, 缩进字符串
        :return: None
        """
        lines = structure.split('\n')
        for line in lines:
            log_info(f"{indent}{line}")

    def create_unique_output_dir(self, output_dir: str) -> str:
        """
        创建唯一的输出目录

        :param output_dir: str, 输出目录路径
        :return: str, 唯一的输出目录路径
        """
        log_info(f"原始输出目录: {output_dir}")
        
        if os.path.basename(output_dir) == 'code':
            base_dir = output_dir
            parent_dir = os.path.dirname(output_dir)
        else:
            base_dir = os.path.join(output_dir, 'code')
            parent_dir = output_dir

        log_info(f"基础目录: {base_dir}")
        log_info(f"父目录: {parent_dir}")

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            log_info(f"创建新目录: {base_dir}")
            return base_dir

        index = 1
        while True:
            new_dir = os.path.join(parent_dir, f"code_{index}")
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
                log_info(f"创建新目录: {new_dir}")
                return new_dir
            index += 1

    def _process_structure(self, structure: str) -> Dict[str, Dict[str, list]]:
        """
        处理提取的结构，区分文件和文件夹，计算层级关系

        :param structure: str, 原始提取的结构（字符串格式）
        :return: Dict[str, Dict[str, list]], 处理后的结构
        """
        log_info("开始处理文件结构...")
        processed_structure = {}
        current_path = []
        last_level = -1
        
        lines = structure.split('\n')
        root_dir = lines[0].strip().rstrip('/')  # 移除根目录末尾的斜杠
        log_info(f"根目录: {root_dir}")
        processed_structure[root_dir] = {'dirs': [], 'files': []}
        current_path.append(root_dir)

        for line in lines[1:]:
            level = self._calculate_level(line)
            item = line.strip().split('── ')[-1].strip()
            
            if level <= last_level:
                current_path = current_path[:level]
            
            if item.endswith('/'):  # 文件夹
                folder = item.rstrip('/')  # 移除末尾的斜杠
                current_path.append(folder)
                
                full_path = '/'.join(filter(None, current_path))  # 使用 filter 移除空字符串
                log_info(f"处理文件夹: {full_path}")
                if full_path not in processed_structure:
                    processed_structure[full_path] = {'dirs': [], 'files': []}
                
                parent_path = '/'.join(filter(None, current_path[:-1]))
                if parent_path not in processed_structure:
                    processed_structure[parent_path] = {'dirs': [], 'files': []}
                if folder not in processed_structure[parent_path]['dirs']:
                    processed_structure[parent_path]['dirs'].append(folder)
            else:  # 文件
                parent_path = '/'.join(filter(None, current_path))
                log_info(f"处理文件: {item} 在 {parent_path}")
                if parent_path not in processed_structure:
                    processed_structure[parent_path] = {'dirs': [], 'files': []}
                if item not in processed_structure[parent_path]['files']:
                    processed_structure[parent_path]['files'].append(item)
            
            last_level = level
        
        log_info("文件结构处理完成")
        log_info(f"处理后的结构键: {list(processed_structure.keys())}")
        return processed_structure

    def _calculate_level(self, line: str) -> int:
        """
        计算给定行的层级

        :param line: str, 文件结构中的一行
        :return: int, 计算出的层级
        """
        if not line.strip():  # 空行
            return -1
        
        level = line.count('│   ') + (1 if '├── ' in line or '└── ' in line else 0)
        return max(0, level)  # 确保层级不小于0

    def save_structure(self, output_dir: str, structure: str) -> Tuple[str, str]:
        """
        根据提取的结构在输出目录中创建相应的文件夹和文件

        :param output_dir: str, 输出目录
        :param structure: str, 提取的结构（字符串形式）
        :return: Tuple[str, str], (structure_folder, root_folder)
        """
        self.structure_folder = self.create_unique_output_dir(output_dir)
        log_info(f"最终使用的输出目录: {self.structure_folder}")
        
        processed_structure = self._process_structure(structure)
        
        log_info(f"处理后的结构键: {list(processed_structure.keys())}")
        
        if not processed_structure:
            log_error("错误: 处理后的结构为空")
            return None, None

        first_key = list(processed_structure.keys())[0]
        log_info(f"第一个键: {first_key}")
        
        self.root_folder = first_key.split('/')[-1]
        log_info(f"根文件夹名称: {self.root_folder}")

        if not self.root_folder:
            log_error("错误: 无法确定根文件夹名称")
            return None, None

        for relative_path, content in processed_structure.items():
            current_path = os.path.normpath(os.path.join(self.structure_folder, relative_path))
            
            os.makedirs(current_path, exist_ok=True)
            log_info(f"创建目录: {current_path}")
            
            for file in content['files']:
                file_path = os.path.normpath(os.path.join(current_path, file))
                with open(file_path, 'w') as f:
                    f.write(f"# This file represents: {os.path.join(relative_path, file)}\n")
                log_info(f"创建文件: {file_path}")
        
        structure_file = os.path.join(self.structure_folder, 'project_structure.md')
        with open(structure_file, 'w') as f:
            f.write("# Project Structure\n\n")
            f.write(structure)
        log_info(f"项目结构描述文件已保存到: {structure_file}")

        log_info(f"文件结构创建完成")
        return self.structure_folder, self.root_folder

    def run(self, directory: str) -> Tuple[Optional[str], Optional[str]]:
        """
        运行文件结构提取和保存的完整流程

        :param directory: str, 要提取结构的目录
        :return: Tuple[Optional[str], Optional[str]], (structure_folder, root_folder) 或 (None, None)
        """
        log_info("开始运行文件结构提取和保存流程...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.config['output']['directory'], f"file_structure_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        log_info(f"创建输出目录: {output_dir}")

        try:
            structure = self.extract_file_structure(directory)
            structure_folder, root_folder = self.save_structure(output_dir, structure)
            log_info(f"文件结构提取和保存流程已完成！")
            log_info(f"结构文件夹: {structure_folder}")
            log_info(f"根文件夹: {root_folder}")
            return structure_folder, root_folder
        except Exception as e:
            log_error(f"错误: 文件结构提取过程中发生异常: {str(e)}")
            log_error(traceback.format_exc())
            return None, None

    def get_structure_folder(self) -> Optional[str]:
        """
        获取结构文件夹路径

        :return: Optional[str], 结构文件夹路径
        """
        return self.structure_folder

    def get_root_folder(self) -> Optional[str]:
        """
        获取根文件夹名称

        :return: Optional[str], 根文件夹名称
        """
        return self.root_folder

if __name__ == "__main__":
    # 这里可以添加一些测试代码或使用示例
    pass