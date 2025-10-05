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

    def generate(self):
        """
        保持している設定に基づき、メロディーと伴奏の内部データを生成します。
        この段階ではファイル保存は行いません。
        """
        print(f"--- メロディー生成を開始します ({self.num_measures}小節) ---")
        if self.key not in SCALES:
            raise ValueError(f"キー '{self.key}' は定義されていません。利用可能なキー: {list(SCALES.keys())}")
        if len(self.chord_progression) < self.num_measures:
            raise ValueError("コード進行の長さが、生成する小節数より短いです。")

        ticks_per_measure = self.ticks_per_beat * self.beats_per_measure
        scale = SCALES[self.key]

        # 1. Arrangerを呼び出し、曲の構成レシピを取得
        # TODO: 将来的にはstrategyもconfigから選択できるようにする
        composition = strategy_chord_progression(num_measures=self.num_measures)

        # 2. 元のMotifを、フィルタが扱える初期データ形式に変換
        base_measure_data = []
        current_motif_time = 0
        for pitch, duration in self.motif_notes:
            base_measure_data.append({'pitch': pitch, 'time': current_motif_time, 'duration': duration})
            current_motif_time += duration

        # 3. 各小節について、レシピに従いメロディーを生成
        full_melody_data = []
        current_total_time = 0
        print("今回のメロディー構成:")
        for i, filter_chain in enumerate(composition):
            processed_data = [note.copy() for note in base_measure_data]
            for transform_func in filter_chain:
                processed_data = transform_func(processed_data, self.key, scale, self.ticks_per_beat)

            current_chord_name = self.chord_progression[i]
            chord_notes = CHORDS.get(current_chord_name)
            chain_names = ' -> '.join([f.__name__ for f in filter_chain])
            print(f"  - {i+1}小節目: {chain_names} (コード: {current_chord_name})")
            if chord_notes:
                for note in processed_data:
                    note['pitch'] = snap_to_chord(note['pitch'], chord_notes)

            processed_data = transform_add_passing_notes(processed_data, self.key, scale, self.ticks_per_beat)

            for note in processed_data:
                note['time'] += current_total_time
                full_melody_data.append(note)
            current_total_time += ticks_per_measure

        # 4. 伴奏データを生成
        accompaniment_data = []
        if self.play_chords:
            print("\n--- 伴奏を生成します ---")
            selected_style_name = self.accompaniment_generator_name
            if selected_style_name == 'random':
                selected_style_name = random.choice(ACCOMPANIMENT_STYLES)
            actual_generator = ACCOMPANIMENT_MAP.get(selected_style_name)

            if not actual_generator:
                raise ValueError(f"伴奏スタイル '{selected_style_name}' は定義されていません。")

            print(f"使用する伴奏スタイル: {selected_style_name}")
            current_accomp_time = 0
            for chord_name in self.chord_progression:
                measure_accomp_notes = actual_generator(chord_name, ticks_per_measure, self.key, scale)
                for note in measure_accomp_notes:
                    note['time'] += current_accomp_time
                    accompaniment_data.append(note)
                current_accomp_time += ticks_per_measure

        # 5. 生成したデータをインスタンス変数に格納
        self.melody_data = full_melody_data
        self.accompaniment_data = accompaniment_data
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