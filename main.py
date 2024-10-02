import tkinter as tk
import configparser
import os
from gui import AutoSaveCodeGUI
from logging_utils import get_logger

def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists('settings.ini'):
        config.read('settings.ini')
    else:
        create_default_settings(config)
    
    # 确保 'code_block_detection' 部分存在
    if 'code_block_detection' not in config:
        config['code_block_detection'] = {
            'start_marker': '```',
            'end_marker': '```',
            'min_occurrences': '2',
            'indentation_level': '4'
        }
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
    
    return config

def create_default_settings(config):
    config['Symbols'] = {
        'directory': '/',
        'file': ''
    }
    config['FileTypes'] = {
        'types': '.py, .js, .html, .css, .md'
    }
    config['Extraction'] = {
        'max_file_size': '10485760',
        'encoding': 'utf-8'
    }
    config['Output'] = {
        'structure_file': 'project_structure.md'
    }
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    get_logger()  # 初始化日志系统
    root = tk.Tk()
    config = load_settings()
    app = AutoSaveCodeGUI(root, config)
    root.mainloop()