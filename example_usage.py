#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
metatube-rename-tool 使用示例
"""

import os
import sys
import subprocess
import json

def create_sample_directory():
    """创建示例目录和文件"""
    # 创建示例目录
    sample_dir = "sample_files"
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
    
    # 创建示例文件
    sample_files = [
        "ABC-123-C-U.mp4",
        "DEF-456-U.avi",
        "GHI-789-C.mkv",
        "JKL-012.mp4",
        "MNO-345-sample.mp4",  # 这个应该被排除
        "PQR-678-preview.avi"  # 这个也应该被排除
    ]
    
    for filename in sample_files:
        filepath = os.path.join(sample_dir, filename)
        # 创建空文件
        with open(filepath, 'w') as f:
            f.write("")  # 创建空文件
    
    print(f"示例文件已创建在 {sample_dir} 目录中")
    return sample_dir

def create_sample_config():
    """创建示例配置文件"""
    config = {
        "naming_rules": {
            "code_format": "uppercase_with_hyphen",
            "separator": "-",
            "order": ["code", "markers", "episode", "resolution", "quality"],
            "episode_format": "cd{episode}"
        },
        "file_extensions": [".mp4", ".avi", ".mkv"],
        "exclude_patterns": ["sample", "preview"],
        "advanced_options": {
            "max_filename_length": 100,
            "conflict_resolution": "suffix"
        }
    }
    
    with open("example_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("示例配置文件 example_config.json 已创建")
    return "example_config.json"

def run_demo():
    """运行演示"""
    print("=== metatube-rename-tool 使用演示 ===\n")
    
    # 1. 创建示例文件
    print("1. 创建示例文件...")
    sample_dir = create_sample_directory()
    
    # 2. 创建示例配置文件
    print("2. 创建示例配置文件...")
    config_file = create_sample_config()
    
    # 3. 显示原始文件列表
    print("3. 原始文件列表:")
    for file in os.listdir(sample_dir):
        print(f"  {file}")
    print()
    
    # 4. 使用配置文件进行模拟运行
    print("4. 使用配置文件进行模拟运行...")
    try:
        result = subprocess.run([
            sys.executable, "metatube_rename.py", 
            "-d",  # 模拟运行
            "-c", config_file,  # 使用配置文件
            sample_dir
        ], capture_output=True, text=True, cwd=".")
        
        print("模拟运行输出:")
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
    except Exception as e:
        print(f"运行演示时出错: {e}")
    
    # 5. 清理示例文件
    print("5. 清理示例文件...")
    import shutil
    if os.path.exists(sample_dir):
        shutil.rmtree(sample_dir)
    if os.path.exists(config_file):
        os.remove(config_file)
    
    print("演示完成!")

if __name__ == "__main__":
    run_demo()