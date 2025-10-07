import tkinter as tk
from tkinter import messagebox
import io
import contextlib

import config
from generator import MelodyGenerator
# データ変換ユーティリティをインポート
from gui_utils import parse_chord_progression, parse_motif, ParsingError

class AppController:
    """
    アプリケーションのロジックを管理するコントローラー。
    View (GUI) からの指示を受け、Model (Generator) を操作し、結果をViewに反映する。
    """
    def __init__(self, view):
        """
        コントローラーを初期化します。

        Args:
            view (MelodyGeneratorApp): 操作対象のViewインスタンス。
        """
        self.view = view

    def handle_generate_melody(self, settings_data, output_path):
        """
        メロディー生成プロセス全体を管理します。

        Args:
            settings_data (dict): Viewから受け取った設定値の辞書。
            output_path (str): 出力ファイルパス。
        """
        self.view.clear_log()
        self.view.log(">>> メロディー生成を開始します...\n")

        try:
            # 1. GUIから受け取った設定値をユーティリティ関数で解析・変換する
            self.view.log("1. GUIから設定を読み込み中...")

            # ユーティリティ関数を呼び出す
            chord_progression = parse_chord_progression(settings_data['chord_prog_text'])
            motif_notes = parse_motif(settings_data['motif_text'])
            
            # 小節数
            num_measures = int(settings_data['measures_var'])

            # 2. MelodyGeneratorに渡すconfig辞書を構築
            app_config = {
                'motif_notes': motif_notes,
                'key': settings_data['key_var'],
                'chord_progression': chord_progression,
                'num_measures': num_measures,
                'ticks_per_beat': config.TICKS_PER_BEAT,
                'beats_per_measure': config.BEATS_PER_MEASURE,
                'play_chords': config.PLAY_CHORDS,
                'accompaniment_generator': settings_data['accomp_var'],
            }
            self.view.log("設定の読み込み完了。\n")

            # 3. MelodyGeneratorのインスタンスを生成し、実行
            self.view.log("\n2. MelodyGeneratorを初期化...\n")
            generator = MelodyGenerator(config=app_config)

            self.view.log("3. メロディーと伴奏を生成中...\n")
            with io.StringIO() as log_capture, contextlib.redirect_stdout(log_capture):
                generator.generate()
                self.view.log(log_capture.getvalue())

            self.view.log("\n4. MIDIファイルに保存中...\n")
            with io.StringIO() as log_capture, contextlib.redirect_stdout(log_capture):
                generator.save_midi(output_path)
                self.view.log(log_capture.getvalue())

            self.view.log(f"\n>>> 完了: MIDIファイルを '{output_path}' に保存しました。\n")
            messagebox.showinfo("成功", f"メロディーの生成が完了しました。\nファイル: {output_path}")

        except (ParsingError, ValueError) as e:
            error_message = f"入力値のエラー: {e}"
            self.view.log(f"\n!!! {error_message}")
            messagebox.showerror("入力エラー", error_message)
        except Exception as e: # その他の予期せぬエラー
            error_message = f"エラーが発生しました: {type(e).__name__}: {e}"
            self.view.log(f"\n!!! {error_message}")
            messagebox.showerror("エラー", error_message)