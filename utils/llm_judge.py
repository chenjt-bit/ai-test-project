# utils/llm_judge.py
import os
import json
from openai import OpenAI

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def llm_as_judge(query, answer, criteria):
    """
    调用 DeepSeek 作为裁判，根据 criteria 评估 answer
    """
    prompt = f"""
    你是一个严格、专业的 AI 质量评估专家。
    用户的提问是：{query}
    被测 AI 的回答是：{answer}
    请根据以下预期标准进行评估：{criteria}

    请务必只输出纯 JSON 格式，不要输出任何多余文字。JSON 结构要求：
    {{
        "passed": true 或 false,
        "score": 1到5的整数,
        "reason": "简短说明打分理由"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # 裁判需要绝对客观，温度调到最低
            response_format={"type": "json_object"}  # 强制返回 JSON
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"裁判调用失败: {e}")
        return {"passed": False, "score": 0, "reason": f"裁判接口异常: {e}"}