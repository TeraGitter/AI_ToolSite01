'''
# services/png_reader.py
'''
from PIL import Image
import pytesseract
import os

class PNGReader():

    tesseract_path : str

    def __init__(self):
        # Tesseract（PNG→テキスト変換Lib）のパス取得
        self.tesseract_path = os.getenv("TESSERACT_PATH")
        

    def extract_text_from_png(self, file_path: str) -> str:
        """PNGファイルからテキストを抽出する関数"""
        try:
            # Tesseractのパスが設定されているか確認
            if not self.tesseract_path:
                raise ValueError("TESSERACT_PATH環境変数が設定されていません")
                
            # ファイルの存在確認
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
            
            # Windowsの場合、Tesseractのパスを設定
            if os.name == 'nt':
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img, lang='jpn')
                return text
            else:
                raise OSError("このサイトの機能は、Windowsのみサポートされています")
            
        except Exception as e:
            raise IOError(f"テキスト抽出中にエラーが発生しました: {str(e)}")
