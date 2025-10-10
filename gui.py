import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ast
import io
import contextlib

# 既存のファイルから設定値や選択肢をインポート
import config
from generator import MelodyGenerator # このファイルはMelodyGeneratorのみ使用するため変更なし
# UIコンポーネントをインポート
from settings_panel import SettingsPanel
from action_panel import ActionPanel
from controller import AppController

class MelodyGeneratorApp(tk.Tk):
    """メロディー生成ツールのGUIアプリケーション"""

    def __init__(self):
        super().__init__()

        self.title("メロディー生成ツール")
        self.geometry("800x600")
        self.minsize(600, 400)

        # --- コントローラーの初期化 ---
        self.controller = AppController(self)

        # --- メインフレームの作成 ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左側の設定パネル ---
        self.settings_panel = SettingsPanel(main_frame)
        self.settings_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- 右側の操作・出力パネル ---
        self.action_panel = ActionPanel(
            main_frame,
            generate_command=self._generate_melody,
            browse_command=self._browse_output_file
        )
        self.action_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def log(self, message):
        """ログエリアにメッセージを追記する"""
        # print文からの出力は末尾に改行を含むため、ここでは改行を追加しない
        log_widget = self.action_panel.log_text
        log_widget.config(state='normal')
        log_widget.insert(tk.END, message)
        log_widget.see(tk.END) # 自動スクロール
        log_widget.config(state='disabled')
        self.update_idletasks() # UIを即時更新

    def clear_log(self):
        """ログエリアをクリアする"""
        log_widget = self.action_panel.log_text
        log_widget.config(state='normal')
        log_widget.delete('1.0', tk.END)
        log_widget.config(state='disabled')

    def _browse_output_file(self):
        """「参照」ボタンの処理。ファイル保存ダイアログを開く。"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")],
            initialfile=self.action_panel.output_path_var.get().split('/')[-1]
        )
        if filename:
            self.action_panel.output_path_var.set(filename)

    def _generate_melody(self):
        """「生成＆保存」ボタンの処理。メロディー生成ロジックを呼び出す。"""
        # 1. UIパネルから現在の設定値を取得
        settings_data = {
            'key_var': self.settings_panel.key_var.get(),
            'chord_prog_text': self.settings_panel.chord_text.get("1.0", tk.END),
            'motif_text': self.settings_panel.motif_text.get("1.0", tk.END),
            'measures_var': self.settings_panel.measures_var.get(),
            'accomp_var': self.settings_panel.accomp_var.get(),
        }
        output_path = self.action_panel.output_path_var.get()

        # 2. コントローラーに処理を委譲
        self.controller.handle_generate_melody(settings_data, output_path)

def start_app():
    """アプリケーションを起動する"""
    app = MelodyGeneratorApp()
    app.mainloop()

if __name__ == '__main__':
    # このファイルを直接実行したときにGUIを起動するためのコード
    start_app()