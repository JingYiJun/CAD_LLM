"""
STL渲染步骤
使用matplotlib将STL文件渲染为图片
"""

from config import IMAGE_RESOLUTION
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from stl import mesh

# 添加父目录到路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class STLRenderingStep:
    """STL渲染步骤类"""

    def __init__(self, resolution=None):
        """
        初始化STL渲染步骤

        Args:
            resolution: 图片分辨率，默认使用配置文件中的设置
        """
        self.resolution = resolution or IMAGE_RESOLUTION
        print("STL渲染步骤初始化完成")

    def run(self, stl_path, image_path):
        """
        将STL文件渲染为图片

        Args:
            stl_path: STL文件路径
            image_path: 输出图片路径

        Returns:
            str: 图片文件路径，如果失败返回None
        """
        print(f"使用matplotlib渲染STL文件为图片: {image_path}")

        try:
            # 读取STL文件
            stl_mesh = mesh.Mesh.from_file(stl_path)
            print(f"STL文件加载成功，三角形数量: {len(stl_mesh.vectors)}")

            # 创建3D图形
            fig = plt.figure(figsize=(self.resolution[0]/100, self.resolution[1]/100), dpi=100)
            ax = fig.add_subplot(111, projection='3d')

            # 提取顶点数据
            vectors = stl_mesh.vectors

            # 绘制所有三角形边框
            for triangle in vectors:
                # triangle 是一个 3x3 的数组，每行是一个顶点 (x, y, z)
                x = triangle[:, 0]
                y = triangle[:, 1]
                z = triangle[:, 2]

                # 添加第一个点到末尾以闭合三角形
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                z = np.append(z, z[0])

                # 绘制三角形边框
                ax.plot(x, y, z, 'b-', alpha=0.6, linewidth=0.5)

            # 填充三角形表面
            ax.plot_trisurf(vectors[:, :, 0].flatten(),
                            vectors[:, :, 1].flatten(),
                            vectors[:, :, 2].flatten(),
                            alpha=0.3, color='lightblue')

            # 计算模型的边界
            min_x = vectors[:, :, 0].min()
            max_x = vectors[:, :, 0].max()
            min_y = vectors[:, :, 1].min()
            max_y = vectors[:, :, 1].max()
            min_z = vectors[:, :, 2].min()
            max_z = vectors[:, :, 2].max()

            print(f"模型边界: X[{min_x:.2f}, {max_x:.2f}], Y[{min_y:.2f}, {max_y:.2f}], Z[{min_z:.2f}, {max_z:.2f}]")

            # 设置坐标轴范围，保持比例
            max_range = max(max_x - min_x, max_y - min_y, max_z - min_z) / 2.0
            mid_x = (max_x + min_x) * 0.5
            mid_y = (max_y + min_y) * 0.5
            mid_z = (max_z + min_z) * 0.5

            ax.set_xlim(mid_x - max_range, mid_x + max_range)
            ax.set_ylim(mid_y - max_range, mid_y + max_range)
            ax.set_zlim(mid_z - max_range, mid_z + max_range)

            # 设置标签和标题
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('CAD模型渲染')

            # 设置视角
            ax.view_init(elev=20, azim=45)

            # 移除坐标轴以获得更清洁的图像
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])

            # 设置背景色
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            ax.grid(False)

            # 保存图片
            plt.tight_layout()
            plt.savefig(image_path, dpi=100, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            plt.close()

            # 验证图片是否生成
            if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                print(f"图片渲染成功: {image_path}")
                return image_path
            else:
                print(f"图片生成失败: {image_path}")
                return None

        except Exception as e:
            print(f"渲染图片时出现错误: {e}")
            import traceback
            traceback.print_exc()
            return None

    def render_multiple_views(self, stl_path, output_dir, base_name):
        """
        从多个角度渲染STL文件

        Args:
            stl_path: STL文件路径
            output_dir: 输出目录
            base_name: 基础文件名

        Returns:
            list: 生成的图片路径列表
        """
        print(f"从多个角度渲染STL文件: {stl_path}")

        # 定义不同的视角
        views = [
            (20, 45, "front"),
            (20, 135, "side"),
            (70, 45, "top"),
            (20, -45, "back")
        ]

        rendered_images = []

        try:
            # 读取STL文件
            stl_mesh = mesh.Mesh.from_file(stl_path)
            vectors = stl_mesh.vectors

            for elev, azim, view_name in views:
                image_path = os.path.join(output_dir, f"{base_name}_{view_name}.png")

                # 创建3D图形
                fig = plt.figure(figsize=(self.resolution[0]/100, self.resolution[1]/100), dpi=100)
                ax = fig.add_subplot(111, projection='3d')

                # 绘制表面
                ax.plot_trisurf(vectors[:, :, 0].flatten(),
                                vectors[:, :, 1].flatten(),
                                vectors[:, :, 2].flatten(),
                                alpha=0.7, color='lightblue')

                # 设置视角
                ax.view_init(elev=elev, azim=azim)
                ax.set_title(f'CAD模型 - {view_name}视角')

                # 移除坐标轴
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_zticks([])
                ax.grid(False)

                # 保存图片
                plt.tight_layout()
                plt.savefig(image_path, dpi=100, bbox_inches='tight',
                            facecolor='white', edgecolor='none')
                plt.close()

                if os.path.exists(image_path):
                    rendered_images.append(image_path)
                    print(f"视角 {view_name} 渲染完成: {image_path}")

        except Exception as e:
            print(f"多视角渲染失败: {e}")
            import traceback
            traceback.print_exc()

        return rendered_images

    def get_image_info(self, image_path):
        """
        获取图片信息

        Args:
            image_path: 图片路径

        Returns:
            dict: 图片信息
        """
        if not os.path.exists(image_path):
            return None

        try:
            from PIL import Image
            with Image.open(image_path) as img:
                return {
                    'path': image_path,
                    'size': os.path.getsize(image_path),
                    'dimensions': img.size,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception as e:
            print(f"获取图片信息失败: {e}")
            return {
                'path': image_path,
                'size': os.path.getsize(image_path),
                'error': str(e)
            }


# 用于独立测试的主函数
if __name__ == "__main__":
    # 首先需要生成一个测试STL文件
    import tempfile
    import cadquery as cq

    # 创建测试STL文件
    with tempfile.TemporaryDirectory() as temp_dir:
        stl_path = os.path.join(temp_dir, "test.stl")

        # 生成测试立方体
        box = cq.Workplane("XY").box(10, 10, 10)
        cq.exporters.export(box, stl_path)

        # 测试渲染
        step = STLRenderingStep()
        image_path = os.path.join(temp_dir, "test_render.png")

        result = step.run(stl_path, image_path)
        if result:
            print(f"单视角渲染成功: {result}")
            print(f"图片信息: {step.get_image_info(result)}")

            # 测试多视角渲染
            multi_images = step.render_multiple_views(stl_path, temp_dir, "test")
            print(f"多视角渲染完成，生成 {len(multi_images)} 张图片")
        else:
            print("渲染失败")
