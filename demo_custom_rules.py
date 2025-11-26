#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自定义规则功能演示脚本
"""

import os
import json
from metatube_rename import normalize_filename, generate_config_template

def demo_custom_rules():
    """演示自定义规则功能"""
    print("=== 自定义规则功能演示 ===\n")
    
    # 示例文件名
    test_files = [
        "ABC-123-C-U.mp4",
        "DEF-456-U.avi",
        "GHI-789-C.mkv",
        "JKL-012.mp4"
    ]
    
    print("原始文件名:")
    for filename in test_files:
        print(f"  {filename}")
    print()
    
    # 1. 默认规则
    print("1. 默认规则重命名结果:")
    for filename in test_files:
        result = normalize_filename(filename)
        print(f"  {filename} -> {result}")
    print()
    
    # 2. 自定义规则：改变顺序
    print("2. 自定义规则 - 改变顺序 (markers, code, episode, resolution, quality):")
    custom_rules_order = {
        "naming_rules": {
            "order": ["markers", "code", "episode", "resolution", "quality"]
        }
    }
    for filename in test_files:
        result = normalize_filename(filename, custom_rules_order)
        print(f"  {filename} -> {result}")
    print()
    
    # 3. 自定义规则：改变分隔符
    print("3. 自定义规则 - 改变分隔符为 '_':")
    custom_rules_separator = {
        "naming_rules": {
            "separator": "_"
        }
    }
    for filename in test_files:
        result = normalize_filename(filename, custom_rules_separator)
        print(f"  {filename} -> {result}")
    print()
    
    # 4. 自定义规则：改变番号格式
    print("4. 自定义规则 - 番号格式改为小写无连字符:")
    custom_rules_format = {
        "naming_rules": {
            "code_format": "lowercase_no_hyphen"
        }
    }
    for filename in test_files:
        result = normalize_filename(filename, custom_rules_format)
        print(f"  {filename} -> {result}")
    print()
    
    # 5. 自定义规则：改变分集格式
    print("5. 自定义规则 - 分集格式改为 'part{episode}':")
    custom_rules_episode = {
        "naming_rules": {
            "episode_format": "part{episode}"
        }
    }
    # 使用带分集的文件名进行测试
    episode_files = ["ABC-123-C-U-cd1.mp4", "DEF-456-U-cd2.avi"]
    for filename in episode_files:
        result = normalize_filename(filename, custom_rules_episode)
        print(f"  {filename} -> {result}")
    print()
    
    # 6. 生成配置文件模板
    print("6. 生成配置文件模板:")
    config_template = generate_config_template()
    print(config_template)
    print()
    
    # 7. 保存配置文件示例
    print("7. 保存配置文件示例...")
    sample_config = {
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
    
    with open("demo_config.json", "w", encoding="utf-8") as f:
        json.dump(sample_config, f, indent=4, ensure_ascii=False)
    
    print("配置文件已保存为 demo_config.json")
    print()

if __name__ == "__main__":
    demo_custom_rules()