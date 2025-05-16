'''
# services/pdf_reader.py
'''
import fitz  # PyMuPDF
import os

class PDFReader():

    def extract_text_from_pdf(file_path: str) -> str:
        """PDFファイルからテキストを抽出する関数"""
        text = ""
        try:
            # ファイルの存在確認
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text += page.get_text()
            return text
        except:
            raise IOError
