import tkinter as tk
from tkinter import ttk

# 既存のファイルから設定値や選択肢をインポート
from melody_generator import config
from melody_generator.core.music_theory import SCALES
from melody_generator.core.accompaniment import ACCOMPANIMENT_STYLES

class SettingsPanel(ttk.LabelFrame):
    """設定関連のウィジェットをまとめたパネル"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="[A] 設定パネル", padding="10", *args, **kwargs)

        self.columnconfigure(1, weight=1) # 2列目のテキストボックスが伸びるように設定

        # キー
        ttk.Label(self, text="キー:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.key_var = tk.StringVar(value=config.INPUT_KEY)
        key_combo = ttk.Combobox(self, textvariable=self.key_var, values=list(SCALES.keys()))
        key_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        # コード進行
        ttk.Label(self, text="コード進行:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=2)
        self.chord_text = tk.Text(self, height=5)
        self.chord_text.insert(tk.END, ", ".join(config.INPUT_CHORD_PROGRESSION))
        self.chord_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        self.rowconfigure(1, weight=1) # この行が垂直方向に伸びるように設定

        # モチーフ
        ttk.Label(self, text="モチーフ:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=2)
        self.motif_text = tk.Text(self, height=5)
        motif_str = ",\n".join([str(n) for n in config.INPUT_MOTIF])
        self.motif_text.insert(tk.END, motif_str)
        self.motif_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        self.rowconfigure(2, weight=1) # この行が垂直方向に伸びるように設定

        # 小節数
        ttk.Label(self, text="小節数:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.measures_var = tk.StringVar(value=str(config.NUMBER_OF_MEASURES))
        measures_entry = ttk.Entry(self, textvariable=self.measures_var, width=10)
        measures_entry.grid(row=3, column=1, sticky=tk.W, pady=2)

        # 伴奏スタイル
        ttk.Label(self, text="伴奏スタイル:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.accomp_var = tk.StringVar(value=config.ACCOMPANIMENT_GENERATOR)
        # 'random'も選択肢に含める
        accomp_styles = ['random'] + ACCOMPANIMENT_STYLES
        accomp_combo = ttk.Combobox(self, textvariable=self.accomp_var, values=accomp_styles)
        accomp_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)