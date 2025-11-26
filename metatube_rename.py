#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metatube-rename-tool
根据文件名中的番号自动重命名文件，支持多种媒体文件命名规范
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import Optional, Tuple, List


def extract_code(filename: str) -> Optional[str]:
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
                if alpha_part not in ['end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test']:
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
            if alpha_part not in ['end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
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
            if alpha_part not in ['end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
                return f"{alpha_num_match.group(1).upper()}{alpha_num_match.group(2)}"
    
    # 优先级3: 数字在前的格式 (例如 123ABC)，但排除明显不是番号的情况
    num_alpha_pattern = r'^(\d{1,6})([A-Za-z]{2,10})'
    num_alpha_match = re.search(num_alpha_pattern, base_name)
    if num_alpha_match:
        # 数字在前的情况通常不是标准番号格式，只有在特定情况下才识别
        # 例如 "123ABC" 可能是番号
        # 检查是否符合典型的番号格式特征
        alpha_part = num_alpha_match.group(2)
        # 增强前缀过滤，排除更多非番号前缀
        if len(alpha_part) >= 2 and len(alpha_part) <= 10 and \
           alpha_part.lower() not in ['end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
            return f"{num_alpha_match.group(2).upper()}{num_alpha_match.group(1)}"
    
    # 优先级4: 尝试从文件名中提取所有可能的番号格式，并选择最合适的
    # 这是最后的尝试，用于处理复杂或不规范的文件名
    all_matches = []
    
    # 常见的非番号字符串模式
    invalid_patterns = [
        # 移除了对start开头的过滤
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
                    if alpha_part not in ['end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
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
                    if alpha_part.lower() not in ['end', 'part', 'vol', 'img', 'pic', 'file', 'doc', 'test', 'disk', 'disc']:
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


def extract_special_markers(filename: str) -> Tuple[List[str], Optional[str]]:
    """
    从文件名中提取特殊标记并进行标准化
    返回标准化后的标记列表和分集号
    """
    markers = []
    base_name = os.path.splitext(filename)[0].lower()
    
    # 定义需要标准化的标记映射
    # 键：需要标准化的标记，值：标准化后的标记
    standardize_map = {
        'ai': 'u',  # AI去码标准化为U标记
        'uncensored': 'u',  # uncensored标准化为U标记
        'uncen': 'u',  # uncen标准化为U标记
        'uc': 'u',  # uc标准化为U标记
        'ch': 'c',  # 中文字幕标准化为C标记
        'chs': 'c',  # 中文字幕标准化为C标记
        'cht': 'c',  # 中文字幕标准化为C标记
        'cn': 'c',  # 中文字幕标准化为C标记
        'sc': 'c',  # 简体中文标准化为C标记
        'tc': 'c',  # 繁体中文标准化为C标记
        '4k': '4K',  # 4K标记
        '1080p': '1080P',  # 1080P标记
        '720p': '720P',  # 720P标记
        'h265': 'H265',  # H265编码标记
        'h264': 'H264',  # H264编码标记
        'dvd': 'DVD',  # DVD标记
        'bluray': 'BluRay',  # 蓝光标记
        'web': 'WEB',  # 网络版标记
        'remux': 'REMUX',  # REMUX标记
    }
    
    # 先提取番号部分，避免将番号中的数字识别为分集号
    code = extract_code(filename)
    if code:
        # 从基础名称中移除番号部分，避免干扰
        # 处理带连字符和不带连字符的两种格式
        code_parts = code.split('-')
        if len(code_parts) == 2:
            # 带连字符的格式，如 ABC-123
            code_pattern = re.escape(code)
        else:
            # 不带连字符的格式，如 ABC123
            # 尝试将数字部分和字母部分分开
            match = re.match(r'([A-Za-z]+)(\d+)', code)
            if match:
                alpha_part, num_part = match.groups()
                # 创建一个模式，允许数字部分前有可选的连字符
                code_pattern = f"{re.escape(alpha_part)}[-]?{re.escape(num_part)}"
            else:
                code_pattern = re.escape(code)
        
        # 从base_name中移除番号部分
        temp_name = re.sub(code_pattern, '', base_name, flags=re.IGNORECASE)
    else:
        temp_name = base_name
    
    # 提取字幕标记，确保它是独立的标记，不是其他单词的一部分
    if re.search(r'[-_.]c(?:h)?(?=\.|$|[-_.])', temp_name):
        if 'C' not in markers:
            markers.append('C')
    
    # 提取多碟标记，确保它是独立的标记，不是其他单词的一部分
    episode_match = re.search(r'[-_.](?:cd)?(\d+)(?=\.|$|[-_.])', temp_name)
    episode_num = None
    if episode_match:
        # 确保不是番号中的数字部分
        episode_candidate = episode_match.group(1)
        # 检查是否是合理的分集编号（通常是1-99之间的数字）
        if episode_candidate.isdigit() and 1 <= int(episode_candidate) <= 99:
            episode_num = episode_candidate
    
    # 提取并标准化其他特殊标记
    special_matches = re.findall(r'[-_.]([a-z0-9]+)(?=\.|$|[-_.])', temp_name)
    
    for match in special_matches:
        # 跳过分集标记
        if match.startswith('cd') and match[2:].isdigit():
            continue
        # 检查是否是需要保留的标记
        if match == 'u':
            if 'U' not in markers:
                markers.append('U')
        elif match == 'c':
            if 'C' not in markers:
                markers.append('C')
        # 检查是否需要标准化
        elif match in standardize_map:
            standard_marker = standardize_map[match].upper()
            if standard_marker not in markers:
                markers.append(standard_marker)
        # 特殊处理 - 处理CH/CHS/CHT/CN等字幕标记
        elif match in ['ch', 'chs', 'cht', 'cn', 'sc', 'tc']:
            if 'C' not in markers:
                markers.append('C')
        # 特殊处理 - 处理分辨率标记
        elif match in ['4k', '1080p', '720p', 'h265', 'h264', 'dvd', 'bluray', 'web', 'remux']:
            standard_marker = standardize_map[match]
            if standard_marker not in markers:
                markers.append(standard_marker)
    
    return markers, episode_num


def extract_resolution_and_codec(filename: str) -> List[str]:
    """
    从文件名中提取分辨率和编码信息
    """
    resolution_and_codec = []
    base_name = os.path.splitext(filename)[0].lower()
    
    # 分辨率模式
    resolution_patterns = [
        r'4k',
        r'2160p',
        r'1080p',
        r'1080i',
        r'720p',
        r'720i',
        r'480p',
        r'480i'
    ]
    
    # 编码格式模式
    codec_patterns = [
        r'h264',
        r'h265',
        r'hevc',
        r'x264',
        r'x265',
        r'avc',
        r'hevc',
        r'av1'
    ]
    
    # 检查分辨率
    for pattern in resolution_patterns:
        if re.search(pattern, base_name, re.IGNORECASE):
            resolution_and_codec.append(pattern.upper())
            break  # 只取第一个匹配的分辨率
    
    # 检查编码格式
    for pattern in codec_patterns:
        if re.search(pattern, base_name, re.IGNORECASE):
            codec = pattern.upper()
            # 特殊处理
            if pattern.lower() in ['hevc', 'x265']:
                codec = 'H265'
            elif pattern.lower() in ['x264', 'avc']:
                codec = 'H264'
            if codec not in resolution_and_codec:
                resolution_and_codec.append(codec)
            break  # 只取第一个匹配的编码
    
    return resolution_and_codec


def extract_quality_tags(filename: str) -> List[str]:
    """
    从文件名中提取质量标签
    """
    quality_tags = []
    base_name = os.path.splitext(filename)[0].lower()
    
    # 定义质量标签
    quality_map = {
        'dvd': 'DVD',
        'bluray': 'BluRay',
        'web': 'WEB',
        'remux': 'REMUX',
        'repack': 'REPACK',
        'proper': 'PROPER',
        'extended': 'EXTENDED',
        'theatrical': 'THEATRICAL',
        'directors': 'DIRECTORS',
        'unrated': 'UNRATED'
    }
    
    for pattern, tag in quality_map.items():
        if re.search(rf'\b{pattern}\b', base_name, re.IGNORECASE):
            if tag not in quality_tags:
                quality_tags.append(tag)
    
    return quality_tags


def normalize_filename(filename: str, custom_rules: dict = None) -> str:
    """
    根据命名规则规范化文件名
    """
    base_name = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    
    # 提取番号
    code = extract_code(filename)
    if not code:
        return filename  # 无法提取番号则返回原文件名
    
    # 提取特殊标记
    special_markers, episode_num = extract_special_markers(filename)
    
    # 提取分辨率和编码信息
    resolution_codec = extract_resolution_and_codec(filename)
    
    # 提取质量标签
    quality_tags = extract_quality_tags(filename)
    
    # 构建新的文件名
    new_name_parts = [code]
    
    # 添加特殊标记（按优先级排序）
    ordered_markers = []
    
    # 字幕标记优先
    if 'C' in special_markers:
        ordered_markers.append('C')
        special_markers.remove('C')
    
    # 无码标记
    if 'U' in special_markers:
        ordered_markers.append('U')
        special_markers.remove('U')
    
    # 其他标记
    ordered_markers.extend(special_markers)
    
    # 添加所有标记
    for marker in ordered_markers:
        new_name_parts.append(f'-{marker}')
    
    # 添加分集信息
    if episode_num:
        new_name_parts.append(f'-cd{episode_num}')
    
    # 添加分辨率和编码信息
    for item in resolution_codec:
        new_name_parts.append(f'-{item}')
    
    # 添加质量标签
    for tag in quality_tags:
        new_name_parts.append(f'-{tag}')
    
    # 组合所有部分
    base_new_name = ''.join(new_name_parts)
    new_name = f"{base_new_name}{extension}"
    
    return new_name


def rename_files(directory: str, dry_run: bool = False, recursive: bool = False, 
                custom_rules: dict = None, preserve_original: bool = False):
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
            # 使用新的规范化函数
            new_name = normalize_filename(original_name, custom_rules)
            
            # 如果文件名已经是规范格式，则跳过
            expected_name = normalize_filename(original_name, custom_rules)
            if file_path.name == expected_name:
                print(f"跳过: {original_name} (文件名已经符合规范)")
                continue
            
            new_path = file_path.parent / new_name
            
            # 避免覆盖现有文件
            counter = 1
            original_new_path = new_path
            while new_path.exists() and new_path != file_path:
                name_parts = os.path.splitext(new_name)
                counter_suffix = f"_{counter}"
                new_name = f"{name_parts[0]}{counter_suffix}{name_parts[1]}"
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
                    if preserve_original:
                        # 保留原始文件的副本
                        import shutil
                        shutil.copy2(file_path, new_path)
                        print(f"复制并重命名: {original_name} -> {new_name}")
                    else:
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


def generate_config_template():
    """
    生成配置文件模板
    """
    config = {
        "naming_rules": {
            "code_format": "uppercase_with_hyphen",  # 番号格式: uppercase_with_hyphen, uppercase_no_hyphen, lowercase_with_hyphen
            "markers": {
                "chinese_subtitle": "C",  # 中文字幕标记
                "uncensored": "U",        # 无码标记
                "resolution": True,       # 是否保留分辨率信息
                "codec": True,            # 是否保留编码信息
                "quality_tags": True      # 是否保留质量标签
            },
            "separator": "-",             # 分隔符
            "order": ["code", "markers", "episode", "resolution", "quality"]  # 组成部分顺序
        },
        "file_extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".3gp", ".3g2", ".mxf", ".ts", ".m2ts", ".vob", ".ifo", ".bup"],
        "exclude_patterns": ["sample", "preview", "trailer", "extra", "bonus"],
        "custom_replacements": {
            "ai": "u",
            "uncensored": "u",
            "uncen": "u",
            "uc": "u",
            "ch": "c",
            "chs": "c",
            "cht": "c",
            "cn": "c"
        }
    }
    
    return json.dumps(config, indent=4, ensure_ascii=False)


def main():
    """
    主函数，解析命令行参数
    """
    parser = argparse.ArgumentParser(description='metatube-rename-tool - 媒体文件重命名工具')
    parser.add_argument('directory', nargs='?', default='.', help='要处理的目录路径，默认为当前目录')
    parser.add_argument('-d', '--dry-run', action='store_true', help='仅显示将要执行的重命名操作，不实际执行')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-p', '--preserve', action='store_true', help='保留原始文件（复制并重命名）')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--generate-config', action='store_true', help='生成配置文件模板')
    
    args = parser.parse_args()
    
    if args.generate_config:
        config_template = generate_config_template()
        print("配置文件模板:")
        print(config_template)
        return
    
    custom_rules = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                custom_rules = json.load(f)
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return
    
    rename_files(args.directory, args.dry_run, args.recursive, custom_rules, args.preserve)


if __name__ == '__main__':
    main()