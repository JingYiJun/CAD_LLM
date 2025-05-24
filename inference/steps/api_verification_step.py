"""
API验证步骤
使用OpenAI库调用兼容模式API进行验证并生成新prompt
"""

import base64
import os
import sys
import json
from openai import OpenAI

# 添加父目录到路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.path:
    from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, VERIFICATION_TEMPLATE


class APIVerificationStep:
    """API验证步骤类"""

    def __init__(self, api_key=None, base_url=None, model=None):
        """
        初始化API验证步骤

        Args:
            api_key: API密钥，默认使用配置文件中的设置
            base_url: API基础URL，默认使用配置文件中的设置
            model: 模型名称，默认使用配置文件中的设置
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.base_url = base_url or OPENAI_BASE_URL
        self.model = model or OPENAI_MODEL

        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        print("API验证步骤初始化完成")

    def encode_image_to_base64(self, image_path):
        """
        将图片编码为base64

        Args:
            image_path: 图片路径

        Returns:
            str: base64编码的图片数据
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"图片编码失败: {e}")
            return None

    def run(self, prompt, code, image_path):
        """
        调用API进行验证并生成新prompt

        Args:
            prompt: 原始需求
            code: 生成的代码
            image_path: 渲染的图片路径

        Returns:
            tuple: (验证结果, 新prompt)，失败时返回(None, None)
        """
        print("使用OpenAI库调用API进行验证...")

        # 检查API密钥
        if self.api_key == "YOUR_OPENAI_API_KEY_HERE" or not self.api_key:
            print("错误: 请在config.py中设置正确的API密钥")
            return None, None

        # 编码图片
        image_base64 = self.encode_image_to_base64(image_path)
        if not image_base64:
            print("错误: 图片编码失败")
            return None, None

        # 构建验证prompt
        verification_prompt = VERIFICATION_TEMPLATE.format(prompt=prompt, code=code)

        try:
            print("开始流式生成验证结果...")
            print("-" * 50)

            # 使用OpenAI客户端调用API，启用流式输出
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": verification_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1,
                stream=True  # 启用流式输出
            )

            # 收集完整响应
            full_response = ""

            # 处理流式响应
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)  # 实时打印token
                    full_response += content

            print()  # 换行
            print("-" * 50)

            if full_response:
                print("API验证完成")
                print(f"完整响应长度: {len(full_response)} 字符")

                # 提取新需求
                new_prompt = self.extract_new_prompt(full_response)
                return full_response, new_prompt
            else:
                print("API返回空响应")
                return None, None

        except Exception as e:
            print(f"API调用异常: {e}")
            import traceback
            traceback.print_exc()
            return None, None

    def extract_new_prompt(self, verification_result):
        """
        从验证结果中提取新的prompt

        Args:
            verification_result: API验证结果

        Returns:
            str: 提取的新prompt，失败时返回None
        """
        try:
            print(f"[调试] extract_new_prompt - 输入类型: {type(verification_result)}")
            print(f"[调试] extract_new_prompt - 输入内容: {verification_result}")

            # 解析JSON
            verification_result = verification_result.replace("```json", "").replace("```", "")
            try:
                verification_data = json.loads(verification_result)
                return verification_data.get("Refined Requirement", None)
            except json.JSONDecodeError:
                print("[调试] 解析JSON失败")
                return None

        except Exception as e:
            print(f"提取新prompt时出现错误: {e}")
            print(f"错误类型: {type(e)}")
            import traceback
            print("完整错误堆栈:")
            traceback.print_exc()
            print(f"[调试] verification_result详细信息:")
            print(f"  类型: {type(verification_result)}")
            print(f"  内容: {verification_result}")
            if hasattr(verification_result, '__dict__'):
                print(f"  属性: {verification_result.__dict__}")
            return None

    def save_result(self, verification_result, new_prompt, output_path, original_prompt):
        """
        保存验证结果

        Args:
            verification_result: 验证结果
            new_prompt: 新prompt
            output_path: 保存路径
            original_prompt: 原始prompt
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Original Requirement: {original_prompt}\n\n")
                f.write(f"Verification Result:\n{verification_result}\n\n")
                f.write(f"Refined Requirement: {new_prompt}\n")
            print(f"验证结果已保存: {output_path}")
        except Exception as e:
            print(f"保存验证结果失败: {e}")

    def validate_api_key(self):
        """
        验证API密钥是否有效

        Returns:
            bool: API密钥是否有效
        """
        if not self.api_key or self.api_key == "YOUR_OPENAI_API_KEY_HERE":
            return False

        # 这里可以添加实际的API密钥验证逻辑
        # 目前只是简单检查格式
        return len(self.api_key) > 10


# 用于独立测试的主函数
if __name__ == "__main__":
    import tempfile
    from PIL import Image
    import numpy as np

    print("="*60)
    print("API验证步骤独立测试 - 流式输出演示")
    print("="*60)

    step = APIVerificationStep()

    # 检查API密钥
    if step.validate_api_key():
        print("✓ API密钥有效")

        # 创建测试图片
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_image = temp_file.name

        # 生成一个简单的测试图片
        print("生成测试图片...")
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(temp_image)
        print(f"✓ 测试图片已保存: {temp_image}")

        # 测试API调用
        test_prompt = "设计一个简单的立方体，边长为10mm"
        test_code = """import cadquery as cq

# 创建一个简单的立方体
result = cq.Workplane('XY').box(10, 10, 10)

# 导出为STL
cq.exporters.export(result, "cube.stl")"""

        print(f"\n测试prompt: {test_prompt}")
        print(f"测试代码长度: {len(test_code)} 字符")
        print("\n" + "="*60)
        print("开始API验证（流式输出）:")
        print("="*60)

        verification_result, new_prompt = step.run(test_prompt, test_code, temp_image)

        print("\n" + "="*60)
        if verification_result and new_prompt:
            print("✓ 验证成功")
            print(f"精炼需求: {new_prompt}")
        else:
            print("✗ 验证失败")

        # 清理临时文件
        os.unlink(temp_image)
        print(f"✓ 临时文件已清理")
    else:
        print("✗ API密钥无效，请在config.py中设置正确的密钥")
        print("当前配置:")
        print(f"  - API密钥: {step.api_key[:10]}..." if step.api_key else "  - API密钥: 未设置")
        print(f"  - 基础URL: {step.base_url}")
        print(f"  - 模型: {step.model}")
