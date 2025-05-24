# CAD验证流水线 - 模块化版本

这是一个完整的CAD设计验证流水线，采用模块化设计，每个步骤都是独立的类，便于调试和维护。

## 🏗️ 架构设计

### 模块化结构
```
inference/
├── inference_and_verify.py    # 主流水线类
├── config.py                  # 配置文件
├── requirements.txt           # 依赖包
├── test_setup.py             # 环境测试
├── debug_steps.py            # 单步调试脚本
├── steps/                    # 步骤模块
│   ├── __init__.py           # 包初始化
│   ├── inference_step.py     # 模型推理步骤
│   ├── code_cleaning_step.py # 代码清理步骤
│   ├── code_execution_step.py # 代码执行步骤
│   ├── stl_rendering_step.py # STL渲染步骤
│   └── api_verification_step.py # API验证步骤
└── README.md                 # 说明文档
```

### 步骤说明
1. **InferenceStep**: 使用训练好的模型生成CAD代码
2. **CodeCleaningStep**: 清理和准备CadQuery代码
3. **CodeExecutionStep**: 执行代码生成STL文件
4. **STLRenderingStep**: 使用matplotlib渲染STL为图片
5. **APIVerificationStep**: 使用OpenAI库调用兼容模式API验证并生成新需求

## 🚀 快速开始

### 1. 安装依赖
```bash
cd inference
pip install -r requirements.txt
```

### 2. 配置API密钥
编辑 `config.py` 文件：
```python
# OpenAI兼容API配置（使用阿里云兼容模式）
OPENAI_API_KEY = "你的实际API密钥"  # 阿里云DashScope API密钥
OPENAI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 兼容模式接口
OPENAI_MODEL = "qwen-vl-max-latest"  # 通义千问视觉模型
```

### 3. 环境测试
```bash
python test_setup.py
```

### 4. 运行完整流水线
```bash
# 命令行方式
python inference_and_verify.py "设计一个简单的立方体，边长为10mm"

# 交互式方式
python inference_and_verify.py
```

## 🔧 调试功能

### 单步调试
你可以独立测试每个步骤：

```bash
# 测试推理步骤
python debug_steps.py inference

# 测试代码清理步骤
python debug_steps.py cleaning

# 测试代码执行步骤
python debug_steps.py execution

# 测试STL渲染步骤
python debug_steps.py rendering

# 测试API验证步骤（包含流式输出演示）
python debug_steps.py verification

# 运行所有测试
python debug_steps.py all
```

### 流式输出演示
API验证步骤支持实时显示生成的Token：
- 运行 `python debug_steps.py verification` 可以看到完整的流式输出效果
- 或者直接运行 `cd steps && python api_verification_step.py` 进行独立测试
- 生成过程中会实时显示每个Token，最后显示完整结果统计

### 直接调用步骤
```python
from inference_and_verify import CADVerificationPipeline

pipeline = CADVerificationPipeline()

# 运行单个步骤
result = pipeline.run_single_step('inference', input_prompt="设计一个立方体")
```

### 独立测试步骤类
每个步骤文件都可以独立运行：
```bash
cd steps
python inference_step.py
python code_cleaning_step.py
python code_execution_step.py
python stl_rendering_step.py
python api_verification_step.py
```

## 📁 输出文件

完整流水线运行后，所有文件保存在 `./output/` 目录：

- `first_generated_code.py` - 第一次生成的原始代码
- `first_cleaned_code.py` - 第一次清理后的代码
- `first_model.stl` - 第一次生成的STL模型
- `first_model.png` - 第一次模型的渲染图片
- `verification_result.txt` - API验证结果和新需求
- `second_generated_code.py` - 第二次生成的原始代码
- `second_cleaned_code.py` - 第二次清理后的代码
- `second_model.stl` - 第二次生成的STL模型
- `second_model.png` - 第二次模型的渲染图片

## 🔄 流水线步骤

1. **第一次推理** → 生成初始CAD代码
2. **代码清理** → 清理和准备代码
3. **代码执行** → 创建STL文件
4. **图片渲染** → 生成可视化图片
5. **智能验证** → 使用OpenAI兼容API分析并提出改进建议
6. **第二次推理** → 基于改进需求重新生成
7. **代码清理** → 清理第二次生成的代码
8. **代码执行** → 生成第二次STL文件
9. **图片渲染** → 渲染最终模型

## 🎯 技术特点

- **模块化设计**: 每个步骤独立，便于调试和维护
- **OpenAI兼容**: 使用OpenAI库调用阿里云兼容模式API
- **流式输出**: API验证步骤支持实时显示生成的Token
- **轻量级渲染**: 使用matplotlib + numpy-stl
- **鲁棒性**: 优雅的错误处理和降级策略
- **可扩展性**: 易于添加新步骤或修改现有步骤
- **调试友好**: 支持单步调试和详细日志

## 📋 自定义步骤

### 添加新步骤
1. 在 `steps/` 目录创建新的步骤文件
2. 实现步骤类，包含 `run()` 方法
3. 在 `steps/__init__.py` 中导入
4. 在主流水线中集成

### 修改现有步骤
每个步骤都是独立的类文件，可以直接修改而不影响其他步骤。

## ⚠️ 注意事项

1. 确保你有有效的阿里云DashScope API密钥
2. 确保CUDA环境正确配置用于模型推理
3. 确保CadQuery环境正确安装
4. 第一次运行可能需要较长时间加载模型
5. 使用单步调试功能来定位具体问题
6. API验证步骤使用OpenAI库，但连接到阿里云兼容模式接口

## 🛠️ 故障排除

- **模型加载失败**: 检查模型路径配置
- **API调用失败**: 检查API密钥和网络连接，确保使用正确的兼容模式URL
- **代码执行失败**: 使用 `debug_steps.py execution` 单独测试
- **渲染失败**: 使用 `debug_steps.py rendering` 单独测试
- **环境问题**: 运行 `python test_setup.py` 检查环境
- **OpenAI库问题**: 确保安装了最新版本的openai库

## 📈 性能优化

- 模型只在第一次使用时加载
- 每个步骤都有独立的错误处理
- 支持部分完成的流水线
- 详细的调试信息帮助快速定位问题
- OpenAI库自动处理重试和错误恢复
