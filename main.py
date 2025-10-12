import sys
import os

# このファイルがどこから実行されても、プロジェクトのルートディレクトリを
# Pythonのモジュール検索パスに追加します。
# これにより、'from melody_generator.gui.app import start_app' のような
# 絶対インポートが常に機能するようになります。
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from melody_generator.gui.app import start_app

def main():
    """GUIアプリケーションを起動する。"""
    print("GUIアプリケーションを起動します...")
    start_app()

if __name__ == "__main__":
    main()