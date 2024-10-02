import os
import re
from typing import Dict, Any, Optional, List, Tuple
from logging_utils import log_info, log_warning, log_error, log_debug

class FileStructureDetector:
    """
    文件结构检测器类
    用于在指定目录下的文件中查找并提取文件结构描述
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化文件结构检测器

        :param config: Dict[str, Any], 配置对象，包含文件类型等设置
        """
        self.config = config
        self.file_types = config.get('FileTypes', 'types').split(',')
        self.gui = None
        log_info("FileStructureDetector 初始化完成")

    def set_gui(self, gui: Any) -> None:
        """
        设置 GUI 对象，用于在界面上显示日志信息

        :param gui: Any, GUI 对象
        :return: None
        """
        self.gui = gui
        log_info("GUI 对象已设置")

    def detect_structure(self, directory: str) -> Optional[str]:
        """
        在指定目录下检测文件结构（仅检查当前目录，不包括子目录）

        :param directory: str, 要检测的目录路径
        :return: Optional[str], 检测到的文件结构，如果未找到则返回 None
        """
        log_info(f"开始检测目录结构: {directory}")
        structure = None

        try:
            for entry in os.scandir(directory):
                if entry.is_file() and any(entry.name.endswith(ext) for ext in self.file_types):
                    file_path = entry.path
                    log_info(f"正在检查文件: {file_path}")
                    file_structure = self.find_structure_in_file(file_path)
                    if file_structure:
                        structure = file_structure
                        log_info(f"在文件 {entry.name} 中找到文件结构")
                        break

            if not structure:
                log_info("未找到任何文件结构")

        except Exception as e:
            log_error(f"访问目录 {directory} 时出错: {str(e)}")

        log_info(f"structure 的类型: {type(structure)}")
        if structure:
            log_info(f"structure 的值类型: {type(structure)}")

        return structure

    def find_structure_in_file(self, file_path: str) -> Optional[str]:
        """
        在指定文件中查找文件结构描述

        :param file_path: str, 文件路径
        :return: Optional[str], 找到的文件结构描述，如果未找到则返回 None
        """
        log_info(f"开始处理文件: {file_path}")
        content = self._read_file_content(file_path)
        if content is None:
            return None

        log_info(f"文件 {file_path} 内容读取完成，长度: {len(content)} 字符")

        pattern = r'^.*[│├└].*$'
        log_info("开始搜索包含特殊符号的行")
        structure_lines = re.findall(pattern, content, re.MULTILINE)

        if structure_lines:
            return self._process_structure_lines(content, structure_lines)
        else:
            log_info(f"在文件 {file_path} 中未找到任何包含特殊符号的行")
            return None

    def _read_file_content(self, file_path: str) -> Optional[str]:
        """
        读取文件内容，尝试不同的编码方式

        :param file_path: str, 文件路径
        :return: Optional[str], 文件内容，如果无法读取则返回 None
        """
        encodings = ['utf-8', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                log_error(f"处理文件 {file_path} 时出错: {str(e)}")
                return None
        log_error(f"无法读取文件 {file_path}: 尝试了所有可能的编码")
        return None

    def _process_structure_lines(self, content: str, structure_lines: List[str]) -> Optional[str]:
        """
        处理找到的结构行

        :param content: str, 文件全部内容
        :param structure_lines: List[str], 包含结构信息的行
        :return: Optional[str], 处理后的结构描述，如果无效则返回 None
        """
        log_info(f"找到 {len(structure_lines)} 个包含特殊符号的行")
        
        content_lines = content.split('\n')
        structure = []
        start_index = -1
        end_index = -1

        # 查找结构的开始和结束
        for i, line in enumerate(content_lines):
            if re.match(r'^.*[│├└].*$', line):
                if start_index == -1:
                    start_index = i
                    if i > 0:
                        structure.append(content_lines[i - 1].strip() + '/')
                structure.append(line.rstrip())
                if line.lstrip().startswith('└'):
                    end_index = i
                    break
            elif start_index != -1 and not line.strip():
                end_index = i - 1
                break

        if structure:
            final_structure = '\n'.join(structure)
            log_info(f"找到有效的文件结构，共 {len(structure)} 行")
            log_info(f"找到的结构:\n{final_structure}")
            return final_structure
        else:
            log_info("未找到有效的连续文件结构")
            return None

    def _is_valid_file(self, filename: str) -> bool:
        """
        检查文件是否是我们要处理的类型

        :param filename: str, 文件名
        :return: bool, 表示是否是有效文件
        """
        return any(filename.endswith(ext.strip()) for ext in self.file_types)

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        更新配置

        :param new_config: Dict[str, Any], 新的配置信息
        :return: None
        """
        self.config = new_config
        self.file_types = new_config.get('FileTypes', 'types').split(',')
        self.max_depth = new_config.getint('StructureDiscovery', 'max_depth', fallback=None)
        self.exclude_dirs = new_config.get('StructureDiscovery', 'exclude_dirs', fallback='').split(',')
        log_info("FileStructureDetector 配置已更新")

    def save_structure(self, output_dir: str, structure: str) -> Tuple[str, str]:
        """
        根据提取的结构在输出目录中创建相应的文件夹和文件

        :param output_dir: str, 输出目录
        :param structure: str, 提取的结构（字符串形式）
        :return: Tuple[str, str], (structure_folder, root_folder)
        """
        self.structure_folder = self.create_unique_output_dir(output_dir)
        log_info(f"最终使用的输出目录: {self.structure_folder}")
        
        processed_structure = self._convert_structure_to_dict(structure)
        
        log_info(f"处理后的结构键1: {list(processed_structure.keys())}")
        
        if not processed_structure:
            log_error("错误: 处理后的结构为空")
            return None, None

        first_key = list(processed_structure.keys())[0]
        log_info(f"第一个键: {first_key}")
        
        self.root_folder = first_key.split('/')[-1] if '/' in first_key else first_key
        log_info(f"根文件夹名称: {self.root_folder}")

        if not self.root_folder:
            log_error("错误: 无法确定根文件夹名称")
            return None, None

        for relative_path, content in processed_structure.items():
            current_path = os.path.join(self.structure_folder, relative_path)
            
            os.makedirs(current_path, exist_ok=True)
            log_info(f"创建目录: {current_path}")
            
            for file in content['files']:
                file_path = os.path.join(current_path, file)
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

    def _convert_structure_to_dict(self, structure: str) -> Dict[str, Dict[str, list]]:
        """
        将字符串形式的结构描述转换为字典格式

        :param structure: str, 原始的结构描述（字符串格式）
        :return: Dict[str, Dict[str, list]], 处理后的结构字典
        """
        log_info("开始将文件结构转换为字典...")
        processed_structure = {}
        current_path = []
        last_level = -1
        
        lines = structure.split('\n')
        log_info(f"原始结构的行数: {len(lines)}")
        log_info(f"原始结构的第一行: {lines[0] if lines else 'No lines'}")
        
        if not lines:
            log_error("错误: 结构字符串为空")
            return processed_structure

        root_dir = lines[0].strip().rstrip('/')
        log_info(f"处理后的根目录: {root_dir}")
        processed_structure[root_dir] = {'dirs': [], 'files': []}
        current_path.append(root_dir)

        for line in lines[1:]:
            level = self._calculate_level(line)
            item = line.strip().split('── ')[-1].strip()
            log_info(f"处理行: {line}")
            log_info(f"提取的项目: {item}")
            
            if level <= last_level:
                current_path = current_path[:level]
            
            if item.endswith('/'):  # 文件夹
                folder = item.rstrip('/')  # 移除末尾的斜杠
                current_path.append(folder)
                
                full_path = '/'.join(filter(None, current_path))  # 使用 filter 移除空字符串
                log_info(f"当前完整路径: {full_path}")
                if full_path not in processed_structure:
                    processed_structure[full_path] = {'dirs': [], 'files': []}
                
                parent_path = '/'.join(filter(None, current_path[:-1]))
                if parent_path not in processed_structure:
                    processed_structure[parent_path] = {'dirs': [], 'files': []}
                if folder not in processed_structure[parent_path]['dirs']:
                    processed_structure[parent_path]['dirs'].append(folder)
            else:  # 文件
                parent_path = '/'.join(filter(None, current_path))
                if parent_path not in processed_structure:
                    processed_structure[parent_path] = {'dirs': [], 'files': []}
                if item not in processed_structure[parent_path]['files']:
                    processed_structure[parent_path]['files'].append(item)
            
            last_level = level
        
        log_info("文件结构转换为字典完成")
        log_info(f"处理后的结构键2: {list(processed_structure.keys())}")
        return processed_structure