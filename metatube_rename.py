#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metatube-rename-tool
根据文件名中的番号自动重命名文件
"""

import os
import re
import argparse
from pathlib import Path


def extract_code(filename):
    """
    从文件名中提取AV番号
    匹配常见格式如: ABC-123, abc123, ABC123, 123ABC 等
    优先选择带连字符的格式，因为这是最常见的番号格式
    对于带有序集编号的文件名（如ABC-123-1），只提取主番号部分
    """
    # 先移除文件扩展名
    base_name = os.path.splitext(filename)[0]
    
    # 处理特定的@符号格式，比如 domain@CODE 或 CODE@domain
    if '@' in base_name:
        parts = base_name.split('@')
        for part in parts:
            # 首先检查是否直接包含标准的带连字符格式
            std_match = re.search(r'([A-Za-z]{2,10})-(\d{1,6})', part)
            if std_match:
                alpha_part = std_match.group(1).lower()
                if alpha_part not in ['start', 'end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test']:
                    return f"{std_match.group(1).upper()}-{std_match.group(2)}"
            
            # 尝试从@分割后的部分直接提取番号
            clean_part = re.sub(r'[^A-Za-z0-9]', '', part)
            # 检查是否符合基本的番号格式：字母+数字
            if re.match(r'^[A-Za-z]{2,10}[0-9]{1,6}$', clean_part, re.IGNORECASE):
                return clean_part.upper()
    
    # 定义不同优先级的模式
    # 优先级1: 带连字符的标准格式，可能带有分集编号 (例如 ABC-123 或 ABC-123-1)
    standard_pattern = r'([A-Za-z]{2,10})-(\d{1,6})(?:-\d+)?'
    standard_match = re.search(standard_pattern, base_name)
    if standard_match:
        # 检查是否是URL或域名的一部分
        if not standard_match.group(0).startswith('http') and not 'www' in standard_match.group(0):
            # 检查是否是常见的非番号前缀
            alpha_part = standard_match.group(1).lower()
            if alpha_part not in ['start', 'end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
                # 只返回主番号部分，忽略分集编号
                return f"{standard_match.group(1).upper()}-{standard_match.group(2)}"
    
    # 优先级2: 无分隔符格式 (例如 ABC123)
    alpha_num_pattern = r'([A-Za-z]{2,10})(\d{1,6})'
    alpha_num_match = re.search(alpha_num_pattern, base_name)
    if alpha_num_match:
        # 检查是否是URL或域名的一部分
        match_context = base_name[max(0, alpha_num_match.start()-5):alpha_num_match.end()+5].lower()
        if 'http' not in match_context and 'www' not in match_context and '.com' not in match_context:
            # 增强前缀过滤
            alpha_part = alpha_num_match.group(1).lower()
            if alpha_part not in ['start', 'end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
                return f"{alpha_num_match.group(1).upper()}{alpha_num_match.group(2)}"
    
    # 优先级3: 数字在前的格式 (例如 123ABC)，但排除明显不是番号的情况
    num_alpha_pattern = r'^(\d{1,6})([A-Za-z]{2,10})'
    num_alpha_match = re.search(num_alpha_pattern, base_name)
    if num_alpha_match:
        # 数字在前的情况通常不是标准番号格式，只有在特定情况下才识别
        # 例如 "123ABC" 可能是番号，但 "1start" 不是
        # 检查是否符合典型的番号格式特征
        alpha_part = num_alpha_match.group(2)
        # 增强前缀过滤，排除更多非番号前缀
        if len(alpha_part) >= 2 and len(alpha_part) <= 10 and \
           alpha_part.lower() not in ['start', 'end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
            return f"{num_alpha_match.group(2).upper()}{num_alpha_match.group(1)}"
    
    # 优先级4: 尝试从文件名中提取所有可能的番号格式，并选择最合适的
    # 这是最后的尝试，用于处理复杂或不规范的文件名
    all_matches = []
    
    # 常见的非番号字符串模式
    invalid_patterns = [
        r'^[0-9]+start',  # 以数字开头后跟start的模式
        r'^start[0-9]+',  # 以start开头后跟数字的模式
    ]
    
    # 查找所有可能的番号格式
    for pattern in [standard_pattern, alpha_num_pattern]:
        for match in re.finditer(pattern, base_name):
            # 检查是否是无效模式
            is_invalid = False
            for invalid_pattern in invalid_patterns:
                if re.search(invalid_pattern, match.group(0).lower()):
                    is_invalid = True
                    break
            if is_invalid:
                continue
                
            # 获取完整匹配
            full_match = match.group(0)
            
            # 检查是否是URL或域名的一部分
            context = base_name[max(0, match.start()-10):match.end()+10].lower()
            if any(keyword in context for keyword in ['http', 'https', 'www', '.com', '.net', '.org']):
                continue
            
            # 计算匹配的可能性评分
            score = 0
            if '-' in full_match:
                score += 10  # 包含连字符的额外加分
                # 标准格式 (字母-数字)
                parts = match.groups()
                if len(parts) >= 2 and parts[0].isalpha() and parts[1].isdigit():
                    alpha_part = parts[0].lower()
                    # 检查是否是常见的非番号前缀
                    if alpha_part not in ['start', 'end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
                        if 2 <= len(parts[0]) <= 10 and 1 <= len(parts[1]) <= 6:
                            score += 20
                            all_matches.append((score, f"{parts[0]}-{parts[1]}"))  # 只保留主番号部分
            elif full_match.isalnum() and not full_match.isdigit() and not full_match.isalpha():
                # 无分隔符格式
                parts = match.groups()
                if len(parts) >= 2:
                    alpha_part = parts[0] if not parts[0].isdigit() else parts[1]
                    num_part = parts[1] if not parts[0].isdigit() else parts[0]
                    # 检查是否是常见的非番号前缀
                    if alpha_part.lower() not in ['start', 'end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
                        if 2 <= len(alpha_part) <= 10 and 1 <= len(num_part) <= 6:
                            score += 15
                            all_matches.append((score, full_match))
    
    # 如果有多个匹配，选择得分最高的
    if all_matches:
        # 按分数排序
        all_matches.sort(key=lambda x: x[0], reverse=True)
        best_match = all_matches[0][1]
        return best_match.upper()
    
    return None


def rename_files(directory, dry_run=False, recursive=False):
    """
    重命名目录中的文件
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        print(f"错误: {directory} 不是有效的目录")
        return
    
    # 收集需要处理的文件
    files_to_process = []
    if recursive:
        for root, _, files in os.walk(dir_path):
            for file in files:
                files_to_process.append(Path(root) / file)
    else:
        files_to_process = [f for f in dir_path.iterdir() if f.is_file()]
    
    renamed_count = 0
    failed_count = 0
    
    for file_path in files_to_process:
        original_name = file_path.name
        code = extract_code(original_name)
        
        if code:
            # 保留原始文件扩展名
            extension = file_path.suffix
            
            # 检查是否有分集信息
            episode_match = re.search(r'-\d+-([0-9]+)(?=\.|$)', original_name)
            episode_num = None
            if episode_match:
                episode_num = episode_match.group(1)
            
            # 新文件名
            if episode_num:
                new_name = f"{code}-cd{episode_num}{extension}"
            else:
                new_name = f"{code}{extension}"
            
            new_path = file_path.parent / new_name
            
            # 避免覆盖现有文件
            counter = 1
            while new_path.exists() and new_path != file_path:
                if episode_num:
                    new_name = f"{code}-cd{episode_num}_{counter}{extension}"
                else:
                    new_name = f"{code}_{counter}{extension}"
                new_path = file_path.parent / new_name
                counter += 1
            
            # 如果文件名已经正确或者是同一个文件，则跳过
            if new_path == file_path:
                print(f"跳过: {original_name} (文件名已经符合规范)")
                continue
            
            # 执行重命名或模拟重命名
            if dry_run:
                print(f"将重命名: {original_name} -> {new_name}")
            else:
                try:
                    file_path.rename(new_path)
                    print(f"重命名: {original_name} -> {new_name}")
                    renamed_count += 1
                except Exception as e:
                    print(f"重命名失败: {original_name} -> {new_name}。错误: {e}")
                    failed_count += 1
        else:
            print(f"跳过: {original_name} (无法提取番号)")
            failed_count += 1
    
    print(f"\n处理完成!")
    print(f"成功重命名: {renamed_count}")
    print(f"失败/跳过: {failed_count}")


def main():
    """
    主函数，解析命令行参数
    """
    parser = argparse.ArgumentParser(description='metatube-rename-tool')
    parser.add_argument('directory', nargs='?', default='.', help='要处理的目录路径，默认为当前目录')
    parser.add_argument('-d', '--dry-run', action='store_true', help='仅显示将要执行的重命名操作，不实际执行')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    args = parser.parse_args()
    
    rename_files(args.directory, args.dry_run, args.recursive)


if __name__ == '__main__':
    main()