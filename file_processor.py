import os
from tkinter import messagebox
from code_extractor import CodeExtractor
from project_structure import ProjectStructureExtractor
from utils import create_unique_output_dir

class FileProcessor:
    def __init__(self):
        self.code_extractor = CodeExtractor()
        self.structure_extractor = ProjectStructureExtractor()

    def process_files(self, input_dir, output_dir, selected_types, gui):
        gui.log_general("开始执行...", "info")
        gui.progress['value'] = 0
        
        input_dir = input_dir or os.getcwd()
        output_dir = output_dir or os.path.join(os.getcwd(), 'code')
        
        gui.log_general(f"输入目录: {input_dir}", "info")
        gui.log_general(f"输出目录: {output_dir}", "info")
        
        if not os.path.exists(input_dir):
            gui.log_important(f"错误：输入目录不存在！", "error")
            return

        output_dir = create_unique_output_dir(output_dir)
        gui.log_general(f"最终输出目录: {output_dir}", "info")

        gui.log_general(f"选择的文件类型: {selected_types}", "info")

        try:
            # 提取项目结构
            gui.log_general(f"开始从 {input_dir} 提取项目结构...", "info")
            structure_lines = self.structure_extractor.extract_project_structure(input_dir)
            if structure_lines:
                structure_file = os.path.join(output_dir, "project_structure.md")
                with open(structure_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(structure_lines))
                
                # 计算项目结构统计信息
                dir_count = sum(1 for line in structure_lines if line.strip().endswith('/'))
                file_count = len(structure_lines) - dir_count
                
                gui.log_important(f"项目结构已保存到: {structure_file}", "info")
                gui.log_general(f"项目结构提取完成，共 {len(structure_lines)} 行", "info")
                gui.log_general(f"项目结构统计: {dir_count} 个目录, {file_count} 个文件", "info")
            else:
                gui.log_general("未能提取项目结构", "warning")

            file_count = 0
            processed_file_count = 0
            code_block_count = 0
            
            gui.log_general("开始处理文件...", "info")
            
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if not gui.is_running:
                        gui.log_important("操作被用户中断", "warning")
                        return
                    file_count += 1
                    if any(file.endswith(ext) for ext in selected_types):
                        processed_file_count += 1
                        input_path = os.path.join(root, file)
                        gui.log_general(f"正在处理文件: {input_path}", "info")
                        try:
                            with open(input_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            code_blocks = self.code_extractor.extract_code_blocks(content)
                            for path, lang, code in code_blocks:
                                self.save_code_block(output_dir, path, lang, code, gui)
                                code_block_count += 1
                            
                            gui.log_general(f"处理完成: {input_path} (提取了 {len(code_blocks)} 个代码块)", "info")
                        except Exception as e:
                            gui.log_important(f"处理文件时出错 {input_path}: {str(e)}", "error")

                    gui.progress['value'] = (file_count / len(files)) * 100
                    gui.master.update_idletasks()

            # 记录总体统计信息
            stats = (f"处理完成\n"
                     f"项目结构: {dir_count} 个目录, {file_count} 个文件\n"
                     f"共扫描 {file_count} 个文件\n"
                     f"处理了 {processed_file_count} 个文件\n"
                     f"提取了 {code_block_count} 个代码块")
            gui.log_important(stats, "info")
        except Exception as e:
            gui.log_important(f"处理过程中出现错误：\n{str(e)}", "error")
        finally:
            gui.progress['value'] = 100

    def save_code_block(self, output_dir, file_path, lang, code, gui):
        try:
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                # 添加原文件中标记的完整路径行作为注释
                f.write(f"# ## {file_path}\n")
                f.write(f"# 语言: {lang}\n\n")
                f.write(code)
            
            # 获取文件大小
            file_size = os.path.getsize(full_path)
            size_str = self.format_size(file_size)
            
            gui.log_important(f"保存文件: {full_path} (大小: {size_str})", "info")
        except Exception as e:
            gui.log_important(f"保存文件失败: {full_path}, 错误: {str(e)}", "error")

    def format_size(self, size):
        # 将字节转换为更易读的格式
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0