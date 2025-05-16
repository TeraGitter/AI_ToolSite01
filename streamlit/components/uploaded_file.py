'''
# components/uploaded_file.py
'''
import os
import uuid
from typing import Optional

class UploadedFile():

    def save_uploaded_file(uploaded_file, save_dir) -> Optional[str]:
        """
        アップロードされたファイルを一時保存する関数
        保存したファイルのパスを返す
        """
        try:
            if uploaded_file is None:
                return None

            os.makedirs(save_dir, exist_ok=True)

            # ファイル名をユニークにする（UUID + 元のファイル名）
            unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
            file_path = os.path.join(save_dir, unique_filename)

            # ファイル保存
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            return file_path
        except:
            raise IOError