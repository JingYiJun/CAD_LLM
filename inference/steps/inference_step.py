"""
模型推理步骤
使用训练好的模型生成CAD代码
"""

from config import *
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os
import sys

# 添加父目录到路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class InferenceStep:
    """模型推理步骤类"""

    def __init__(self, base_model_id=None, peft_model_id=None):
        """
        初始化推理步骤

        Args:
            base_model_id: 基础模型路径
            peft_model_id: PEFT模型路径
        """
        self.base_model_id = base_model_id or BASE_MODEL_ID
        self.peft_model_id = peft_model_id or PEFT_MODEL_ID

        print("初始化推理模型...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_id, trust_remote_code=True)
        self.base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_id,
            trust_remote_code=True,
            device_map="auto"
        )
        self.model = PeftModel.from_pretrained(self.base_model, self.peft_model_id, device_map="auto")
        self.model.eval()
        print("推理模型初始化完成")

    @torch.inference_mode()
    def run(self, input_prompt):
        """
        执行推理步骤

        Args:
            input_prompt: 输入的设计需求

        Returns:
            str: 生成的代码
        """
        print(f"正在推理: {input_prompt[:100]}...")

        # 构建prompt
        prompt = f"<s>[INST] {input_prompt} [/INST]"

        # 编码输入
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to("cuda")
        input_lengths = inputs["input_ids"].shape[1]
        max_new_tokens = max(1, MAX_NEW_TOKENS - input_lengths)

        # 生成代码
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=DO_SAMPLE
        )

        # 解码输出
        output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 清理输出
        if "</s>" in output:
            output = output.replace("</s>", "")

        if "[/INST]" in output:
            output = output.split("[/INST]", 1)[1].strip()

        print(f"推理完成，生成代码长度: {len(output)}")
        return output

    def save_result(self, result, output_path):
        """
        保存推理结果

        Args:
            result: 推理结果
            output_path: 保存路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"推理结果已保存: {output_path}")


# 用于独立测试的主函数
if __name__ == "__main__":
    step = InferenceStep()
    test_prompt = "设计一个简单的立方体，边长为10mm"
    result = step.run(test_prompt)
    print("推理结果:")
    print(result)
