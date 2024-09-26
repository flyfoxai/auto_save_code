import os

def create_unique_output_dir(base_dir):
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

def normalize_path(path):
    return os.path.normpath(path)

def is_valid_path(path):
    try:
        if len(path) > 255:
            return False
        os.path.normpath(path)
        return True
    except:
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
    return comment_syntax.get(file_extension.lower(), '#')