#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metatube-rename-tool 自定义规则测试脚本
测试自定义重命名规则的功能
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
import importlib.util
import sys

# 动态导入主模块
spec = importlib.util.spec_from_file_location("metatube_rename", "metatube_rename.py")
metatube_rename = importlib.util.module_from_spec(spec)
sys.modules["metatube_rename"] = metatube_rename
spec.loader.exec_module(metatube_rename)

# 从模块中导入所需的函数
normalize_filename = metatube_rename.normalize_filename
generate_config_template = metatube_rename.generate_config_template


class TestCustomRules(unittest.TestCase):
    """
    测试自定义重命名规则功能
    """
    
    def test_generate_config_template(self):
        """
        测试生成配置文件模板
        """
        template = generate_config_template()
        config = json.loads(template)
        
        # 检查必需的配置项
        self.assertIn("naming_rules", config)
        self.assertIn("file_extensions", config)
        self.assertIn("exclude_patterns", config)
        self.assertIn("custom_replacements", config)
        self.assertIn("advanced_options", config)
        
        # 检查命名规则配置项
        naming_rules = config["naming_rules"]
        self.assertIn("code_format", naming_rules)
        self.assertIn("markers", naming_rules)
        self.assertIn("separator", naming_rules)
        self.assertIn("order", naming_rules)
        self.assertIn("episode_format", naming_rules)
        self.assertIn("custom_rules", naming_rules)
        
        # 检查高级选项
        advanced_options = config["advanced_options"]
        self.assertIn("preserve_original_filename", advanced_options)
        self.assertIn("max_filename_length", advanced_options)
        self.assertIn("conflict_resolution", advanced_options)
    
    def test_normalize_filename_with_custom_rules(self):
        """
        测试使用自定义规则规范化文件名
        """
        # 默认规则
        result = normalize_filename("ABC-123-C-U.mp4")
        self.assertEqual(result, "ABC-123-C-U.mp4")
        
        # 自定义规则：改变分隔符
        custom_rules = {
            "naming_rules": {
                "separator": "_",
                "order": ["code", "markers", "episode", "resolution", "quality"]
            }
        }
        result = normalize_filename("ABC-123-C-U.mp4", custom_rules)
        self.assertEqual(result, "ABC-123_C_U.mp4")
        
        # 自定义规则：改变顺序
        custom_rules = {
            "naming_rules": {
                "order": ["markers", "code", "episode", "resolution", "quality"]
            }
        }
        result = normalize_filename("ABC-123-C-U.mp4", custom_rules)
        # 根据实现，除了code部分外的所有部分都会添加前缀分隔符
        # markers部分会变成"-C-U"，code部分保持为"ABC-123"，两者连接在一起
        self.assertEqual(result, "-C-UABC-123.mp4")
        
        # 自定义规则：改变番号格式
        custom_rules = {
            "naming_rules": {
                "code_format": "uppercase_no_hyphen"
            }
        }
        result = normalize_filename("ABC-123-C-U.mp4", custom_rules)
        self.assertEqual(result, "ABC123-C-U.mp4")
        
        # 自定义规则：改变分集格式
        custom_rules = {
            "naming_rules": {
                "episode_format": "part{episode}"
            }
        }
        result = normalize_filename("ABC-123-C-cd1.mp4", custom_rules)
        self.assertEqual(result, "ABC-123-C-part1.mp4")
    
    def test_advanced_options(self):
        """
        测试高级选项功能
        """
        # 测试保留原始文件名选项（此选项在normalize_filename中不直接体现，但在rename_files中使用）
        custom_rules = {
            "advanced_options": {
                "preserve_original_filename": True
            }
        }
        result = normalize_filename("ABC-123-C-U.mp4", custom_rules)
        self.assertEqual(result, "ABC-123-C-U.mp4")  # normalize_filename不受此选项影响


def main():
    """
    运行测试并显示详细结果
    """
    # 创建测试套件
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCustomRules))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果状态码
    exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()