import random
import logging
from dataclasses import dataclass, field
from typing import List, Tuple

from strategies import strategy_chord_progression, strategy_random_choice
from music_theory import SCALES, CHORDS, snap_to_chord
from transformations import transform_add_passing_notes
from accompaniment import ACCOMPANIMENT_MAP, ACCOMPANIMENT_STYLES
from midi_utils import create_midi_file

@dataclass
class MelodyConfig:
    """メロディー生成のための設定を保持するデータクラス。"""
    key: str
    chord_progression: List[str]
    num_measures: int
    ticks_per_beat: int
    beats_per_measure: int
    motif_notes: List[Tuple[int, int]]
    play_chords: bool = True
    accompaniment_generator: str = 'random'

    def __post_init__(self):
        """初期化後のバリデーション。"""
        if self.key not in SCALES:
            raise ValueError(f"キー '{self.key}' は定義されていません。利用可能なキー: {list(SCALES.keys())}")
        if len(self.chord_progression) < self.num_measures:
            raise ValueError("コード進行の長さが、生成する小節数より短いです。")

class MelodyProcessor:
    """メロディー生成の具体的な処理を担当するクラス。"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def process(self, config: MelodyConfig) -> List[dict]:
        """
        設定に基づき、メロディーデータを生成します。

        Args:
            config (MelodyConfig): メロディー生成のための設定。

        Returns:
            List[dict]: 生成されたメロディーデータのリスト。
        """
        # 1. 準備
        scale = SCALES[config.key]
        ticks_per_measure = config.ticks_per_beat * config.beats_per_measure
        # TODO: 将来的にはstrategyもconfigから選択できるようにする
        composition = strategy_chord_progression(num_measures=config.num_measures)
        base_measure_data = self._initialize_motif_data(config)

        # 2. メロディーの全小節を生成
        melody_data = self._generate_melody_measures(
            config, composition, base_measure_data, scale, ticks_per_measure
        )
        return melody_data

    def _initialize_motif_data(self, config: MelodyConfig) -> List[dict]:
        base_measure_data = []
        current_motif_time = 0
        for pitch, duration in config.motif_notes:
            base_measure_data.append({'pitch': pitch, 'time': current_motif_time, 'duration': duration})
            current_motif_time += duration
        return base_measure_data

    def _generate_melody_measures(self, config: MelodyConfig, composition: List, base_measure_data: List[dict], scale: List[int], ticks_per_measure: int) -> List[dict]:
        full_melody_data = []
        current_total_time = 0
        self.logger.info("今回のメロディー構成:")
        for i, filter_chain in enumerate(composition):
            processed_data = [note.copy() for note in base_measure_data]
            for transform_func in filter_chain:
                processed_data = transform_func(processed_data, config.key, scale, config.ticks_per_beat)

            current_chord_name = config.chord_progression[i]
            chord_notes = CHORDS.get(current_chord_name)
            chain_names = ' -> '.join([f.__name__ for f in filter_chain])
            self.logger.info(f"  - {i+1}小節目: {chain_names} (コード: {current_chord_name})")
            if chord_notes:
                for note in processed_data:
                    note['pitch'] = snap_to_chord(note['pitch'], chord_notes)

            processed_data = transform_add_passing_notes(processed_data, config.key, scale, config.ticks_per_beat)
            for note in processed_data:
                note['time'] += current_total_time
                full_melody_data.append(note)
            current_total_time += ticks_per_measure
        return full_melody_data

class AccompanimentProcessor:
    """伴奏生成の具体的な処理を担当するクラス。"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def process(self, config: MelodyConfig, scale: List[int], ticks_per_measure: int) -> List[dict]:
        """
        設定に基づき、伴奏データを生成します。

        Args:
            config (MelodyConfig): メロディー生成のための設定。
            scale (List[int]): 曲のスケール。
            ticks_per_measure (int): 1小節のTick数。

        Returns:
            List[dict]: 生成された全伴奏データ。
        """
        if not config.play_chords:
            return []

        self.logger.info("\n--- 伴奏を生成します ---")
        selected_style_name = config.accompaniment_generator
        if selected_style_name == 'random':
            selected_style_name = random.choice(ACCOMPANIMENT_STYLES)
        actual_generator = ACCOMPANIMENT_MAP.get(selected_style_name)

        if not actual_generator:
            raise ValueError(f"伴奏スタイル '{selected_style_name}' は定義されていません。")

        self.logger.info(f"使用する伴奏スタイル: {selected_style_name}")

        full_accompaniment_data = []
        current_accomp_time = 0
        for chord_name in config.chord_progression:
            measure_accomp_notes = actual_generator(chord_name, ticks_per_measure, config.key, scale)
            for note in measure_accomp_notes:
                note['time'] += current_accomp_time
                full_accompaniment_data.append(note)
            current_accomp_time += ticks_per_measure
        return full_accompaniment_data

class MelodyGenerator:
    """
    メロディー生成に関する状態と振る舞いを一元管理するクラス。
    GUIや他のクライアントコードから「部品」として利用されることを想定しています。
    """

    def __init__(self, config: MelodyConfig, logger=None):
        """
        コンストラクタ。メロディー生成に必要な設定オブジェクトを受け取ります。

        Args:
            config (MelodyConfig): 設定を保持するデータクラスのインスタンス。
            logger (logging.Logger, optional): ログ出力用のロガー。
                                               指定されない場合、標準出力にフォールバックします。
        """
        # --- ロガーの設定 ---
        self.logger = logger or logging.getLogger(__name__)
        # --- 設定の保持 ---
        self.config = config

        # --- 生成結果の初期化 ---
        self.melody_data = None
        self.accompaniment_data = None

    def generate(self):
        """
        保持している設定に基づき、メロディーと伴奏の内部データを生成します。
        """
        self.logger.info(f"--- メロディー生成を開始します ({self.config.num_measures}小節) ---")

        # 1. 準備
        scale = SCALES[self.config.key]
        ticks_per_measure = self.config.ticks_per_beat * self.config.beats_per_measure

        # 2. メロディーと伴奏の生成
        # メロディー生成をMelodyProcessorに委譲
        melody_processor = MelodyProcessor(logger=self.logger)
        self.melody_data = melody_processor.process(self.config)

        # 伴奏生成をAccompanimentProcessorに委譲
        accompaniment_processor = AccompanimentProcessor(logger=self.logger)
        self.accompaniment_data = accompaniment_processor.process(self.config, scale, ticks_per_measure)

        self.logger.info("\nメロディーと伴奏の内部データ生成が完了しました。")

    def save_midi(self, output_path):
        """
        生成済みのメロディーデータをMIDIファイルとして保存します。
        """
        if self.melody_data is None:
            raise RuntimeError("メロディーがまだ生成されていません。先に .generate() を呼び出してください。")

        create_midi_file(
            melody_data=self.melody_data,
            output_filename=output_path,
            ticks_per_beat=self.config.ticks_per_beat,
            accompaniment_data=self.accompaniment_data
        )
        self.logger.info(f"MIDIファイル '{output_path}' を保存しました。")