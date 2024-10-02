import logging
import os
import inspect
from datetime import datetime
from typing import Optional

class CustomLogger:
    _instance = None

    @staticmethod
    def get_instance():
        """
        获取 CustomLogger 的单例实例
        """
        if CustomLogger._instance is None:
            CustomLogger()
        return CustomLogger._instance

    def __init__(self):
        """
        初始化 CustomLogger
        设置日志级别，创建文件处理器和格式化器
        """
        if CustomLogger._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            CustomLogger._instance = self

        # 创建logger对象
        self.logger = logging.getLogger('AutoSaveCode')
        self.logger.setLevel(logging.DEBUG)

        # 创建日志目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 创建文件处理器
        log_file = os.path.join(log_dir, f"auto_save_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 创建格式化器
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        # 将文件处理器添加到logger
        self.logger.addHandler(file_handler)
        
        # GUI对象，初始为None
        self.gui = None

    def find_caller(self):
        """
        查找真正的调用者
        """
        frame = inspect.currentframe()
        while frame:
            if frame.f_code.co_filename != __file__:
                return (
                    os.path.basename(frame.f_code.co_filename),
                    frame.f_code.co_name,
                    frame.f_lineno
                )
            frame = frame.f_back
        return ("unknown", "unknown", 0)

    def set_gui(self, gui):
        """
        设置GUI对象
        :param gui: GUI对象
        """
        self.gui = gui

    def log(self, message: str, level: str = "info", display_gui: bool = True, important: bool = False):
        """
        记录日志
        :param message: 日志消息
        :param level: 日志级别
        :param display_gui: 是否在GUI中显示
        :param important: 是否为重要消息
        """
        # 获取调用者的信息
        filename, func_name, lineno = self.find_caller()

        # 构造完整的日志消息，包含文件名等信息
        full_message = f"[{filename}:{func_name}:{lineno}] {message}"

        # 获取对应的日志函数
        log_func = getattr(self.logger, level.lower())
        # 记录日志到文件
        log_func(full_message)

        # 如果需要在GUI中显示，且GUI对象存在，且消息重要
        if display_gui and self.gui and important:
            # 对于GUI显示，我们只传递消息本身，不包含文件名等信息
            self.gui.log_info(message, level, from_logger=True)

    def debug(self, message: str, display_gui: bool = False, important: bool = False):
        """
        记录debug级别的日志
        """
        self.log(message, "debug", display_gui, important)

    def info(self, message: str, display_gui: bool = True, important: bool = False):
        """
        记录info级别的日志
        """
        self.log(message, "info", display_gui, important)

    def warning(self, message: str, display_gui: bool = True, important: bool = False):
        """
        记录warning级别的日志
        """
        self.log(message, "warning", display_gui, important)

    def error(self, message: str, display_gui: bool = True, important: bool = False):
        """
        记录error级别的日志
        """
        self.log(message, "error", display_gui, important)

def get_logger():
    """
    获取CustomLogger实例
    """
    return CustomLogger.get_instance()

def log_info(message: str, display_gui: bool = True, important: bool = False):
    """
    记录info级别的日志
    """
    get_logger().info(message, display_gui, important)

def log_warning(message: str, display_gui: bool = True, important: bool = False):
    """
    记录warning级别的日志
    """
    get_logger().warning(message, display_gui, important)

def log_error(message: str, display_gui: bool = True, important: bool = False):
    """
    记录error级别的日志
    """
    get_logger().error(message, display_gui, important)

def log_debug(message: str, display_gui: bool = False, important: bool = False):
    """
    记录debug级别的日志
    """
    get_logger().debug(message, display_gui, important)