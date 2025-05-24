# CAD验证流水线配置文件

# 模型配置
BASE_MODEL_ID = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
PEFT_MODEL_ID = "../train/lora_deepseek16b_best"

# 输出目录
OUTPUT_DIR = './output'

# OpenAI兼容API配置（使用阿里云兼容模式）
# 请在https://dashscope.console.aliyun.com/获取你的API密钥
OPENAI_API_KEY = "<Your API Key>"  # 请替换为你的实际API密钥
OPENAI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 阿里云兼容模式接口
OPENAI_MODEL = "qwen-vl-max-latest"  # 使用通义千问视觉模型

# 渲染配置
IMAGE_RESOLUTION = [800, 600]  # 渲染图片分辨率

# 推理配置
MAX_NEW_TOKENS = 1024
DO_SAMPLE = False

# 执行配置
EXECUTION_TIMEOUT = 60  # 代码执行超时时间（秒）

# 验证模板
VERIFICATION_TEMPLATE = """
Please analyze this CAD design task:

Original requirement: {prompt}

Generated code:
```python
{code}
```

Please examine the generated 3D model image and verify the following points:
1. Does the generated model meet the original requirements?
2. Is the code implementation correct?
3. If there are any issues, what are the specific problems?

Then please generate an improved design requirement for the next iteration. The new requirement should:
- Address any identified problems
- Be more precise and detailed
- Maintain consistency with the original requirement

Please respond in the following json format, and the output should be in English, do not generate any other text or code:
{{
    "Verification Result": "Correct/Has Issues",
    "Problem Description": "If there are issues, describe them in detail",
    "Improvement Suggestions": "Specific improvement recommendations",
    "Refined Requirement": "Improved detailed design requirement"
}}
"""
