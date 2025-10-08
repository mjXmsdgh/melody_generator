import random
from strategies import strategy_chord_progression, strategy_random_choice
from music_theory import SCALES, CHORDS, snap_to_chord
from transformations import transform_add_passing_notes
from accompaniment import ACCOMPANIMENT_MAP, ACCOMPANIMENT_STYLES
from midi_utils import create_midi_file

class MelodyGenerator:
    """
    メロディー生成に関する状態と振る舞いを一元管理するクラス。
    GUIや他のクライアントコードから「部品」として利用されることを想定しています。
    """

    def __init__(self, config):
        """
        コンストラクタ。メロディー生成に必要な設定を辞書として受け取ります。

        Args:
            config (dict): 'key', 'chord_progression' などを含む設定辞書。
        """
        # --- 設定の保持 ---
        self.config = config
        self.key = config['key']
        self.chord_progression = config['chord_progression']
        self.num_measures = config['num_measures']
        self.ticks_per_beat = config['ticks_per_beat']
        self.beats_per_measure = config['beats_per_measure']
        self.motif_notes = config['motif_notes']
        self.play_chords = config.get('play_chords', True) # デフォルト値
        self.accompaniment_generator_name = config.get('accompaniment_generator', 'random')

        # --- 生成結果の初期化 ---
        self.melody_data = None
        self.accompaniment_data = None

    def _validate_config(self):
        """設定値の妥当性を検証します。"""
        if self.key not in SCALES:
            raise ValueError(f"キー '{self.key}' は定義されていません。利用可能なキー: {list(SCALES.keys())}")
        if len(self.chord_progression) < self.num_measures:
            raise ValueError("コード進行の長さが、生成する小節数より短いです。")

    def _initialize_motif_data(self):
        """
        モチーフデータ（タプルのリスト）を内部処理用の辞書のリスト形式に変換します。
        """
        base_measure_data = []
        current_motif_time = 0
        for pitch, duration in self.motif_notes:
            base_measure_data.append({'pitch': pitch, 'time': current_motif_time, 'duration': duration})
            current_motif_time += duration
        return base_measure_data


    def _generate_melody_measures(self, composition, base_measure_data, scale, ticks_per_measure):
        """
        構成レシピに従って、メロディーの全小節を生成します。

        Args:
            composition (list): フィルタ関数のリストのリスト（構成レシピ）。
            base_measure_data (list): 1小節分の元となるモチーフデータ。
            scale (list): 曲のスケール。
            ticks_per_measure (int): 1小節のTick数。

        Returns:
            list: 生成された全メロディーデータ。
        """
        full_melody_data = []
        current_total_time = 0
        print("今回のメロディー構成:")
        for i, filter_chain in enumerate(composition):
            # フィルタを適用して1小節分のメロディーを生成
            processed_data = [note.copy() for note in base_measure_data]
            for transform_func in filter_chain:
                processed_data = transform_func(processed_data, self.key, scale, self.ticks_per_beat)

            # コードにスナップ
            current_chord_name = self.chord_progression[i]
            chord_notes = CHORDS.get(current_chord_name)
            chain_names = ' -> '.join([f.__name__ for f in filter_chain])
            print(f"  - {i+1}小節目: {chain_names} (コード: {current_chord_name})")
            if chord_notes:
                for note in processed_data:
                    note['pitch'] = snap_to_chord(note['pitch'], chord_notes)

            # 経過音を追加
            processed_data = transform_add_passing_notes(processed_data, self.key, scale, self.ticks_per_beat)

            for note in processed_data:
                note['time'] += current_total_time
                full_melody_data.append(note)
            current_total_time += ticks_per_measure
        return full_melody_data

    def _generate_accompaniment(self, scale, ticks_per_measure):
        """
        設定に基づいて伴奏データを生成します。

        Args:
            scale (list): 曲のスケール。
            ticks_per_measure (int): 1小節のTick数。

        Returns:
            list: 生成された全伴奏データ。
        """
        if not self.play_chords:
            return []

        print("\n--- 伴奏を生成します ---")
        selected_style_name = self.accompaniment_generator_name
        if selected_style_name == 'random':
            selected_style_name = random.choice(ACCOMPANIMENT_STYLES)
        actual_generator = ACCOMPANIMENT_MAP.get(selected_style_name)

        if not actual_generator:
            raise ValueError(f"伴奏スタイル '{selected_style_name}' は定義されていません。")

        print(f"使用する伴奏スタイル: {selected_style_name}")

        full_accompaniment_data = []
        current_accomp_time = 0
        for chord_name in self.chord_progression:
            measure_accomp_notes = actual_generator(chord_name, ticks_per_measure, self.key, scale)
            for note in measure_accomp_notes:
                note['time'] += current_accomp_time
                full_accompaniment_data.append(note)
            current_accomp_time += ticks_per_measure
        return full_accompaniment_data

    def generate(self):
        """
        保持している設定に基づき、メロディーと伴奏の内部データを生成します。
        """
        print(f"--- メロディー生成を開始します ({self.num_measures}小節) ---")
        self._validate_config()

        # 1. 準備
        ticks_per_measure = self.ticks_per_beat * self.beats_per_measure
        scale = SCALES[self.key]
        # TODO: 将来的にはstrategyもconfigから選択できるようにする
        composition = strategy_chord_progression(num_measures=self.num_measures)
        base_measure_data = self._initialize_motif_data()

        # 2. メロディーと伴奏の生成
        self.melody_data = self._generate_melody_measures(
            composition, base_measure_data, scale, ticks_per_measure
        )
        self.accompaniment_data = self._generate_accompaniment(scale, ticks_per_measure)

        print("\nメロディーと伴奏の内部データ生成が完了しました。")

    def save_midi(self, output_path):
        """
        生成済みのメロディーデータをMIDIファイルとして保存します。
        """
        if self.melody_data is None:
            raise RuntimeError("メロディーがまだ生成されていません。先に .generate() を呼び出してください。")

        create_midi_file(
            melody_data=self.melody_data,
            output_filename=output_path,
            ticks_per_beat=self.ticks_per_beat,
            accompaniment_data=self.accompaniment_data
        )
        print(f"MIDIファイル '{output_path}' を保存しました。")