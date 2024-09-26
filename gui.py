import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from file_processor import FileProcessor
import os
import sys

class CodeExtractorGUI:
    def __init__(self, master):
        self.master = master
        self.file_processor = FileProcessor()
        master.title("代码提取器")
        master.geometry("1200x800")
        self.create_widgets()
        self.is_running = False

    def create_widgets(self):
        # 输入目录
        tk.Label(self.master, text="输入目录:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_dir = tk.StringVar(value=os.getcwd())
        tk.Entry(self.master, textvariable=self.input_dir, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.master, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        # 输出目录
        tk.Label(self.master, text="输出目录:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "code"))
        tk.Entry(self.master, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.master, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # 文件类型
        tk.Label(self.master, text="文件类型 (用逗号分隔):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.file_types = tk.StringVar(value=".md")
        tk.Entry(self.master, textvariable=self.file_types, width=50).grid(row=2, column=1, padx=5, pady=5)

        # 执行按钮
        tk.Button(self.master, text="执行", command=self.execute).grid(row=3, column=0, columnspan=3, pady=10)

        # 普通信息显示区域
        tk.Label(self.master, text="普通信息:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.general_info = tk.Text(self.master, wrap="word", height=10)
        self.general_info.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.general_info.tag_configure("debug", foreground="gray")
        self.general_info.tag_configure("info", foreground="black")
        self.general_info.tag_configure("warning", foreground="orange")
        self.general_info.tag_configure("error", foreground="red")

        # 修改重要信息显示区域
        tk.Label(self.master, text="重要信息:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.important_info = tk.Text(self.master, wrap="word", height=10)
        self.important_info.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.important_info.tag_configure("info", foreground="blue")
        self.important_info.tag_configure("warning", foreground="orange")
        self.important_info.tag_configure("error", foreground="red")

        # 进度条
        self.progress = ttk.Progressbar(self.master, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # 退出按钮
        tk.Button(self.master, text="退出", command=self.quit_application).grid(row=9, column=0, columnspan=3, pady=10)

        # 配置行和列的权重，使得文本框可以随窗口大小调整
        self.master.grid_rowconfigure(5, weight=1)
        self.master.grid_rowconfigure(7, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    def browse_input(self):
        initial_dir = self.input_dir.get() or os.getcwd()
        directory = filedialog.askdirectory(initialdir=initial_dir)
        if directory:
            self.input_dir.set(self.normalize_path(directory))
            self.log_general(f"已选择输入目录: {directory}", "debug")

    def browse_output(self):
        initial_dir = self.output_dir.get() or os.path.join(os.getcwd(), "code")
        directory = filedialog.askdirectory(initialdir=initial_dir)
        if directory:
            self.output_dir.set(self.normalize_path(directory))
            self.log_general(f"已选择输出目录: {directory}", "debug")

    def normalize_path(self, path):
        # 统一路径分隔符
        return os.path.normpath(path)

    def execute(self):
        self.is_running = True
        try:
            input_dir = self.input_dir.get() or os.getcwd()
            output_dir = self.output_dir.get() or os.path.join(os.getcwd(), "code")
            selected_types = [t.strip() for t in self.file_types.get().split(',')]
            self.file_processor.process_files(input_dir, output_dir, selected_types, self)
        except Exception as e:
            self.log_important(f"执行过程中出错: {str(e)}", "error")
        finally:
            self.is_running = False

    def quit_application(self):
        if self.is_running:
            if messagebox.askyesno("确认退出", "正在执行中，确定要退出吗？"):
                self.is_running = False
                self.log_general("操作被用户中断", "info")
        else:
            self.master.quit()

    def log_general(self, message, level="info"):
        self.general_info.insert(tk.END, message + "\n", level)
        self.general_info.see(tk.END)
        self.master.update_idletasks()

    def log_important(self, message, level="info"):
        self.important_info.insert(tk.END, message + "\n", level)
        self.important_info.see(tk.END)
        self.master.update_idletasks()