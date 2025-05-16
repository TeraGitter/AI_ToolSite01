'''
main.py
# StreamlitのメインUI（ここが起点）
'''
from dotenv import load_dotenv
import os
import streamlit as st
from components.uploaded_file import UploadedFile
# import openai
import tempfile
from services.pdf_reader import PDFReader
from services.png_reader import PNGReader
from components.cleanup import CleanUp
from services.summarizer import Summarizer

# スタートアップ・クラス
class Main():

    #  定数・変数 
    # LLM_TYPE(GPT/GEMINI)
    TYPE_GPT = "gpt"
    TYPE_GEMINI = "gemini"

    # .envから取得する変数
    streamlit_secrets_path : str
    max_tokens : int
    max_input_str : str
    llm_type :str
    summary_char_min : int
    summary_char_limit : int
    debug_mode : str
    temp_dir : str
    upload_max_size : int
    saved_path_file : str
    streamlit_secrets_path : str

    # コンストラクタ： .envの環境変数値を設定 
    def __init__(self) -> None:
        
        try:
            if os.getenv("MAX_TOKENS") is None:
                raise ValueError("環境変数：最大トークン数 が未設定です")
            self.max_tokens = int(os.getenv("MAX_TOKENS")) # os.getenv(): str以外は変換する
            
            if os.getenv("MAX_INPUT_STR") is None:
                raise ValueError("環境変数：ファイルの最大文字数 が未設定です")
            self.max_input_str = int(os.getenv("MAX_INPUT_STR"))  # ファイルから読み込んだテキストの最大文字数(スライスする)

            if self.TYPE_GPT != os.getenv("LLM_TYPE") and self.TYPE_GEMINI != os.getenv("LLM_TYPE"):
                raise ValueError("環境変数：LLMクライアントタイプ が未設定です")
            self.llm_type = os.getenv("LLM_TYPE")   # LLMクライアントのタイプ（GPT/GEMINI）
            
            
            if os.getenv("SUMMARY_CHAR_MIN") is None:
                raise ValueError("環境変数：要約文字数下限 が未設定です")
            self.summary_char_min = int(os.getenv("SUMMARY_CHAR_MIN"))
            
            # 要約文字数上限：実行時
            if self.TYPE_GPT == self.llm_type:
                self.summary_char_limit = int(os.getenv("GPT_SUMMARY_CHAR_LIMIT"))   # 要約文字数上限：GPT
            elif self.TYPE_GEMINI == self.llm_type:
                self.summary_char_limit = int(os.getenv("GEMINI_SUMMARY_CHAR_LIMIT"))   # 要約文字数上限：GEMINI
            else:
                raise ValueError("環境変数：要文字数上限 が未設定です")

            self.debug_mode = os.getenv("DEBUG", "False").lower() == "true" # デフォルト値を指定可能
            
            if os.getenv("TEMP_DIR") is None:
                raise ValueError("環境変数：一時ファイル保存フォルダ が未設定です")
            self.temp_dir = os.getenv("TEMP_DIR")
            
            if os.getenv("UPLOAD_MAX_SIZE_MB") is None:
                raise ValueError("環境変数：アップロードファイルの最大サイズ が未設定です")
            self.upload_max_size = int(os.getenv("UPLOAD_MAX_SIZE_MB"))
            
            # 画面で選択したファイル名の保存後の一時ファイル
            self.saved_path_file : str = ""

            # secrets.tomlの設定値を取得
            if os.getenv("STREAMLIT_SECRETS_PATH") is None:
                raise ValueError("環境変数：Streamlitのシークレットファイルのパス が未設定です")
            self.streamlit_secrets_path = os.getenv("STREAMLIT_SECRETS_PATH")
            # ファイル有無チェック
            if not os.path.exists(self.streamlit_secrets_path):
                st.error(f"シークレットファイルが見つかりません: {self.streamlit_secrets_path}")
                raise FileExistsError
        
        except ValueError as e:
            st.error("環境設定ファイル(.env)の値取得に失敗しました")
            st.exception(e)
        
        except FileExistsError as e:
            st.error("シークレットファイル(secrets.toml)の値取得に失敗しました")
            st.exception(e)

    # メイン処理
    def main_proc(self):

        st.set_page_config(layout="wide")  # ページ全体を幅広く表示
        # anchor=Falseは、タイトルにアンカーリンク(#)を付けないようにする設定
        st.title("ファイルAI要約ツール（デモ版）", anchor=False)
        # unsafe_allow_html=Trueを指定すると、HTMLタグをマークダウン内で使用できるようになる
        # セキュリティ上のリスクがあるため、信頼できるHTMLのみ使用する
        st.markdown("<h1 style='font-size: 16px; color: red;'>※個人情報・機密情報を含んだファイルはアップロードしないでください。</h1>", \
            unsafe_allow_html=True)

        uploaded_file = st.file_uploader("アップロードするファイルを選択してください（アップロード可能なファイル形式：PDF / PNG / TXT）", type=["pdf", "png", "txt"])
        input_sum_chars = st.number_input(f"要約文字数の制限：{str(self.summary_char_min)}～{str(self.summary_char_limit)}文字", \
                                    min_value=self.summary_char_min, max_value=self.summary_char_limit)

        if st.button("要約を実行"):
            try:
                # file_upload check
                if uploaded_file is None:
                    # upload_file が異常の場合、例外エラーを発生させる
                    raise FileExistsError
                
                # 要約文字数チェック 
                if input_sum_chars is None or input_sum_chars == 0:
                    st.error("「要約文字数の上限」は必須入力です。") # 未入力エラー
                    st.stop()
                elif not str(input_sum_chars).isdigit():
                    st.error("「要約文字数の上限」は半角数字のみ入力可能です。")
                    st.stop()
                elif self.summary_char_min > input_sum_chars or self.summary_char_limit < input_sum_chars:
                    st.error(f"「要約文字数の上限」は{str(self.summary_char_min)}以上、{str(self.summary_char_limit)}以下の数値を入力してください。" ) # 文字数上限エラー
                    st.stop()

                #  ファイルアップロード 
                # ファイルサイズをバイト単位で取得
                file_size_mb = uploaded_file.size / (1024**2)  # バイトをMBに変換
                if file_size_mb > self.upload_max_size:
                    st.error(f"ファイルサイズが大きすぎます。最大{self.upload_max_size}MBまでアップロード可能です。")
                    raise ValueError("ファイルサイズが制限を超えています")

                self.saved_path_file = UploadedFile.save_uploaded_file(uploaded_file, self.temp_dir)
                if self.saved_path_file is not None:
                    st.success(f"ファイルを保存しました: {self.saved_path_file}")
                
                # ファイル保存成功後
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    # self.tmp_path = tmp.name

                #  # File to text　
                if uploaded_file.name.endswith(".pdf"):
                    text = PDFReader.extract_text_from_pdf(self.saved_path_file)

                elif uploaded_file.name.endswith(".png"):
                    pNGReaderObj = PNGReader()
                    text = pNGReaderObj.extract_text_from_png(self.saved_path_file)

                elif uploaded_file.name.endswith(".txt"):
                    text = uploaded_file.getvalue().decode("utf-8")

                else:
                    st.error("対応していないファイル形式です")
                    text = ""

                if text: # Noneか空文字の場合はスキップ
                    with st.spinner("AIで要約中..."):
                        # LLMの種類を判定して、別処理を呼び出す形にする（複数のLLMにも対応させる）
                        summarizerObj = Summarizer(self.llm_type)
                        summary = summarizerObj.get_llm_client(text[:self.max_input_str], input_sum_chars)
                        
                        st.text_area("要約結果", summary, height=300)
            
            except FileExistsError as e:
                st.error("ファイルが未選択、または存在しません")
                st.exception(e)

            except IOError as e:
                st.error("ファイルの保存に失敗しました")
                st.exception(e)
            
            except ValueError as e:
                st.error("想定外の（LLMモデル等の）値を取得しました")
                st.exception(e)

            except Exception as e:
                st.error("予期しないエラーが発生しました")
                st.exception(e)

            finally:
                self.after_proc()

    # 後始末処理
    def after_proc(self):
        try:
            # 後始末：tempフォルダ配下ｎ全ファイルを削除
            # フォルダパスからディレクトリ部分のみを取得
            saved_path = os.path.dirname(self.saved_path_file)
            CleanUp.cleanup_temp_folder(saved_path)
            st.success("一時作成ファイルをすべて削除しました")
                
        except IOError as e:
            st.error("一時作成ファイルのクリーンアップに失敗しました")
            st.exception(e)

### ※ここから実行部 ##################################### 
# クラス定義の後でインスタンス化する必要があるため、
# ファイルの最後に移動させるか、if __name__ == "__main__": の中で実行する必要がある

load_dotenv()  # .env ファイルの読み込み

# メイン処理実行
mainObj = Main()
mainObj.main_proc()
