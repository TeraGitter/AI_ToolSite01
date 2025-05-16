'''
summarizer.py
'''
from llm.gpt_client import GPTClient
from llm.gemini_client import GeminiClient
import streamlit as st
import openai
import google.generativeai as gemini

class Summarizer():

    TYPE_GPT = "gpt"
    TYPE_GEMINI = "gemini"
    run_llm_type : str = ""
    # 未設定時の要約文字数
    DEFAULT_SUM_CHAR : int = 300

    
    def __init__(self, llm_tpye : str):
            self.run_llm_type = llm_tpye

    def get_llm_client(self, text : str, max_chars: int = DEFAULT_SUM_CHAR):
        
        try:
            if self.run_llm_type == self.TYPE_GPT:
                if "OPENAI_API_KEY" not in st.secrets:
                    raise ValueError("OPENAI_API_KEYが設定されていません")
                openai.api_key = st.secrets["OPENAI_API_KEY"]
                gPTClientObj = GPTClient(api_key=openai.api_key)
                return gPTClientObj.summarize(text, max_chars)
            
            elif self.run_llm_type == self.TYPE_GEMINI:
                if "GEMINI_API_KEY" not in st.secrets:
                    raise ValueError("GEMINI_API_KEYが設定されていません")
                gemini.api_key = st.secrets["GEMINI_API_KEY"]
                geminiClientObj = GeminiClient(api_key=gemini.api_key)
                return geminiClientObj.summarize(text, max_chars)
            else:
                raise ValueError(f"サポートされていないLLM typeが設定されています: {self.run_llm_type}")
        except Exception as e:
            raise Exception(f"LLMクライアントの処理中にエラーが発生しました: {str(e)}")
