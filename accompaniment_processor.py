import random
import logging
from typing import List

from melody_config import MelodyConfig
from accompaniment import ACCOMPANIMENT_MAP, ACCOMPANIMENT_STYLES

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

        # コード進行をループし、各小節の伴奏を生成して結合する
        full_accompaniment_data = []
        current_accomp_time = 0
        for chord_name in config.chord_progression:
            measure_accomp_notes = actual_generator(chord_name, ticks_per_measure, config.key, scale)
            for note in measure_accomp_notes:
                note['time'] += current_accomp_time
                full_accompaniment_data.append(note)
            current_accomp_time += ticks_per_measure
        return full_accompaniment_data