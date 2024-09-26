import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import traceback

class CodeExtractorGUI:
    def __init__(self, master):
        self.master = master
        master.title("代码提取器")
        master.geometry("1200x800")  # 增加窗口大小以容纳更多信息

        self.create_widgets()
        self.current_line = 0
        self.lines = []
        self.code_blocks = []

    def create_widgets(self):
        # 创建并布局GUI组件
        
        # 输入目录选择
        tk.Label(self.master, text="输入目录:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.input_dir = tk.StringVar(value=os.getcwd())
        tk.Entry(self.master, textvariable=self.input_dir, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.master, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        # 输出目录选择
        tk.Label(self.master, text="输出目录:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), 'code'))
        tk.Entry(self.master, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.master, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # 文件类型选择
        tk.Label(self.master, text="文件类型:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.file_types = tk.StringVar(value=".md")
        tk.Entry(self.master, textvariable=self.file_types, width=50).grid(row=2, column=1, padx=5, pady=5)
        tk.Label(self.master, text="用逗号分隔多个类型").grid(row=2, column=2, padx=5, pady=5)

        # 执行和退出按钮
        button_frame = tk.Frame(self.master)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        tk.Button(button_frame, text="执行", command=self.execute).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="退出", command=self.master.quit).pack(side=tk.LEFT, padx=5)

        # 创建两个文本框来显示不同类型的信息
        tk.Label(self.master, text="普通信息:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.general_info = tk.Text(self.master, wrap="word", height=15)
        self.general_info.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.general_info.tag_configure("info", foreground="#006400")  # 深绿色
        self.general_info.tag_configure("debug", foreground="#228B22")  # 浅绿色

        tk.Label(self.master, text="重要信息:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.important_info = tk.Text(self.master, wrap="word", height=10)
        self.important_info.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.important_info.tag_configure("warning", foreground="#FF4500")  # 浅红色
        self.important_info.tag_configure("error", foreground="#8B0000")  # 深红色

        # 进度条
        self.progress = ttk.Progressbar(self.master, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # 添加调试信息显示区域
        tk.Label(self.master, text="调试信息:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.debug_info = tk.Text(self.master, wrap="word", height=15)
        self.debug_info.grid(row=10, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # 添加下一步按钮
        self.next_step_button = tk.Button(self.master, text="下一步", command=self.next_step)
        self.next_step_button.grid(row=11, column=0, columnspan=3, pady=10)
        self.next_step_button.config(state=tk.DISABLED)

        # 配置行和列的权重，使得文本框可以随窗口大小调整
        self.master.grid_rowconfigure(5, weight=1)
        self.master.grid_rowconfigure(7, weight=1)
        self.master.grid_rowconfigure(10, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

    def log_general(self, message, level="info"):
        """记录普通信息到普通信息文本框"""
        self.general_info.insert(tk.END, message + "\n", level)
        self.general_info.see(tk.END)
        self.master.update_idletasks()

    def log_important(self, message, level="warning"):
        """记录重要信息到重要信息文本框"""
        self.important_info.insert(tk.END, message + "\n", level)
        self.important_info.see(tk.END)
        self.master.update_idletasks()

    def log_debug(self, message):
        """记录调试信息到调试信息文本框"""
        self.debug_info.insert(tk.END, message + "\n")
        self.debug_info.see(tk.END)
        self.master.update_idletasks()

    def browse_input(self):
        """打开文件对话框选择输入目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir.set(directory)
            self.log_general(f"已选择输入目录: {directory}", "debug")

    def browse_output(self):
        """打开文件对话框选择输出目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
            self.log_general(f"已选择输出目录: {directory}", "debug")

    def extract_code_blocks(self, content):
        """从文件内容中提取代码块"""
        self.log_general("开始提取代码块...", "debug")
        self.code_blocks = []
        
        # 统一换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 分割内容为行
        self.lines = content.split('\n')
        self.current_line = 0
        
        # 启用下一步按钮
        self.next_step_button.config(state=tk.NORMAL)
        
        # 清空调试信息
        self.debug_info.delete('1.0', tk.END)
        
        self.log_debug("准备开始逐步提取代码块")
        return self.code_blocks

    def next_step(self):
        """执行下一步代码块提取"""
        if self.current_line < len(self.lines):
            self.extract_code_block_step()
        else:
            self.log_debug("代码块提取完成")
            self.next_step_button.config(state=tk.DISABLED)

    def extract_code_block_step(self):
        """单步执行代码块提取"""
        line = self.lines[self.current_line]
        self.log_debug(f"当前行 ({self.current_line + 1}/{len(self.lines)}): {line}")

        # 使用正则表达式匹配文件路径格式
        file_path_pattern = r'^##\s+(.*?/.*?\.[a-zA-Z]{1,3})$'
        match = re.match(file_path_pattern, line)

        if match:
            self.log_debug("发现可能的文件路径（二级标题）")
            potential_path = match.group(1).strip()
            self.log_debug(f"提取的文件路径: {potential_path}")
            self.current_line += 1
            self.find_code_block_start(potential_path)
        else:
            self.current_line += 1
            self.log_debug("不是文件路径，继续下一行")

    def find_code_block_start(self, potential_path):
        """查找代码块开始并解析信息"""
        while self.current_line < len(self.lines) and not self.lines[self.current_line].startswith('```'):
            self.current_line += 1
            self.log_debug(f"跳过行: {self.lines[self.current_line-1]}")

        if self.current_line < len(self.lines):
            code_start = self.lines[self.current_line]
            self.log_debug(f"发现代码块开始: {code_start}")
            
            # 解析语言
            lang = code_start.strip('`').strip()
            self.log_debug(f"代码语言: {lang}")

            # 查找文件路径
            file_path = self.find_file_path()
            
            if file_path:
                self.current_line += 1  # 移动到代码内容开始
                self.extract_code_content(file_path, lang)
            else:
                self.log_debug("未找到有效的文件路径")
                self.current_line += 1
        else:
            self.log_debug("未找到代码块开始标记")

    def find_file_path(self):
        """在代码块开始行之前查找文件路径"""
        for i in range(1, 4):  # 检查前1-3行
            if self.current_line - i >= 0:
                line = self.lines[self.current_line - i]
                file_path_pattern = r'^##\s+(.*?/.*?\.[a-zA-Z]{1,3})$'
                match = re.match(file_path_pattern, line)
                if match:
                    file_path = match.group(1).strip()
                    self.log_debug(f"在第{i}行前找到文件路径: {file_path}")
                    return file_path
        self.log_debug("在前3行中未找到文件路径")
        return None

    def extract_code_content(self, file_path, lang):
        """提取代码内容"""
        code_lines = []
        while self.current_line < len(self.lines) and not self.lines[self.current_line].startswith('```'):
            code_lines.append(self.lines[self.current_line])
            self.current_line += 1
            self.log_debug(f"提取代码行: {code_lines[-1]}")

        if self.current_line < len(self.lines) and self.lines[self.current_line] == '```':
            code = '\n'.join(code_lines)
            if file_path:
                self.code_blocks.append((file_path, lang, code))
                self.log_debug(f"成功提取代码块，文件路径: {file_path}, 语言: {lang}")
            else:
                self.log_debug("发现没有明确路径的代码块，已舍弃")
        else:
            self.log_debug("发现未正确结束的代码块，已舍弃")

    def execute(self):
        """执行主要的代码提取和处理逻辑"""
        # 清空之前的日志信息
        self.general_info.delete('1.0', tk.END)
        self.important_info.delete('1.0', tk.END)
        self.log_general("开始执行...", "info")
        self.progress['value'] = 0
        
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        self.log_general(f"输入目录: {input_dir}", "debug")
        self.log_general(f"输出目录: {output_dir}", "debug")
        
        # 检查输入目录是否存在
        if not os.path.exists(input_dir):
            self.log_important(f"错误：输入目录不存在！", "error")
            messagebox.showerror("错误", "输入目录不存在！")
            return

        # 检查并创建唯一的输出目录
        output_dir = self.create_unique_output_dir(output_dir)
        self.log_general(f"最终输出目录: {output_dir}", "info")

        # 获取用户选择的文件类型
        selected_types = [t.strip() for t in self.file_types.get().split(',')]
        self.log_general(f"选择的文件类型: {selected_types}", "debug")

        try:
            # 处理文件并获取统计信息
            file_count, structure_count, code_count = self.process_files(input_dir, output_dir, selected_types)
            
            # 显示结果
            result_message = f"处理完成\n共处理 {file_count} 个文件\n提取 {structure_count} 个目录结构\n{code_count} 段代码"
            self.log_general(result_message, "info")
            messagebox.showinfo("处理完成", result_message)
        except Exception as e:
            error_message = f"处理过程中出现错误：\n{str(e)}\n\n{traceback.format_exc()}"
            self.log_important(error_message, "error")
            messagebox.showerror("错误", error_message)
        finally:
            # 确保进度条显示100%完成
            self.progress['value'] = 100

    def create_unique_output_dir(self, base_dir):
        """创建一个唯一的输出目录，避免覆盖现有目录"""
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            return base_dir

        index = 1
        while True:
            new_dir = f"{base_dir}_{index}"
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
                return new_dir
            index += 1

    def extract_project_structure(self, content, filename):
        """从文件内容中提取项目结构"""
        self.log_general(f"开始提取 {filename} 的项目结构...", "debug")
        
        structure_lines = self.find_structure_lines(content, filename)
        if not structure_lines:
            self.log_important(f"在文件 {filename} 中未找到有效的文档结构", "warning")
            return None
        
        self.log_important(f"在文件 {filename} 中提取到的目录结构:\n{chr(10).join(structure_lines)}", "warning")
        return structure_lines

    def find_structure_lines(self, content, filename):
        """在文件内容中查找并提取结构行"""
        lines = content.split('\n')

        structure_start = -1
        structure_end = -1
        structure_pattern = re.compile(r'^[│├└]')
        folder_pattern = re.compile(r'^(\s*)(\S+)/$')

        # 首先查找有效的结构标记
        for i in range(len(lines) - 2):
            if all(structure_pattern.match(lines[j]) for j in range(i, i+3)):
                structure_start = i
                self.log_general(f"在文件 {filename} 中找到文档结构标记: 第 {i+1} 行", "debug")
                break
        
        if structure_start == -1:
            self.log_important(f"在文件 {filename} 中未找到符合条件的文档结构标记", "warning")
            return None
        
        # 向上查找文件夹名称
        for i in range(structure_start - 1, -1, -1):
            if folder_pattern.match(lines[i]):
                structure_start = i
                self.log_general(f"在文件 {filename} 中找到顶级文件夹: 第 {i+1} 行", "debug")
                break
        else:
            self.log_important(f"在文件 {filename} 中未找到有效的顶级文件夹", "warning")
            return None
        
        # 向下查找结构结束位置
        for i in range(structure_start, len(lines)):
            if lines[i].startswith('└'):
                structure_end = i
                self.log_general(f"在文件 {filename} 中找到文档结构结束位置: 第 {i+1} 行", "debug")
                break
        
        if structure_end == -1:
            self.log_important(f"在文件 {filename} 中未找到文档结构结束标", "warning")
            return None
        
        # 提取结构内容
        structure_lines = lines[structure_start:structure_end+1]
        
        # 验证结构的有效性
        if not self.validate_structure(structure_lines, filename):
            self.log_important(f"在文件 {filename} 中提取的结构不符合要求", "warning")
            return None
        
        return structure_lines

    def validate_structure(self, lines, filename):
        """验证提取的结构是否有效"""
        if len(lines) < 3:
            self.log_important(f"在文件 {filename} 中的结构行数少于3行", "warning")
            return False
        
        # 检查第一行是否是一个有效的目录名（不以特殊字符开头，以斜杠结尾）
        if lines[0].startswith(('│', '├', '└')) or not lines[0].strip().endswith('/'):
            self.log_important(f"在文件 {filename} 中的结构第一行不是有效的目录名: {lines[0]}", "warning")
            return False
        
        # 检查最后一行是否以 '└' 开头
        if not lines[-1].startswith('└'):
            self.log_important(f"在文件 {filename} 中的结构最后一行不是以'└'开头: {lines[-1]}", "warning")
            return False
        
        # 检查中间行连续性和正确性
        for i in range(1, len(lines) - 1):
            if not lines[i].startswith(('│', '├')):
                self.log_important(f"在文件 {filename} 中的结构第 {i+1} 行不是以'│'或'├'开头: {lines[i]}", "warning")
                return False
            
            # 检查目录是否以斜杠结尾，文件是否不以斜杠结尾
            if '─' in lines[i]:
                item = lines[i].split('─')[-1].strip()
                if ('.' in item and item.endswith('/')) or ('.' not in item and not item.endswith('/')):
                    self.log_important(f"在文件 {filename} 中的结构第 {i+1} 行目录/文件格式不正确: {lines[i]}", "warning")
                    return False
        
        return True

    def create_project_structure(self, base_dir, structure):
        """根据提取的结构创建实际的录和文件"""
        self.log_general(f"开始创建项目结构在: {base_dir}", "info")
        current_path = base_dir
        path_stack = [current_path]
        created_files = set()
        
        for i, line in enumerate(structure):
            # 计算缩进级别
            indent_level = len(line) - len(line.lstrip('│ ├─└'))
            
            # 提取文件或目录名
            name = line.strip().split('─')[-1].strip() if '─' in line else line.strip()
            
            # 根据缩进调整当前路径
            while indent_level < len(path_stack) - 1:
                path_stack.pop()
            
            current_path = os.path.join(path_stack[-1], name)
            
            if name.endswith('/') or (i == 0 and '.' not in name):  # 目录或顶级文件夹
                if name.endswith('/'):
                    name = name[:-1]  # 移除尾的斜杠
                    current_path = current_path[:-1]  # 确保路径不以斜杠结尾
                if not os.path.exists(current_path):
                    os.makedirs(current_path, exist_ok=True)
                    self.log_general(f"创建目录: {current_path}", "info")
                path_stack.append(current_path)
            else:  # 文件
                if not os.path.exists(current_path):
                    open(current_path, 'a').close()  # 创建空文件
                    self.log_general(f"创建文件: {current_path}", "info")
                    created_files.add(current_path)
                else:
                    self.log_general(f"文件已存在，跳过创建: {current_path}", "info")
                    created_files.add(current_path)

        return created_files

    def normalize_path(self, path):
        """规范化路径，处理不同平台的路径分隔符"""
        return os.path.normpath(path)

    def is_valid_path(self, path):
        """检查路径是否有效"""
        try:
            # 检查路径长度
            if len(path) > 255:  # 大多数文件系统的最大路径长度
                return False
            # 检查路径是否包含非法字符
            os.path.normpath(path)
            return True
        except:
            return False

    def get_comment_syntax(self, file_extension):
        """根据文件扩展名返回相应的注释语法"""
        comment_syntax = {
            '.py': '#',
            '.js': '//',
            '.java': '//',
            '.c': '//',
            '.cpp': '//',
            '.html': '<!--',
            '.css': '/*',
            '.md': '[comment]: #',
            '.sh': '#',
            '.bat': 'REM',
            '.ps1': '#'
        }
        return comment_syntax.get(file_extension.lower(), '#')

    def process_files(self, input_dir, output_base_dir, selected_types):
        """处理输入目录中的所有文件"""
        self.log_general(f"开始处理文件夹: {input_dir}", "info")
        file_count = 0
        structure_count = 0
        code_count = 0
        total_files = sum(len(files) for _, _, files in os.walk(input_dir) 
                          if any(f.endswith(tuple(selected_types)) for f in files))
        self.log_general(f"文件夹中共有 {total_files} 个匹配的文件", "info")

        created_files = set()

        # 第一次遍历：处理目录结构
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if any(file.endswith(ext) for ext in selected_types):
                    file_count += 1
                    input_path = os.path.join(root, file)
                    self.log_general(f"正在处理第 {file_count}/{total_files} 个文件结构: {input_path}", "debug")
                    try:
                        with open(input_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        project_structure = self.extract_project_structure(content, file)
                        if project_structure:
                            structure_count += 1
                            created_files.update(self.create_project_structure(output_base_dir, project_structure))
                    except Exception as e:
                        self.log_important(f"处理文件结构时出错 {input_path}: {str(e)}", "error")
                    self.progress['value'] = (file_count / (total_files * 2)) * 100
                    self.master.update_idletasks()

        # 第二次遍历：处理代码块
        file_count = 0
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if any(file.endswith(ext) for ext in selected_types):
                    file_count += 1
                    input_path = os.path.join(root, file)
                    self.log_general(f"正在处理第 {file_count}/{total_files} 个文件代码: {input_path}", "debug")
                    try:
                        with open(input_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.extract_code_blocks(content)
                        
                        # 等待用户点击"下一步"按钮来处理下一个文件
                        self.master.wait_variable(self.next_step_button['state'])
                    except Exception as e:
                        self.log_important(f"处理文件代码时出错 {input_path}: {str(e)}", "error")
                    
                    self.progress['value'] = ((total_files + file_count) / (total_files * 2)) * 100
                    self.master.update_idletasks()

        return file_count, structure_count, code_count

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeExtractorGUI(root)
    root.mainloop()
    