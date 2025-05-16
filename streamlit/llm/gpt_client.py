'''
 llm/gpt_client.py
'''
from openai import OpenAI
from .base import LLMClient
import os

class GPTClient(LLMClient):
    
    gpt_model_name : str = ""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
        try:
            self.gpt_model_name = os.getenv("GPT_MODEL_NAME")
        except ValueError:
            raise ValueError("GPT_MODEL_NAMEが設定されていません")

    def summarize(self, text: str, max_chars: int) -> str:
        prompt = f"次の内容を{str(max_chars)}文字以内で日本語で要約してください：\n{text}"
        response = self.client.chat.completions.create(
            model=self.gpt_model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
