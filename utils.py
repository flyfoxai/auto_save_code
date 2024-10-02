import os
from logging_utils import log_info, log_warning, log_error, log_debug

def create_unique_output_dir(base_dir):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        log_info(f"创建新目录: {base_dir}")
        return base_dir

    index = 1
    while True:
        new_dir = f"{base_dir}_{index}"
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            log_info(f"创建新目录: {new_dir}")
            return new_dir
        index += 1

def normalize_path(path):
    normalized_path = os.path.normpath(path)
    log_debug(f"路径标准化: {path} -> {normalized_path}")
    return normalized_path

def is_valid_path(path):
    try:
        if len(path) > 255:
            log_warning(f"路径长度超过255个字符: {path}")
            return False
        os.path.normpath(path)
        return True
    except:
        log_error(f"无效的路径: {path}")
        return False

def get_comment_syntax(file_extension):
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
    syntax = comment_syntax.get(file_extension.lower(), '#')
    log_debug(f"文件扩展名 {file_extension} 的注释语法: {syntax}")
    return syntax