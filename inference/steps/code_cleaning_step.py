"""
代码清理步骤
清理和准备CadQuery代码，添加正确的导出语句
"""

import re
import os
import sys

# 添加父目录到路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CodeCleaningStep:
    """代码清理步骤类"""

    def __init__(self):
        """初始化代码清理步骤"""
        print("代码清理步骤初始化完成")

    def run(self, raw_code, output_filename):
        """
        执行代码清理步骤

        Args:
            raw_code: 原始生成的代码
            output_filename: 输出的STL文件名

        Returns:
            str: 清理后的代码，如果失败返回None
        """
        print("开始清理生成的代码...")

        # 查找import cadquery的起始位置
        start = raw_code.find("import cadquery")
        if start == -1:
            print("警告: 未找到 'import cadquery'")
            # 尝试查找其他可能的导入方式
            alt_patterns = ["import cadquery as cq", "from cadquery import", "import cq"]
            for pattern in alt_patterns:
                start = raw_code.find(pattern)
                if start != -1:
                    print(f"找到替代导入: {pattern}")
                    break

            if start == -1:
                print("错误: 无法找到CadQuery导入语句")
                return None

        cleaned = raw_code[start:]

        # 处理导出语句
        export_pattern = r"(cq\.)?exporters\.export\s*\(\s*([^,]+),\s*['\"].*?\.stl['\"].*?\)"
        matches = list(re.finditer(export_pattern, cleaned))

        if matches:
            print(f"找到 {len(matches)} 个导出语句")
            first_param = matches[0].group(2).strip()
            # 移除所有导出语句
            cleaned_wo_exports = re.sub(export_pattern, "", cleaned)
            lines = cleaned_wo_exports.split('\n')
            cleaned_lines = []
            for line in lines:
                if not re.search(r"(cq\.)?exporters\.", line):
                    cleaned_lines.append(line)
            cleaned_wo_exports = '\n'.join(cleaned_lines)

            # 添加新的导出语句
            final_code = cleaned_wo_exports.strip() + f"\n\ncq.exporters.export({first_param}, \"{output_filename}\")"
        else:
            print("警告: 未找到导出语句，尝试自动添加")
            # 尝试寻找可能的结果变量
            result_patterns = [
                r"(\w+)\s*=.*\.extrude\(",
                r"(\w+)\s*=.*\.revolve\(",
                r"(\w+)\s*=.*\.loft\(",
                r"(\w+)\s*=.*\.sweep\(",
                r"(\w+)\s*=.*\.box\(",
                r"(\w+)\s*=.*\.cylinder\(",
                r"(\w+)\s*=.*\.sphere\(",
                r"result\s*=",
                r"model\s*=",
                r"shape\s*=",
                r"part\s*=",
                r"assembly\s*=",
            ]

            result_var = "result"
            for pattern in result_patterns:
                matches = re.findall(pattern, cleaned)
                if matches:
                    result_var = matches[-1]  # 使用最后一个匹配
                    print(f"找到可能的结果变量: {result_var}")
                    break

            # 添加导出语句
            final_code = cleaned.strip() + f"\n\ncq.exporters.export({result_var}, \"{output_filename}\")"

        print("代码清理完成")
        return final_code

    def save_result(self, result, output_path):
        """
        保存清理后的代码

        Args:
            result: 清理后的代码
            output_path: 保存路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"清理后的代码已保存: {output_path}")

    def validate_code(self, code):
        """
        验证代码的基本结构

        Args:
            code: 要验证的代码

        Returns:
            bool: 代码是否有效
        """
        required_elements = [
            "import cadquery",
            "cq.Workplane",
            "cq.exporters.export"
        ]

        for element in required_elements:
            if element not in code:
                print(f"验证失败: 缺少 {element}")
                return False

        print("代码验证通过")
        return True


# 用于独立测试的主函数
if __name__ == "__main__":
    step = CodeCleaningStep()

    # 测试代码
    test_code = """
import cadquery as cq

# 创建一个简单的立方体
result = cq.Workplane("XY").box(10, 10, 10)

# 导出为STL
cq.exporters.export(result, "test.stl")
"""

    cleaned = step.run(test_code, "cleaned_test.stl")
    if cleaned:
        print("清理结果:")
        print(cleaned)
        print(f"代码有效性: {step.validate_code(cleaned)}")
