"""
変換操作を組み合わせてメロディー全体の構成を作る「生成戦略」のカタログ。
"""
import random
from music_theory import SCALES
from transformations import (
    transform_identity, transform_retrograde, transform_ending,
    transform_rhythm_staccato, transform_rhythm_double_time
)

def strategy_random_choice(motif_notes, key, num_measures=4, ticks_per_beat=480):
    """
    生成戦略B: 変換操作をランダムに組み合わせて指定された小節数のメロディーを生成する。
    - 1小節目: 提示 (そのまま)
    - 中間: 展開 (ランダム)
    - 最終小節: 解決 (主音で終わる)

    Args:
        motif_notes (list): モチーフとなるMIDIノート番号のリスト。
        key (str): 使用するキー。
        num_measures (int): 生成する合計小節数。
        ticks_per_beat (int): 1拍あたりのティック数。
    """
    if key not in SCALES:
        raise ValueError(f"キー '{key}' は定義されていません。利用可能なキー: {list(SCALES.keys())}")
    if num_measures < 2:
        raise ValueError("生成する小節数は2以上である必要があります。")

    scale = SCALES[key]

    # 展開に利用する変換操作のリスト
    development_transforms = [
        transform_identity,
        transform_retrograde,
        # リズム系の変換操作を追加
        transform_rhythm_staccato,
        transform_rhythm_double_time,
    ]

    # 指定された小節数で構成を動的に定義
    composition = []
    # 1小節目: 提示
    composition.append(transform_identity)

    # 2小節目から (N-1)小節目: 展開
    # num_measures - 2 は、最初と最後の小節を除いた展開部分の小節数
    for _ in range(num_measures - 2):
        composition.append(random.choice(development_transforms))

    # 最終小節: 解決
    composition.append(transform_ending)

    full_melody_data = []
    current_time = 0
    # 1小節の長さを、モチーフの音数 x 1拍のティック数 と仮定
    ticks_per_measure = len(motif_notes) * ticks_per_beat

    print("今回のメロディー構成:")
    for i, transform_func in enumerate(composition):
        print(f"  - {i+1}小節目: {transform_func.__name__}")
        # 変換操作を呼び出して1小節分のメロディーを生成
        measure_data = transform_func(motif_notes, key, scale, ticks_per_beat)

        # 小節の開始時間に合わせて、各音符の時間を調整して追加
        for note in measure_data:
            note['time'] += current_time
            full_melody_data.append(note)
        current_time += ticks_per_measure

    return full_melody_data