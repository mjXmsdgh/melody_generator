from dataclasses import dataclass
from typing import List, Tuple

from .music_theory import SCALES

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