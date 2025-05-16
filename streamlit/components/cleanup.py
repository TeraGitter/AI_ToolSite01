'''
# services/cleanup.py
'''

import os
# import shutil

class CleanUp():

    def cleanup_temp_folder(folder_path: str):
        """
        指定されたフォルダ内の全ファイルを削除する関数
        フォルダ自体は残す
        """
        if not os.path.exists(folder_path):
            raise FileExistsError

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
