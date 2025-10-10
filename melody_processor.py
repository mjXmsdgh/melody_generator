import logging
from typing import List

from melody_config import MelodyConfig
from strategies import strategy_chord_progression
from music_theory import SCALES, CHORDS, snap_to_chord
from transformations import transform_add_passing_notes

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