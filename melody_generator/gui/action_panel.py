import tkinter as tk
from tkinter import ttk

from melody_generator import config

class ActionPanel(ttk.LabelFrame):
    """操作ボタンやログ表示エリアをまとめたパネル"""

    def __init__(self, parent, generate_command, browse_command, *args, **kwargs):
        super().__init__(parent, text="[B] 操作・出力パネル", padding="10", *args, **kwargs)

        self.columnconfigure(0, weight=1) # 1列目が伸びるように設定

        # 出力先
        output_frame = ttk.Frame(self)
        output_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="出力先:").grid(row=0, column=0, sticky=tk.W)
        self.output_path_var = tk.StringVar(value=config.OUTPUT_PATH)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        browse_button = ttk.Button(output_frame, text="参照...", command=browse_command)
        browse_button.grid(row=0, column=2, sticky=tk.E)

        # 生成ボタン
        generate_button = ttk.Button(self, text="メロディーを生成＆保存 (Generate)", command=generate_command)
        generate_button.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, ipady=10)

        # ログ表示エリア
        log_frame = ttk.LabelFrame(self, text="[C] ログ表示エリア", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1) # この行が垂直方向に伸びるように設定

        self.log_text = tk.Text(log_frame, height=10, state='disabled', wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # スクロールバーを追加
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set