"""
代码执行步骤
执行CadQuery代码生成STL文件
"""

import subprocess
import tempfile
import os
import sys

# 添加父目录到路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EXECUTION_TIMEOUT


class CodeExecutionStep:
    """代码执行步骤类"""
    
    def __init__(self, output_dir="./output"):
        """
        初始化代码执行步骤
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print("代码执行步骤初始化完成")

    def run(self, code, output_filename):
        """
        执行代码生成STL文件
        
        Args:
            code: 要执行的CadQuery代码
            output_filename: 输出的STL文件名
            
        Returns:
            str: STL文件的完整路径，如果失败返回None
        """
        print(f"执行CAD代码生成STL文件: {output_filename}")
        
        # 创建临时Python文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_python_file = temp_file.name
        
        try:
            # 执行Python文件
            result = subprocess.run(
                ['python', temp_python_file], 
                capture_output=True, 
                text=True, 
                timeout=EXECUTION_TIMEOUT,
                cwd=self.output_dir
            )
            
            if result.returncode == 0:
                stl_path = os.path.join(self.output_dir, output_filename)
                if os.path.exists(stl_path):
                    file_size = os.path.getsize(stl_path)
                    print(f"STL文件生成成功: {stl_path} (大小: {file_size} 字节)")
                    return stl_path
                else:
                    print(f"错误: STL文件未生成 {stl_path}")
                    return None
            else:
                print(f"代码执行错误 (返回码: {result.returncode}):")
                print(f"标准输出: {result.stdout}")
                print(f"标准错误: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"代码执行超时 (超过 {EXECUTION_TIMEOUT} 秒)")
            return None
        except Exception as e:
            print(f"执行过程中出现异常: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 清理临时文件
            if os.path.exists(temp_python_file):
                os.unlink(temp_python_file)
                print("临时Python文件已清理")

    def validate_stl_file(self, stl_path):
        """
        验证STL文件的有效性
        
        Args:
            stl_path: STL文件路径
            
        Returns:
            bool: 文件是否有效
        """
        if not os.path.exists(stl_path):
            print(f"STL文件不存在: {stl_path}")
            return False
        
        file_size = os.path.getsize(stl_path)
        if file_size == 0:
            print(f"STL文件为空: {stl_path}")
            return False
        
        # 检查STL文件头
        try:
            with open(stl_path, 'rb') as f:
                header = f.read(80)
                if len(header) < 80:
                    print(f"STL文件头过短: {stl_path}")
                    return False
                
                # 读取三角形数量
                triangle_count_bytes = f.read(4)
                if len(triangle_count_bytes) < 4:
                    print(f"无法读取三角形数量: {stl_path}")
                    return False
                
                triangle_count = int.from_bytes(triangle_count_bytes, byteorder='little')
                print(f"STL文件验证通过: {stl_path} (三角形数量: {triangle_count})")
                return True
                
        except Exception as e:
            print(f"STL文件验证失败: {e}")
            return False

    def get_stl_info(self, stl_path):
        """
        获取STL文件信息
        
        Args:
            stl_path: STL文件路径
            
        Returns:
            dict: 文件信息
        """
        if not os.path.exists(stl_path):
            return None
        
        info = {
            'path': stl_path,
            'size': os.path.getsize(stl_path),
            'exists': True
        }
        
        try:
            with open(stl_path, 'rb') as f:
                # 跳过80字节头
                f.read(80)
                # 读取三角形数量
                triangle_count_bytes = f.read(4)
                if len(triangle_count_bytes) == 4:
                    info['triangle_count'] = int.from_bytes(triangle_count_bytes, byteorder='little')
                else:
                    info['triangle_count'] = 0
        except Exception as e:
            print(f"读取STL信息时出错: {e}")
            info['triangle_count'] = 0
        
        return info


# 用于独立测试的主函数
if __name__ == "__main__":
    step = CodeExecutionStep("./test_output")
    
    # 测试代码
    test_code = """
import cadquery as cq

# 创建一个简单的立方体
result = cq.Workplane("XY").box(10, 10, 10)

# 导出为STL
cq.exporters.export(result, "test_cube.stl")
"""
    
    stl_path = step.run(test_code, "test_cube.stl")
    if stl_path:
        print(f"执行成功: {stl_path}")
        print(f"文件有效性: {step.validate_stl_file(stl_path)}")
        print(f"文件信息: {step.get_stl_info(stl_path)}")
    else:
        print("执行失败") 