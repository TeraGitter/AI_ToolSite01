'''
llm/base.py
'''
from abc import ABC, abstractmethod

class LLMClient(ABC):

    @abstractmethod
    def summarize(self, text: str, max_chars: int) -> str:
        pass