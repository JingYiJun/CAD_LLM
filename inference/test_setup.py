#!/usr/bin/env python3
"""
测试脚本：验证CAD验证流水线的环境设置
"""

import traceback


def test_imports():
    """测试所有必要的包是否正确安装"""
    print("测试依赖包导入...")

    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
    except ImportError as e:
        print(f"✗ PyTorch 导入失败: {e}")
        return False

    try:
        import transformers
        print(f"✓ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"✗ Transformers 导入失败: {e}")
        traceback.print_exc()
        return False

    try:
        import peft
        print(f"✓ PEFT")
    except ImportError as e:
        print(f"✗ PEFT 导入失败: {e}")
        return False

    try:
        import cadquery as cq
        print(f"✓ CadQuery")
    except ImportError as e:
        print(f"✗ CadQuery 导入失败: {e}")
        return False

    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy 导入失败: {e}")
        return False

    try:
        import matplotlib.pyplot as plt
        print(f"✓ Matplotlib")
    except ImportError as e:
        print(f"✗ Matplotlib 导入失败: {e}")
        return False

    try:
        from stl import mesh
        print(f"✓ numpy-stl")
    except ImportError as e:
        print(f"✗ numpy-stl 导入失败: {e}")
        return False

    try:
        import requests
        print(f"✓ Requests {requests.__version__}")
    except ImportError as e:
        print(f"✗ Requests 导入失败: {e}")
        return False

    try:
        from PIL import Image
        print(f"✓ Pillow")
    except ImportError as e:
        print(f"✗ Pillow 导入失败: {e}")
        return False

    return True


def test_cuda():
    """测试CUDA是否可用"""
    print("\n测试CUDA...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA 可用, 设备数量: {torch.cuda.device_count()}")
            print(f"  当前设备: {torch.cuda.current_device()}")
            print(f"  设备名称: {torch.cuda.get_device_name()}")
            return True
        else:
            print("✗ CUDA 不可用")
            return False
    except Exception as e:
        print(f"✗ CUDA 测试失败: {e}")
        return False


def test_cadquery():
    """测试CadQuery基本功能"""
    print("\n测试CadQuery...")
    try:
        import cadquery as cq
        import tempfile
        import os

        # 创建一个简单的立方体
        box = cq.Workplane("XY").box(10, 10, 10)

        # 尝试导出为STL
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_file:
            temp_stl = temp_file.name

        cq.exporters.export(box, temp_stl)

        if os.path.exists(temp_stl) and os.path.getsize(temp_stl) > 0:
            print("✓ CadQuery 基本功能正常")
            os.unlink(temp_stl)
            return True
        else:
            print("✗ CadQuery STL导出失败")
            return False

    except Exception as e:
        print(f"✗ CadQuery 测试失败: {e}")
        return False


def test_matplotlib_stl_rendering():
    """测试matplotlib + numpy-stl渲染功能"""
    print("\n测试matplotlib + numpy-stl渲染...")
    try:
        import cadquery as cq
        from stl import mesh
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        import numpy as np
        import tempfile
        import os

        # 创建一个简单的立方体并导出为STL
        box = cq.Workplane("XY").box(10, 10, 10)

        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_stl_file:
            temp_stl = temp_stl_file.name

        cq.exporters.export(box, temp_stl)

        # 尝试读取和渲染STL文件
        stl_mesh = mesh.Mesh.from_file(temp_stl)

        # 创建3D图形
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        # 提取顶点数据
        vectors = stl_mesh.vectors

        # 简单渲染测试
        ax.plot_trisurf(vectors[:, :, 0].flatten(),
                        vectors[:, :, 1].flatten(),
                        vectors[:, :, 2].flatten(),
                        alpha=0.5, color='lightblue')

        # 保存为临时图片
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img_file:
            temp_img = temp_img_file.name

        plt.savefig(temp_img, dpi=100, bbox_inches='tight')
        plt.close()

        # 检查文件是否生成
        if os.path.exists(temp_img) and os.path.getsize(temp_img) > 0:
            print("✓ matplotlib + numpy-stl 渲染功能正常")
            # 清理临时文件
            os.unlink(temp_stl)
            os.unlink(temp_img)
            return True
        else:
            print("✗ matplotlib 渲染失败")
            return False

    except Exception as e:
        print(f"✗ matplotlib + numpy-stl 渲染测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("="*50)
    print("CAD验证流水线环境测试")
    print("="*50)

    success = True

    # 测试导入
    success &= test_imports()

    # # 测试CUDA
    # success &= test_cuda()

    # # 测试CadQuery
    # success &= test_cadquery()

    # 测试matplotlib + numpy-stl渲染
    success &= test_matplotlib_stl_rendering()

    print("\n" + "="*50)
    if success:
        print("✓ 所有测试通过！环境设置正确。")
        print("你现在可以运行CAD验证流水线了。")
    else:
        print("✗ 部分测试失败，请检查环境设置。")
        print("请参考README.md中的安装说明。")
    print("="*50)


if __name__ == "__main__":
    main()
