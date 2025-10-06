import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ast
import io
import contextlib

# 既存のファイルから設定値や選択肢をインポート
import config
from music_theory import SCALES
from accompaniment import ACCOMPANIMENT_STYLES
from generator import MelodyGenerator


class MelodyGeneratorApp(tk.Tk):
    """メロディー生成ツールのGUIアプリケーション"""

    def __init__(self):
        super().__init__()

        self.title("メロディー生成ツール")
        self.geometry("800x600")
        self.minsize(600, 400)

        # --- メインフレームの作成 ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左側の設定パネル ---
        settings_panel = ttk.LabelFrame(main_frame, text="[A] 設定パネル", padding="10")
        settings_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- 右側の操作・出力パネル ---
        action_panel = ttk.LabelFrame(main_frame, text="[B] 操作・出力パネル", padding="10")
        action_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- ウィジェットの作成と配置 ---
        self._create_settings_widgets(settings_panel)
        self._create_action_widgets(action_panel)

    def _create_settings_widgets(self, parent):
        """設定パネルにウィジェットを作成・配置する"""
        parent.columnconfigure(1, weight=1) # 2列目のテキストボックスが伸びるように設定

        # キー
        ttk.Label(parent, text="キー:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.key_var = tk.StringVar(value=config.INPUT_KEY)
        key_combo = ttk.Combobox(parent, textvariable=self.key_var, values=list(SCALES.keys()))
        key_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        # コード進行
        ttk.Label(parent, text="コード進行:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=2)
        self.chord_text = tk.Text(parent, height=5)
        self.chord_text.insert(tk.END, ", ".join(config.INPUT_CHORD_PROGRESSION))
        self.chord_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        parent.rowconfigure(1, weight=1) # この行が垂直方向に伸びるように設定

        # モチーフ
        ttk.Label(parent, text="モチーフ:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=2)
        self.motif_text = tk.Text(parent, height=5)
        motif_str = ",\n".join([str(n) for n in config.INPUT_MOTIF])
        self.motif_text.insert(tk.END, motif_str)
        self.motif_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        parent.rowconfigure(2, weight=1) # この行が垂直方向に伸びるように設定

        # 小節数
        ttk.Label(parent, text="小節数:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.measures_var = tk.StringVar(value=str(config.NUMBER_OF_MEASURES))
        measures_entry = ttk.Entry(parent, textvariable=self.measures_var, width=10)
        measures_entry.grid(row=3, column=1, sticky=tk.W, pady=2)

        # 伴奏スタイル
        ttk.Label(parent, text="伴奏スタイル:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.accomp_var = tk.StringVar(value=config.ACCOMPANIMENT_GENERATOR)
        # 'random'も選択肢に含める
        accomp_styles = ['random'] + ACCOMPANIMENT_STYLES
        accomp_combo = ttk.Combobox(parent, textvariable=self.accomp_var, values=accomp_styles)
        accomp_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)


    def _create_action_widgets(self, parent):
        """操作・出力パネルにウィジェットを作成・配置する"""
        parent.columnconfigure(0, weight=1) # 1列目が伸びるように設定

        # 出力先
        output_frame = ttk.Frame(parent)
        output_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="出力先:").grid(row=0, column=0, sticky=tk.W)
        self.output_path_var = tk.StringVar(value=config.OUTPUT_PATH)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        browse_button = ttk.Button(output_frame, text="参照...", command=self._browse_output_file)
        browse_button.grid(row=0, column=2, sticky=tk.E)

        # 生成ボタン
        generate_button = ttk.Button(parent, text="メロディーを生成＆保存 (Generate)", command=self._generate_melody)
        generate_button.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, ipady=10)

        # ログ表示エリア
        log_frame = ttk.LabelFrame(parent, text="[C] ログ表示エリア", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1) # この行が垂直方向に伸びるように設定

        self.log_text = tk.Text(log_frame, height=10, state='disabled', wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # スクロールバーを追加
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set

    def _log(self, message):
        """ログエリアにメッセージを追記する"""
        # print文からの出力は末尾に改行を含むため、ここでは改行を追加しない
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END) # 自動スクロール
        self.log_text.config(state='disabled')
        self.update_idletasks() # UIを即時更新

    def _clear_log(self):
        """ログエリアをクリアする"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

    def _browse_output_file(self):
        """「参照」ボタンの処理。ファイル保存ダイアログを開く。"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")],
            initialfile=self.output_path_var.get().split('/')[-1]
        )
        if filename:
            self.output_path_var.set(filename)

    def _generate_melody(self):
        """「生成＆保存」ボタンの処理。メロディー生成ロジックを呼び出す。"""
        self._clear_log()
        self._log(">>> メロディー生成を開始します...\n")

        try:
            # 1. GUIから設定値を取得し、適切な型に変換する
            self._log("1. GUIから設定を読み込み中...")
            
            # コード進行: "C, G, Am" -> ['C', 'G', 'Am']
            chord_prog_text = self.chord_text.get("1.0", tk.END).strip()
            chord_progression = [c.strip() for c in chord_prog_text.split(',') if c.strip()]

            # モチーフ: "(76, 480),\n(74, 240)" -> [(76, 480), (74, 240)]
            motif_text = self.motif_text.get("1.0", tk.END).strip()
            # ast.literal_evalを使って安全に文字列をPythonオブジェクトに変換
            motif_notes = ast.literal_eval(f"[{motif_text}]")

            # 小節数
            num_measures = int(self.measures_var.get())

            # 2. MelodyGeneratorに渡すconfig辞書を構築
            app_config = {
                'motif_notes': motif_notes,
                'key': self.key_var.get(),
                'chord_progression': chord_progression,
                'num_measures': num_measures,
                'ticks_per_beat': config.TICKS_PER_BEAT,
                'beats_per_measure': config.BEATS_PER_MEASURE,
                'play_chords': config.PLAY_CHORDS,
                'accompaniment_generator': self.accomp_var.get(),
            }
            self._log("設定の読み込み完了。\n")

            # 3. MelodyGeneratorのインスタンスを生成し、実行
            self._log("\n2. MelodyGeneratorを初期化...\n")
            generator = MelodyGenerator(config=app_config)

            self._log("3. メロディーと伴奏を生成中...\n")
            
            # print文の出力をキャプチャする
            log_capture = io.StringIO()
            with contextlib.redirect_stdout(log_capture):
                generator.generate() # この中のprint文がlog_captureに書き込まれる
            
            # キャプチャしたログをGUIに表示
            self._log(log_capture.getvalue())

            self._log("\n4. MIDIファイルに保存中...\n")
            output_path = self.output_path_var.get()
            
            log_capture = io.StringIO()
            with contextlib.redirect_stdout(log_capture):
                generator.save_midi(output_path)
            self._log(log_capture.getvalue())

            self._log(f"\n>>> 完了: MIDIファイルを '{output_path}' に保存しました。\n")
            messagebox.showinfo("成功", f"メロディーの生成が完了しました。\nファイル: {output_path}")

        except Exception as e:
            error_message = f"エラーが発生しました: {type(e).__name__}: {e}"
            self._log(f"\n!!! {error_message}")
            messagebox.showerror("エラー", error_message)

def start_app():
    """アプリケーションを起動する"""
    app = MelodyGeneratorApp()
    app.mainloop()

if __name__ == '__main__':
    # このファイルを直接実行したときにGUIを起動するためのコード
    start_app()