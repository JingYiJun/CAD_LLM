#!/usr/bin/env python3
"""
单步调试脚本
用于独立测试流水线中的各个步骤
"""

import sys
import os
from inference_and_verify import CADVerificationPipeline


def test_inference_step():
    """测试推理步骤"""
    print("="*50)
    print("测试推理步骤")
    print("="*50)

    pipeline = CADVerificationPipeline()
    test_prompt = "设计一个简单的立方体，边长为10mm"

    result = pipeline.run_single_step('inference', input_prompt=test_prompt)
    print(f"推理结果长度: {len(result) if result else 0}")
    if result:
        print("推理结果预览:")
        print(result[:200] + "..." if len(result) > 200 else result)


def test_cleaning_step():
    """测试代码清理步骤"""
    print("="*50)
    print("测试代码清理步骤")
    print("="*50)

    pipeline = CADVerificationPipeline()

    # 测试代码
    test_code = """
import cadquery as cq

# 创建一个简单的立方体
result = cq.Workplane("XY").box(10, 10, 10)

# 导出为STL
cq.exporters.export(result, "test.stl")
"""

    result = pipeline.run_single_step('cleaning', raw_code=test_code, output_filename="test_clean.stl")
    if result:
        print("清理结果:")
        print(result)


def test_execution_step():
    """测试代码执行步骤"""
    print("="*50)
    print("测试代码执行步骤")
    print("="*50)

    pipeline = CADVerificationPipeline()

    # 测试代码
    test_code = """
import cadquery as cq

# 创建一个简单的立方体
result = cq.Workplane("XY").box(10, 10, 10)

# 导出为STL
cq.exporters.export(result, "test_execution.stl")
"""

    result = pipeline.run_single_step('execution', code=test_code, output_filename="test_execution.stl")
    if result:
        print(f"STL文件生成: {result}")
        print(f"文件大小: {os.path.getsize(result)} 字节")


def test_rendering_step():
    """测试渲染步骤"""
    print("="*50)
    print("测试渲染步骤")
    print("="*50)

    # 首先需要有一个STL文件
    pipeline = CADVerificationPipeline()

    # 先生成一个STL文件
    test_code = """
import cadquery as cq

result = cq.Workplane("XY").box(10, 10, 10)
cq.exporters.export(result, "test_render_input.stl")
"""

    stl_path = pipeline.run_single_step('execution', code=test_code, output_filename="test_render_input.stl")

    if stl_path:
        # 然后渲染它
        image_path = os.path.join(pipeline.output_dir, "test_render_output.png")
        result = pipeline.run_single_step('rendering', stl_path=stl_path, image_path=image_path)

        if result:
            print(f"图片渲染成功: {result}")
            print(f"图片大小: {os.path.getsize(result)} 字节")


def test_verification_step():
    """测试API验证步骤"""
    print("="*60)
    print("测试API验证步骤 - 流式输出演示")
    print("="*60)

    pipeline = CADVerificationPipeline()

    # 检查API密钥是否配置
    print("🔑 检查API配置...")
    if not pipeline.api_verification_step.validate_api_key():
        print("❌ 跳过API验证测试 - 未配置有效的API密钥")
        print("\n配置说明:")
        print("请在 config.py 中设置正确的 OPENAI_API_KEY")
        print("当前配置:")
        step = pipeline.api_verification_step
        print(f"  - API密钥: {step.api_key[:10]}..." if step.api_key else "  - API密钥: 未设置")
        print(f"  - 基础URL: {step.base_url}")
        print(f"  - 模型: {step.model}")
        return

    print("✅ API密钥验证通过")

    # 首先生成测试STL和图片
    print("\n🔧 准备测试数据...")
    test_code = """import cadquery as cq

# 创建一个简单的立方体，边长为10mm
result = cq.Workplane("XY").box(10, 10, 10)

# 导出为STL文件
cq.exporters.export(result, "test_verify_input.stl")"""

    print("📦 生成测试STL文件...")
    stl_path = pipeline.run_single_step('execution', code=test_code, output_filename="test_verify_input.stl")

    if stl_path:
        print(f"✅ STL文件生成成功: {stl_path}")

        print("🖼️ 生成测试图片...")
        image_path = os.path.join(pipeline.output_dir, "test_verify_input.png")
        image_result = pipeline.run_single_step('rendering', stl_path=stl_path, image_path=image_path)

        if image_result:
            print(f"✅ 图片生成成功: {image_result}")

            # 测试API验证
            test_prompt = "设计一个简单的立方体，边长为10mm"

            print(f"\n🎯 测试验证参数:")
            print(f"   原始需求: {test_prompt}")
            print(f"   代码长度: {len(test_code)} 字符")
            print(f"   图片路径: {image_result}")

            print("\n" + "="*60)
            print("🚀 开始API验证（流式输出）:")
            print("="*60)

            result = pipeline.run_single_step('verification',
                                              prompt=test_prompt,
                                              code=test_code,
                                              image_path=image_result)

            print("\n" + "="*60)
            if result:
                verification_result, new_prompt = result
                print("✅ 验证完成!")
                print(f"\n📝 提取的精炼需求:")
                print(f"   {new_prompt}")
                print(f"\n📊 统计信息:")
                print(f"   响应总长度: {len(verification_result)} 字符")
                print(f"   精炼需求长度: {len(new_prompt)} 字符")
            else:
                print("❌ 验证失败")
        else:
            print("❌ 图片生成失败，无法进行验证测试")
    else:
        print("❌ STL文件生成失败，无法进行验证测试")


def main():
    """主函数"""
    tests = {
        'inference': test_inference_step,
        'cleaning': test_cleaning_step,
        'execution': test_execution_step,
        'rendering': test_rendering_step,
        'verification': test_verification_step,
    }

    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name in tests:
            tests[test_name]()
        elif test_name == 'all':
            for name, test_func in tests.items():
                try:
                    test_func()
                    print("\n")
                except Exception as e:
                    print(f"测试 {name} 失败: {e}")
                    import traceback
                    traceback.print_exc()
                    print("\n")
        else:
            print(f"未知测试: {test_name}")
            print(f"可用测试: {list(tests.keys())} 或 'all'")
    else:
        print("用法: python debug_steps.py <test_name>")
        print(f"可用测试: {list(tests.keys())}")
        print("或者使用 'all' 运行所有测试")


if __name__ == "__main__":
    main()
