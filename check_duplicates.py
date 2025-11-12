#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查测试用例中是否存在重复的文件名
"""

import re
import sys
from test_metatube_rename import TestAVRename

class TestChecker:
    def __init__(self):
        # 创建测试类实例来访问测试用例
        self.test_instance = TestAVRename()
        self.test_instance.setUp()  # 初始化测试数据
    
    def find_duplicate_test_cases(self):
        """
        查找重复的测试用例
        """
        all_filenames = []
        duplicates = []
        
        # 收集所有测试用例的文件名
        for category, cases in self.test_instance.test_cases.items():
            for filename, expected in cases:
                if filename in all_filenames:
                    # 找到重复
                    duplicates.append((category, filename))
                else:
                    all_filenames.append(filename)
        
        return duplicates
    
    def run_analysis(self):
        """
        运行分析并显示结果
        """
        duplicates = self.find_duplicate_test_cases()
        
        if duplicates:
            print(f"发现 {len(duplicates)} 个重复的测试用例：")
            for category, filename in duplicates:
                print(f"  - 分类 '{category}': '{filename}'")
            return True
        else:
            print("没有发现重复的测试用例。")
            return False

if __name__ == "__main__":
    checker = TestChecker()
    has_duplicates = checker.run_analysis()
    sys.exit(1 if has_duplicates else 0)