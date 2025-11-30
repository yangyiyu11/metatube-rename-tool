#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metatube-rename-tool 测试脚本
测试各种文件名格式下的番号提取功能

采用分类组织的方式管理测试用例，提高可读性和可维护性
"""

import unittest
import os
from metatube_rename import extract_code


class TestAVRename(unittest.TestCase):
    """
    测试metatube-rename-tool的番号提取功能
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        # 定义测试用例分类，便于管理和维护
        self.test_cases = {
            # 基础标准格式 - 带连字符的标准番号
            'standard_hyphenated': [
                ("SVCAO-020-U.mp4", "SVCAO-020"),
                ("MIAA-837-C.mp4", "MIAA-837"),
                ("ABF-010.mp4", "ABF-010"),
                ("ABF-007-UC.mp4", "ABF-007"),
                ("ABF-016.mp4", "ABF-016"),
                ("PRED-467-C.mp4", "PRED-467"),
                ("MIMK-067.mp4", "MIMK-067"),
                ("MFYD-038.mp4", "MFYD-038"),
                ("MNGS-006.mp4", "MNGS-006"),
                ("suke-117.mp4", "SUKE-117"),  # 小写转换为大写
                ("ABF-012.mp4", "ABF-012"),
                ("SSIS-722.mp4", "SSIS-722"),
                ("MIRD-255.mp4", "MIRD-255"),
                ("ABF-011.mp4", "ABF-011"),
                ("IPZZ-120.mp4", "IPZZ-120"),
                ("ABF-020.mp4", "ABF-020"),
                ("ABF-022.mp4", "ABF-022"),
                ("ABF-015.mp4", "ABF-015"),
                ("LULU-394-U.mp4", "LULU-394"),
                ("SONE-785.mp4", "SONE-785"),
                ("HMN-350.mp4", "HMN-350"),
                ("SONE-784.mp4", "SONE-784"),
                ("MIDA-039.mp4", "MIDA-039"),
                ("IPZZ-550-C.mp4", "IPZZ-550"),
                ("HMN-459-U.mp4", "HMN-459"),
                ("EBWH-215.mp4", "EBWH-215"),
                ("IDBD-864.mp4", "IDBD-864"),
                ("ABF-024.mp4", "ABF-024"),
                ("MIMK-186.mp4", "MIMK-186"),
                ("SONE-081-UC.mp4", "SONE-081"),
                ("ABF-002-UC.mp4", "ABF-002"),
                ("HUNTB-685-C.mp4", "HUNTB-685"),
                ("MIZD-152.mp4", "MIZD-152"),
                ("STARS-979-UC.mp4", "STARS-979"),
                ("IPX-726-U.mp4", "IPX-726"),
                ("MIAB-086.mp4", "MIAB-086"),
                ("ABF-023-C.mp4", "ABF-023"),
                ("SONE-008-UC.mp4", "SONE-008"),
                ("ABF-005-UC.mp4", "ABF-005"),
                ("HSODA-046.mp4", "HSODA-046"),
                ("PFES-058-U.mp4", "PFES-058"),
                ("GVH-775.mp4", "GVH-775"),
                ("MIAB-245.mp4", "MIAB-245"),
                ("JAC-176.mp4", "JAC-176"),
                ("ABF-017-UC.mp4", "ABF-017"),
                ("MIUM-939.mp4", "MIUM-939"),
                ("DVAJ-419.mp4", "DVAJ-419"),
                ("MIDV-530-U.mp4", "MIDV-530"),
                ("ABF-004-C.mp4", "ABF-004"),
                ("MIMK-069.mp4", "MIMK-069"),
                ("MIDV-640.mp4", "MIDV-640"),
                ("ABF-008.mp4", "ABF-008"),
                ("MIBB-026.mp4", "MIBB-026"),
                ("FSDSS-259.mp4", "FSDSS-259"),
                ("SUKE-177.mp4", "SUKE-177"),
                ("IPX-988.mp4", "IPX-988"),
                ("MIAB-043.mp4", "MIAB-043"),
                ("SONE-561-UC.mp4", "SONE-561"),
                ("MIAB-259.mp4", "MIAB-259"),
                ("CLOT-034C.mp4", "CLOT-034"),
                ("ABF-003-UC.mp4", "ABF-003"),
                ("IPZZ-079 未公开映像收录！导演剪辑版 BEAUTY VENUS V【BVPP】.mp4", "IPZZ-079"),
                ("HUNTB-405.H265.mp4", "HUNTB-405"),
                ("MGM-032.mp4", "MGM-032"),
                ("ABF-006.mp4", "ABF-006"),
                ("SQB-217.mp4", "SQB-217"),
                ("SONE-360-UC.mp4", "SONE-360"),
                ("PRED-772-C.mp4", "PRED-772"),
                ("MIDV-715-U.mp4", "MIDV-715"),
                ("MAAN-900.mp4", "MAAN-900"),
                ("ABF-014-UC.mp4", "ABF-014"),
                ("ABF-021-UC.mp4", "ABF-021"),
            ],
            
            # 无分隔符格式
            'no_separator': [
                ("DVMM-307.mp4", "DVMM-307"),
                ("DVMM-298C.mp4", "DVMM-298"),
                ("PBD-455.H265.mp4", "PBD-455"),
            ],
            
            # 带域名和@符号的格式
            'with_domain': [
                ("jav20s8.com@IDBD-867.mp4", "IDBD-867"),
                ("hhd800.com@MKMP-666.mp4", "MKMP-666"),
                ("hhd800.com@HUNTC-296-C.mp4", "HUNTC-296"),
                ("hhd800.com@VEC-738.mp4", "VEC-738"),
                ("hhd800.com@KSAT-094.mp4", "KSAT-094"),
                ("dxxdom.com@DVMM275.mp4", "DVMM-275"),
                ("@jnty60.app_SDAM-093.mp4", "SDAM-093"),
            ],
            
            # 带madoubt.com格式
            'with_madoubt': [
                ("madoubt.com 359589.xyz MIRD-246.mp4", "MIRD-246"),
                ("madoubt.com 852588.xyz LULU-380.mp4", "LULU-380"),
                ("madoubt.com 853363.xyz DOKS-645.mp4", "DOKS-645"),
                ("madoubt.com 393266.xyz PBD-488.mp4", "PBD-488"),
                ("madoubt.com 523229.xyz LULU-340.mp4", "LULU-340"),
                ("madoubt.com 986628.xyz LULU-356.mp4", "LULU-356"),
                ("madoubt.com 986569.xyz LULU-351.mp4", "LULU-351"),
                ("madoubt.com 663982.xyz SDJS-331.mp4", "SDJS-331"),
            ],
            
            # 带特殊标记（uncensored, AI等）
            'with_special_markers': [
                ("PRED-444-uncensored-nyap2p.com.mp4", "PRED-444"),
                ("LULU-330-uncensored-nyap2p.com.mp4", "LULU-330"),
                ("MIRD-254-AI.mp4", "MIRD-254"),
                ("SONE-745-AI.mp4", "SONE-745"),
                ("IPZZ-460_CH-nyap2p.com.mp4", "IPZZ-460"),
                ("SDJS-028_Uncensored.mp4", "SDJS-028"),
                ("LULU-249-C.mp4", "LULU-249"),
                ("lulu-272-4k.mp4", "LULU-272"),
                ("LULU-332 残業中、2人きりの社内でむっちりデカ尻人妻台湾人女上司のムレムレパンスト挑発に乗せられ脚テク.mp4", "LULU-332"),
                ("WoXav.Com@HUNTC-097 だれとでも定額挿れ放題 銀行編3 その地方銀行はお金以外に.mp4", "HUNTC-097"),
                ("WoXav.Com@IPZZ-319 オッパイ丸出し オマ○コ中出し 射精無制限 桜空もも.mp4", "IPZZ-319"),
            ],
            
            # 分集文件格式
            'episode_format': [
                ("HD_sdjs-097-1.mp4", "SDJS-097"),
                ("HD_sdjs-097-2.mp4", "SDJS-097"),
                ("ABC-330-cd1.mp4", "ABC-330"),
                ("ABC-330-cd2.mp4", "ABC-330"),
                ("MCBD-25-C-cd1.mkv", "MCBD-25"),
                ("MCBD-25-C-cd2.mkv", "MCBD-25"),
            ],
            
            # 边界情况和非番号文件
            'edge_cases': [
                ("filelist.txt", None),  # 非视频文件
                ("dvrt-045.mp4", "DVRT-045"),  # 小写但有效
                ("1start00398hhb.restored.mp4", "START-00398"),  # 应识别为有效的番号
                ("1start00405hhb.restored.mp4", "START-00405"),  # 应识别为有效的番号
                ("madoubt.com", None),  # 仅域名，无番号
            ],
        }
    
    def test_extract_code_by_category(self):
        """
        按分类测试各种文件名格式下的番号提取
        这种方式可以更清晰地管理测试用例并定位问题
        """
        # 遍历所有分类的测试用例
        for category, cases in self.test_cases.items():
            print(f"\n测试分类: {category}")
            for filename, expected in cases:
                with self.subTest(category=category, filename=filename):
                    result = extract_code(filename)
                    self.assertEqual(result, expected, 
                                    f"在分类 '{category}' 中，文件名 '{filename}' 的提取失败：\n"  
                                    f"期望: {expected}, 实际: {result}")
                    print(f"  ✓ {filename} -> {result}")
    
    def test_specific_categories(self):
        """
        可以单独测试特定分类的测试用例，方便调试
        例如: self._run_category_tests('with_domain')
        """
        # 默认不执行，用于手动调试
        pass
    
    def _run_category_tests(self, category_name):
        """
        运行指定分类的测试用例
        
        Args:
            category_name: 测试分类名称
        """
        if category_name in self.test_cases:
            print(f"\n测试特定分类: {category_name}")
            for filename, expected in self.test_cases[category_name]:
                result = extract_code(filename)
                self.assertEqual(result, expected)
                print(f"  ✓ {filename} -> {result}")
        else:
            self.fail(f"测试分类 '{category_name}' 不存在")
    
    def test_all_formats(self):
        """
        运行所有测试用例，不管分类
        确保所有情况都能正确处理
        
        注意：这个测试方法与test_extract_code_by_category功能相似，但没有分类信息。
        保留此方法是为了兼容旧的测试调用方式和提供全局验证。
        """
        all_cases = []
        for cases in self.test_cases.values():
            all_cases.extend(cases)
        
        print(f"\n运行所有 {len(all_cases)} 个测试用例")
        for filename, expected in all_cases:
            with self.subTest(filename=filename):
                result = extract_code(filename)
                self.assertEqual(result, expected)
    
    def test_original_format_compatibility(self):
        """
        测试原始测试用例的兼容性
        注意：这些测试用例已经合并到各个分类中，此方法仅作为兼容性验证
        """
        # 原始测试用例已全部合并到各个分类中
        # 此处仅保留方法以保持API兼容性，但实际测试通过分类测试完成
        self.assertTrue(True)  # 始终通过的测试


def main():
    """
    运行测试并显示详细结果
    """
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
