"""
CAD验证流水线主文件
重构为使用模块化的步骤类
"""

import os
import sys
from config import OUTPUT_DIR

# 导入步骤类
from steps import (
    InferenceStep,
    CodeCleaningStep,
    CodeExecutionStep,
    STLRenderingStep,
    APIVerificationStep
)


class CADVerificationPipeline:
    """CAD验证流水线主类"""

    def __init__(self, base_model_id=None, peft_model_id=None, output_dir=None):
        """
        初始化验证流水线

        Args:
            base_model_id: 基础模型路径
            peft_model_id: PEFT模型路径
            output_dir: 输出目录
        """
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        print("="*50)
        print("初始化CAD验证流水线")
        print("="*50)

        # 初始化所有步骤
        self.inference_step = InferenceStep(base_model_id, peft_model_id)
        self.code_cleaning_step = CodeCleaningStep()
        self.code_execution_step = CodeExecutionStep(self.output_dir)
        self.stl_rendering_step = STLRenderingStep()
        self.api_verification_step = APIVerificationStep()

        print(f"流水线初始化完成，输出目录: {self.output_dir}")

    def run_pipeline(self, initial_prompt):
        """
        运行完整的验证流水线

        Args:
            initial_prompt: 初始设计需求
        """
        print("="*50)
        print("开始CAD验证流水线")
        print("="*50)

        results = {}

        # 步骤1: 第一次推理
        print("\n步骤1: 第一次模型推理")
        first_code = self.inference_step.run(initial_prompt)
        results['first_code'] = first_code

        # 保存第一次生成的代码
        first_code_path = os.path.join(self.output_dir, "first_generated_code.py")
        self.inference_step.save_result(first_code, first_code_path)

        # 步骤2: 清理第一次生成的代码
        print("\n步骤2: 清理第一次生成的代码")
        first_stl_filename = "first_model.stl"
        cleaned_first_code = self.code_cleaning_step.run(first_code, first_stl_filename)

        if cleaned_first_code is None:
            print("第一次代码清理失败，流水线终止")
            return results

        results['cleaned_first_code'] = cleaned_first_code

        # 保存清理后的代码
        first_cleaned_code_path = os.path.join(self.output_dir, "first_cleaned_code.py")
        self.code_cleaning_step.save_result(cleaned_first_code, first_cleaned_code_path)

        # 步骤3: 执行第一次代码
        print("\n步骤3: 执行第一次生成的代码")
        first_stl_path = self.code_execution_step.run(cleaned_first_code, first_stl_filename)

        if first_stl_path is None:
            print("第一次STL生成失败，流水线终止")
            return results

        results['first_stl_path'] = first_stl_path

        # 步骤4: 渲染第一次模型
        print("\n步骤4: 渲染第一次生成的模型")
        first_image_path = os.path.join(self.output_dir, "first_model.png")
        first_image_result = self.stl_rendering_step.run(first_stl_path, first_image_path)

        if first_image_result is None:
            print("第一次图片渲染失败，但继续流水线")
            # 这里可以生成一个占位图片或使用默认图片

        results['first_image_path'] = first_image_result

        # 步骤5: API验证并生成新需求
        print("\n步骤5: API验证并生成新需求")
        verification_result, new_prompt = None, None

        if first_image_result:
            verification_result, new_prompt = self.api_verification_step.run(
                initial_prompt, cleaned_first_code, first_image_result
            )

        if verification_result is None or new_prompt is None:
            print("API验证失败，使用备用prompt进行第二次推理")
            new_prompt = f"请改进以下设计: {initial_prompt}。生成更精确和详细的CAD模型。"
            verification_result = f"API验证失败，使用备用prompt: {new_prompt}"

        results['verification_result'] = verification_result
        results['new_prompt'] = new_prompt

        # 保存验证结果
        verification_path = os.path.join(self.output_dir, "verification_result.txt")
        self.api_verification_step.save_result(
            verification_result, new_prompt, verification_path, initial_prompt
        )

        # 步骤6: 基于新需求进行第二次推理
        print("\n步骤6: 基于新需求进行第二次推理")
        second_code = self.inference_step.run(new_prompt)
        results['second_code'] = second_code

        # 保存第二次生成的代码
        second_code_path = os.path.join(self.output_dir, "second_generated_code.py")
        self.inference_step.save_result(second_code, second_code_path)

        # 步骤7: 清理第二次生成的代码
        print("\n步骤7: 清理第二次生成的代码")
        second_stl_filename = "second_model.stl"
        cleaned_second_code = self.code_cleaning_step.run(second_code, second_stl_filename)

        if cleaned_second_code is None:
            print("第二次代码清理失败，但第一次生成已完成")
            self._print_partial_results(results)
            return results

        results['cleaned_second_code'] = cleaned_second_code

        # 保存清理后的代码
        second_cleaned_code_path = os.path.join(self.output_dir, "second_cleaned_code.py")
        self.code_cleaning_step.save_result(cleaned_second_code, second_cleaned_code_path)

        # 步骤8: 执行第二次代码
        print("\n步骤8: 执行第二次生成的代码")
        second_stl_path = self.code_execution_step.run(cleaned_second_code, second_stl_filename)

        if second_stl_path is None:
            print("第二次STL生成失败，但前面的步骤已完成")
            self._print_partial_results(results)
            return results

        results['second_stl_path'] = second_stl_path

        # 步骤9: 渲染第二次模型
        print("\n步骤9: 渲染第二次生成的模型")
        second_image_path = os.path.join(self.output_dir, "second_model.png")
        second_image_result = self.stl_rendering_step.run(second_stl_path, second_image_path)

        if second_image_result is None:
            print("第二次图片渲染失败，但其他步骤已完成")

        results['second_image_path'] = second_image_result

        # 完成流水线
        self._print_complete_results(results)
        return results

    def _print_partial_results(self, results):
        """打印部分完成的结果"""
        print("\n" + "="*50)
        print("CAD验证流水线部分完成！")
        print("="*50)
        print(f"输出文件位置: {self.output_dir}")
        print("已生成的文件:")
        print(f"- 第一次原始代码: first_generated_code.py")
        print(f"- 第一次清理代码: first_cleaned_code.py")
        if 'first_stl_path' in results:
            print(f"- 第一次STL模型: first_model.stl")
        if 'first_image_path' in results:
            print(f"- 第一次渲染图片: first_model.png")
        if 'verification_result' in results:
            print(f"- 验证结果: verification_result.txt")
        if 'second_code' in results:
            print(f"- 第二次原始代码: second_generated_code.py")
        if 'cleaned_second_code' in results:
            print(f"- 第二次清理代码: second_cleaned_code.py")

    def _print_complete_results(self, results):
        """打印完整的结果"""
        print("\n" + "="*50)
        print("CAD验证流水线完成！")
        print("="*50)
        print(f"输出文件位置: {self.output_dir}")
        print("生成的文件:")
        print(f"- 第一次原始代码: first_generated_code.py")
        print(f"- 第一次清理代码: first_cleaned_code.py")
        if 'first_stl_path' in results:
            print(f"- 第一次STL模型: first_model.stl")
        if 'first_image_path' in results:
            print(f"- 第一次渲染图片: first_model.png")
        print(f"- 验证结果: verification_result.txt")
        print(f"- 第二次原始代码: second_generated_code.py")
        print(f"- 第二次清理代码: second_cleaned_code.py")
        if 'second_stl_path' in results:
            print(f"- 第二次STL模型: second_model.stl")
        if 'second_image_path' in results:
            print(f"- 第二次渲染图片: second_model.png")

    def run_single_step(self, step_name, **kwargs):
        """
        运行单个步骤（用于调试）

        Args:
            step_name: 步骤名称
            **kwargs: 步骤参数

        Returns:
            步骤结果
        """
        step_map = {
            'inference': self.inference_step,
            'cleaning': self.code_cleaning_step,
            'execution': self.code_execution_step,
            'rendering': self.stl_rendering_step,
            'verification': self.api_verification_step
        }

        if step_name not in step_map:
            print(f"未知步骤: {step_name}")
            print(f"可用步骤: {list(step_map.keys())}")
            return None

        step = step_map[step_name]
        return step.run(**kwargs)


def main():
    """主函数"""
    # 获取用户输入
    if len(sys.argv) > 1:
        user_prompt = ' '.join(sys.argv[1:])
    else:
        user_prompt = input("请输入CAD设计需求: ")

    # 初始化流水线
    pipeline = CADVerificationPipeline()

    # 运行流水线
    results = pipeline.run_pipeline(user_prompt)

    # 返回结果供其他程序使用
    return results


if __name__ == "__main__":
    main()
