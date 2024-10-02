import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
from file_structure_extractor import FileStructureExtractor
from code_block_processor import CodeBlockProcessor
from code_block_detector import CodeBlockDetector
from utils import create_unique_output_dir, normalize_path, is_valid_path, get_comment_syntax
import yaml
import logging
import traceback
import inspect
from typing import Dict, Any
from datetime import datetime
from logging_utils import get_logger

class AutoSaveCodeGUI:
    """
    自动保存代码的图形用户界面类
    """

    def __init__(self, master: tk.Tk, config: Dict[str, Any]):
        """
        初始化 AutoSaveCodeGUI 类

        :param master: tkinter 主窗口
        :param config: 配置信息字典
        """
        self.master = master
        self.master.title("Auto Save Code")
        self.master.geometry("800x600")

        self.config = config

        self.structure_extractor = FileStructureExtractor(self.config)
        self.code_processor = CodeBlockProcessor(self.config)
        self.code_block_detector = CodeBlockDetector(self.config)

        self.is_running = False
        self.create_widgets()

        self.code_block_detector.set_gui(self)

        # 设置日志
        self.logger = get_logger()
        self.logger.set_gui(self)

    def create_widgets(self):
        """
        创建GUI窗口中的各种控件

        :return: None
        """
        # 创建主框架
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # 输入目录
        ttk.Label(main_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_dir = tk.StringVar(value=os.getcwd())
        ttk.Entry(main_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        # 输出目录
        ttk.Label(main_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "code"))
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # 文件类型
        ttk.Label(main_frame, text="文件类型 (用逗号分隔):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_types = tk.StringVar(value=self.config.get('FileTypes', 'types'))
        ttk.Entry(main_frame, textvariable=self.file_types, width=50).grid(row=2, column=1, padx=5, pady=5)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        # 执行按钮
        self.execute_button = ttk.Button(button_frame, text="执行", command=self.execute)
        self.execute_button.pack(side=tk.LEFT, padx=5)

        # 设置按钮
        self.settings_button = ttk.Button(button_frame, text="设置", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        # 退出按钮
        self.exit_button = ttk.Button(button_frame, text="退出", command=self.exit_program)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # 日志文本框
        self.log_text = tk.Text(main_frame, wrap=tk.WORD, width=80, height=20)
        self.log_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=5, column=3, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def browse_input(self):
        """
        打开文件对话框选择输入目录

        :return: None
        """
        directory = filedialog.askdirectory(initialdir=self.input_dir.get())
        if directory:
            self.input_dir.set(directory)

    def browse_output(self):
        """
        打开文件对话框选择输出目录

        :return: None
        """
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)

    def execute(self):
        """
        执行主程序，在新线程中运行 execute_thread 方法

        :return: None
        """
        self.is_running = True
        threading.Thread(target=self.execute_thread, daemon=True).start()

    def execute_thread(self):
        """
        主程序执行线程，处理文件结构提取和代码块检测

        :return: None
        """
        try:
            input_dir = self.input_dir.get()
            output_dir = self.output_dir.get()
            self.log_info(f"输入目录: {input_dir}")
            self.log_info(f"输出目录: {output_dir}")
            
            file_types = [t.strip() for t in self.file_types.get().split(',')]
            self.log_info(f"文件类型: {file_types}")
            
            # 设置 GUI 对象
            self.structure_extractor.set_gui(self)
            
            self.log_info("正在提取项目结构...")
            structure = self.structure_extractor.extract_file_structure(input_dir)
            
            self.log_info("正在创建文件结构...")
            structure_folder, root_folder = self.structure_extractor.save_structure(output_dir, structure)
            
            if structure_folder and root_folder:
                self.log_info(f"文件结构已保存。结构文件夹: {structure_folder}, 根文件夹: {root_folder}")
                
                # 设置 CodeBlockProcessor 的结构信息
                self.code_processor.set_structure_info(structure_folder, root_folder)
                
                # 更新进度条
                self.update_progress(0)
                
                try:
                    # 处理文件
                    total_files, processed_files, code_block_count = self.code_processor.process_files(
                        input_dir=input_dir, 
                        output_dir=output_dir, 
                        file_types=file_types, 
                        gui=self,
                        structure_folder=structure_folder,
                        root_folder=root_folder
                    )
                    
                    if all(isinstance(x, int) for x in (total_files, processed_files, code_block_count)):
                        self.display_statistics(total_files, processed_files, code_block_count)
                    else:
                        self.log_info("错误: 处理文件返回了无效的统计数据", level="error")
                except Exception as e:
                    self.log_info(f"处理文件时出错: {str(e)}", level="error")
                finally:
                    # 完成后更新进度条
                    self.update_progress(100)
            else:
                self.log_info("错误: 无法保存文件结构", level="error")
        except Exception as e:
            self.log_info(f"执行过程中出错: {str(e)}", "error")
            self.logger.error(f"执行过程中出错: {str(e)}\n{traceback.format_exc()}")
        finally:
            self.is_running = False

    def open_settings(self):
        """
        打开设置窗口

        :return: None
        """
        settings_window = tk.Toplevel(self.master)
        settings_window.title("设置")

        # 创建设置界面的各个部分
        self.create_file_types_settings(settings_window)
        self.create_extraction_settings(settings_window)
        self.create_output_settings(settings_window)
        self.create_structure_discovery_settings(settings_window)
        self.create_code_block_detection_settings(settings_window)

        # 保存按钮
        save_button = ttk.Button(settings_window, text="保存", command=lambda: self.save_settings(settings_window))
        save_button.pack(pady=10)

    def create_file_types_settings(self, parent: tk.Toplevel):
        """
        创建文件类型设置部分的控件

        :param parent: 父窗口
        :return: None
        """
        frame = ttk.LabelFrame(parent, text="文件类型设置")
        frame.pack(padx=10, pady=5, fill=tk.X)

        ttk.Label(frame, text="文件类型 (用逗号分隔):").grid(row=0, column=0, padx=5, pady=5)
        self.file_types_entry = ttk.Entry(frame)
        self.file_types_entry.insert(0, self.config.get('FileTypes', 'types'))
        self.file_types_entry.grid(row=0, column=1, padx=5, pady=5)

    def create_extraction_settings(self, parent: tk.Toplevel):
        """
        创建提取设置部分的控件

        :param parent: 父窗口
        :return: None
        """
        frame = ttk.LabelFrame(parent, text="提取设置")
        frame.pack(padx=10, pady=5, fill=tk.X)

        ttk.Label(frame, text="最大文件大小 (字节):").grid(row=0, column=0, padx=5, pady=5)
        self.max_file_size_entry = ttk.Entry(frame)
        self.max_file_size_entry.insert(0, self.config.get('Extraction', 'max_file_size'))
        self.max_file_size_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="文件编码:").grid(row=1, column=0, padx=5, pady=5)
        self.encoding_entry = ttk.Entry(frame)
        self.encoding_entry.insert(0, self.config.get('Extraction', 'encoding'))
        self.encoding_entry.grid(row=1, column=1, padx=5, pady=5)

    def create_output_settings(self, parent: tk.Toplevel):
        """
        创建输出设置部分的控件

        :param parent: 父窗口
        :return: None
        """
        frame = ttk.LabelFrame(parent, text="出设置")
        frame.pack(padx=10, pady=5, fill=tk.X)

        ttk.Label(frame, text="结构文件名:").grid(row=0, column=0, padx=5, pady=5)
        self.structure_file_entry = ttk.Entry(frame)
        self.structure_file_entry.insert(0, self.config.get('Output', 'structure_file'))
        self.structure_file_entry.grid(row=0, column=1, padx=5, pady=5)

    def create_structure_discovery_settings(self, parent: tk.Toplevel):
        """
        创建文件结构发现设置部分的控件

        :param parent: 父窗口
        :return: None
        """
        frame = ttk.LabelFrame(parent, text="文件结构发现设置")
        frame.pack(padx=10, pady=5, fill=tk.X)

        ttk.Label(frame, text="特殊字符 (用逗号分隔):").grid(row=0, column=0, padx=5, pady=5)
        self.special_chars_entry = ttk.Entry(frame, width=50)
        default_chars = "├, │, └, ─"
        current_chars = self.config.get('StructureDiscovery', 'special_chars', fallback=default_chars)
        self.special_chars_entry.insert(0, current_chars)
        self.special_chars_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="(例如: ├, │, └, ─)").grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        ttk.Label(frame, text="注意: 程序会识别至少三行或更多行以这些符开头，且最后一行以 └ 开头的结构").grid(row=2, column=0, columnspan=2, padx=5, pady=2)
    
    def create_code_block_detection_settings(self, parent: tk.Toplevel):
        """
        创建代码块检测设置部分的控件

        :param parent: 父窗口
        :return: None
        """
        frame = ttk.LabelFrame(parent, text="代码块检测设置")
        frame.pack(padx=10, pady=5, fill=tk.X)

        ttk.Label(frame, text="代码块开始标志:").grid(row=0, column=0, padx=5, pady=5)
        self.start_marker_entry = ttk.Entry(frame)
        self.start_marker_entry.insert(0, self.config.get('code_block_detection', 'start_marker'))
        self.start_marker_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="代码块结束标志:").grid(row=1, column=0, padx=5, pady=5)
        self.end_marker_entry = ttk.Entry(frame)
        self.end_marker_entry.insert(0, self.config.get('code_block_detection', 'end_marker'))
        self.end_marker_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="标志需要出现的最小次数才视为有效代码块:").grid(row=2, column=0, padx=5, pady=5)
        self.min_occurrences_entry = ttk.Entry(frame)
        self.min_occurrences_entry.insert(0, self.config.get('code_block_detection', 'min_occurrences'))
        self.min_occurrences_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="代码块缩进级别（用于检测是否属于同一代码块）:").grid(row=3, column=0, padx=5, pady=5)
        self.indentation_level_entry = ttk.Entry(frame)
        self.indentation_level_entry.insert(0, self.config.get('code_block_detection', 'indentation_level'))
        self.indentation_level_entry.grid(row=3, column=1, padx=5, pady=5)

    def save_settings(self, settings_window: tk.Toplevel):
        """
        保存设置并更新配置

        :param settings_window: 设置窗口
        :return: None
        """
        # 更新配置
        self.config.set('FileTypes', 'types', self.file_types_entry.get())
        self.config.set('Extraction', 'max_file_size', self.max_file_size_entry.get())
        self.config.set('Extraction', 'encoding', self.encoding_entry.get())
        self.config.set('Output', 'structure_file', self.structure_file_entry.get())
        self.config.set('StructureDiscovery', 'special_chars', self.special_chars_entry.get())
        self.config.set('code_block_detection', 'start_marker', self.start_marker_entry.get())
        self.config.set('code_block_detection', 'end_marker', self.end_marker_entry.get())
        self.config.set('code_block_detection', 'min_occurrences', self.min_occurrences_entry.get())
        self.config.set('code_block_detection', 'indentation_level', self.indentation_level_entry.get())

        # 更新文件类型
        new_file_types = self.file_types_entry.get()
        self.config.set('FileTypes', 'types', new_file_types)
        
        # 创建一个新的配置字典
        new_config = {
            'FileTypes': {'types': new_file_types},
            'code_block_detection': {
                'start_marker': self.start_marker_entry.get(),
                'end_marker': self.end_marker_entry.get(),
                'min_occurrences': self.min_occurrences_entry.get(),
                'indentation_level': self.indentation_level_entry.get()
            }
        }
        
        # 更新 CodeBlockDetector 的配置
        self.code_block_detector.update_config(new_config)

        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

        # 更新 FileStructureExtractor 和 CodeBlockProcessor 的设置
        self.structure_extractor.update_config(self.config)
        self.code_processor.update_config(self.config)

        # 更新主界面的文件类型
        self.file_types.set(new_file_types)

        messagebox.showinfo("成功", "设置已保存")
        settings_window.destroy()

    def log_info(self, message: str, level: str = "info", from_logger: bool = False, important: bool = False) -> None:
        """
        记录信息到日志窗口

        :param message: str, 要记录的信息
        :param level: str, 日志级别，默认为 "info"
        :param from_logger: bool, 是否来自logger的调用，用于防止循环调用
        :param important: bool, 是否为重要消息
        :return: None
        """
        # 只显示消息本身，不包含时间和文件名
        log_entry = f"{message}\n"
        
        # 记录到GUI日志窗口
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()
        
        # 根据日志级别设置不同的颜色
        if level == "error":
            self.log_text.tag_add("error", f"end-{len(log_entry)}c", "end-1c")
            self.log_text.tag_config("error", foreground="red")
        elif level == "warning":
            self.log_text.tag_add("warning", f"end-{len(log_entry)}c", "end-1c")
            self.log_text.tag_config("warning", foreground="orange")
        elif important:
            self.log_text.tag_add("important", f"end-{len(log_entry)}c", "end-1c")
            self.log_text.tag_config("important", foreground="blue")

        # 记录到日志文件，但只有在不是来自logger的调用时才执行
        if not from_logger:
            caller = inspect.currentframe().f_back
            func_name = caller.f_code.co_name
            file_name = os.path.basename(caller.f_code.co_filename)
            log_message = f"[{file_name}:{func_name}] {message}"

            if level == "error":
                self.logger.error(log_message)
            elif level == "warning":
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)


    def display_code_block(self, file_path: str, lang: str, code: str):
        """
        在GUI中显示代码块预览

        :param file_path: 代码块所在文件路径
        :param lang: 代码言
        :param code: 代码内容
        :return: None
        """
        preview_lines = code.split('\n')[:10]
        preview = '\n'.join(preview_lines)
        self.log_info(f"\n代码块 ({lang}) 来自文件: {file_path}\n{preview}\n...")
        if len(code.split('\n')) > 10:
            self.log_info("... (更多行被省略)")
        self.log_info("-"*50)

    def log_general(self, message: str, level: str = "info"):
        """
        记录一般日志信息

        :param message: 日志消息
        :param level: 日志级别，默认为 "info"
        :return: None
        """
        self.log_info(message, level)

    def log_important(self, message: str, level: str = "info"):
        """
        记录重要日志信息

        :param message: 日志消息
        :param level: 日志级别，默认为 "info"
        :return: None
        """
        self.log_info(message, level)

    def exit_program(self):
        """
        退出程序

        :return: None
        """
        if self.is_running:
            if messagebox.askyesno("确认", "程序正在执行中，确定要退出吗？"):
                self.is_running = False
                self.master.after(100, self.check_and_exit)
        else:
            self.master.quit()

    def check_and_exit(self):
        """
        检查程序是否还在运行，如果不在运行则退出

        :return: None
        """
        if not self.is_running:
            self.master.quit()
        else:
            self.master.after(100, self.check_and_exit)

    def update_progress(self, value: int):
        """
        更新进度条

        :param value: 进度值（0-100）
        :return: None
        """
        try:
            self.progress['value'] = int(value)
            self.master.update_idletasks()
        except Exception as e:
            self.log_info(f"更新进度条时出错: {str(e)}", "error")

    def display_statistics(self, total_files: int, processed_files: int, code_block_count: int):
        """
        显示处理统计信息

        :param total_files: 总文件数
        :param processed_files: 已处理文件数
        :param code_block_count: 提取的代码块数
        :return: None
        """
        stats = (f"\n统计信息:\n"
                 f"总文件数: {total_files}\n"
                 f"处理的文件数: {processed_files}\n"
                 f"提取的代码块数: {code_block_count}")
        self.log_info(stats)

def load_settings() -> Dict[str, Any]:
    """
    加载配置文件

    :return: 配置信息字典
    """
    # 实现加载配置的逻辑
    pass

if __name__ == "__main__":
    root = tk.Tk()
    config = load_settings()
    app = AutoSaveCodeGUI(root, config)
    root.mainloop()