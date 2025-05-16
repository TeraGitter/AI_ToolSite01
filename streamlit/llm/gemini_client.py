'''
gemini_client.py
'''
import google.generativeai as genai
from .base import LLMClient
import os

class GeminiClient(LLMClient):
    
    gemini_model_name : str = ""

    def __init__(self, api_key: str):
        super().init()
        genai.configure(api_key=api_key)
        try:
            self.gemini_model_name = os.getenv("GEMINI_MODEL_NAME")
        except ValueError:
            raise ValueError("GEMINI_MODEL_NAMEが設定されていません")
        self.model = genai.GenerativeModel(self.gemini_model_name)

    '''
    要約処理
    引数（selfをのぞく）
    text: 入力テキスト
    max_chars: 最大要約文字数
    戻り値：
    要約後のテキスト
    '''
    def summarize(self, text: str, max_chars: int) -> str:
        prompt = f"次の内容を{str(max_chars)}文字以内で日本語で要約してください：\n{text}"
        response = self.model.generate_content(prompt)
        return response.text
