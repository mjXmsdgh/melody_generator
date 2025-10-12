"""
変換操作を組み合わせてメロディー全体の構成を作る「生成戦略」のカタログ。
"""
import random
from .music_theory import SCALES, CHORDS, snap_to_chord
from .transformations import (
    transform_identity, transform_retrograde, transform_ending, transform_rhythm_dotted, transform_add_passing_notes,
    transform_rhythm_triplet, transform_slight_variation,
    transform_rhythm_staccato, transform_rhythm_double_time, transform_syncopation_push,
    transform_syncopation_pull, transform_transpose_up, transform_transpose_down
)

def strategy_random_choice(num_measures=4):
    """
    生成戦略: 変換操作をランダムに組み合わせて構成レシピを生成する。
    - 1小節目: 提示
    - 中間: 展開
    - 最終小節: 解決
    """
    if num_measures < 2:
        raise ValueError("生成する小節数は2以上である必要があります。")

    # 展開に利用する変換操作のリスト
    development_transforms = [
        transform_retrograde,
        transform_rhythm_staccato,
        transform_rhythm_double_time,
        transform_rhythm_dotted,
        transform_rhythm_triplet,
        transform_syncopation_push,
        transform_syncopation_pull,
        transform_transpose_up,
        transform_transpose_down,
    ]

    # 指定された小節数で構成を動的に定義
    composition = []
    composition.append([transform_identity])
    for _ in range(num_measures - 2):
        composition.append([random.choice(development_transforms)])
    composition.append([transform_ending])

    return composition

def strategy_chord_progression(num_measures=8):
    """
    生成戦略: AA'BA''形式で、コード進行に沿ったメロディーを生成するための構成レシピを返す。
    """

    # --- フィルタのカタログを定義 ---
    development_transforms = [
        transform_transpose_up,
        transform_transpose_down,
        transform_rhythm_staccato,
        transform_rhythm_dotted,
        transform_rhythm_triplet,
    ]
    subtle_transforms = [
        transform_slight_variation,
        transform_add_passing_notes,
    ]
    
    if num_measures != 8:
        raise ValueError(f"AABA形式は現在8小節でのみサポートされています。num_measuresを8に設定してください。")

    # --- 構成（フィルタのレシピ）を AA'BA'' 形式でランダムに決定 ---
    composition = []
    # Aセクション (1-2小節): a - a'
    composition.append([transform_identity])
    composition.append([random.choice(subtle_transforms)])
    # A'セクション (3-4小節): a - a'' (a'とは別のバリエーション)
    composition.append([transform_identity])
    composition.append([random.choice(subtle_transforms)])
    # Bセクション (5-6小節) - 展開（フィルタチェーンを生成）
    # 1つまたは2つのフィルタをランダムに組み合わせる
    b1_chain = random.sample(development_transforms, k=random.randint(1, 2))
    b2_chain = random.sample(development_transforms, k=random.randint(1, 2))
    composition.append(b1_chain)
    composition.append(b2_chain)
    # A''セクション (7-8小節) - 再現と解決
    composition.append([transform_identity])
    composition.append([transform_ending])

    return composition