from strategies import strategy_chord_progression
from midi_utils import create_midi_file
from music_theory import SCALES, CHORDS, snap_to_chord
import config

# このファイルがプログラムの実行起点となります。
# 今後、他のファイルは直接実行せず、この main.py を実行してください。

def generate_and_save_melody(
    motif_notes,
    key,
    chord_progression,
    num_measures,
    ticks_per_beat,
    output_path,
    play_chords,
    beats_per_measure
):
    """
    設定に基づき、Arrangerから構成レシピを取得し、Processorとしてメロディーを生成・保存します。
    """
    print(f"--- メロディー生成を開始します ({num_measures}小節) ---")
    if key not in SCALES:
        raise ValueError(f"キー '{key}' は定義されていません。利用可能なキー: {list(SCALES.keys())}")
    if len(chord_progression) < num_measures:
        raise ValueError("コード進行の長さが、生成する小節数より短いです。")

    # --- Processor (処理エンジン) の実装 ---

    # 1. Arrangerを呼び出し、曲の構成レシピを取得
    composition = strategy_chord_progression(num_measures=num_measures)

    # 2. 元のMotifを、フィルタが扱える初期データ形式に変換
    base_measure_data = []
    current_motif_time = 0
    for pitch, duration in motif_notes:
        base_measure_data.append({'pitch': pitch, 'time': current_motif_time, 'duration': duration})
        current_motif_time += duration

    # 3. 各小節について、レシピに従いメロディーを生成
    full_melody_data = []
    current_total_time = 0
    ticks_per_measure = ticks_per_beat * beats_per_measure
    scale = SCALES[key]

    print("今回のメロディー構成:")
    for i, filter_chain in enumerate(composition):
        # 3a. フィルタチェーンを順番に適用 (副作用を防ぐため、毎回深いコピーを作成)
        processed_data = [note.copy() for note in base_measure_data]
        for transform_func in filter_chain:
            processed_data = transform_func(processed_data, key, scale, ticks_per_beat)

        # 3b. コード進行に合わせて音を補正 (ハーモニー・フィルタ)
        current_chord_name = chord_progression[i]
        chord_notes = CHORDS.get(current_chord_name)
        chain_names = ' -> '.join([f.__name__ for f in filter_chain])
        print(f"  - {i+1}小節目: {chain_names} (コード: {current_chord_name})")
        if chord_notes:
            for note in processed_data:
                note['pitch'] = snap_to_chord(note['pitch'], chord_notes)

        # 3c. 全体のメロディーに結合
        for note in processed_data:
            note['time'] += current_total_time
            full_melody_data.append(note)
        current_total_time += ticks_per_measure

    # 4. 生成されたメロディーをMIDIファイルに出力
    # (midi_utils側で時間順ソートは行われる)
    create_midi_file(
        melody_data=full_melody_data,
        output_filename=output_path,
        chord_progression=chord_progression if play_chords else None,
        beats_per_measure=beats_per_measure
    )
    print(f"\nMIDIファイル '{output_path}' を生成しました。")

def main():
    """プログラムの実行を管理する司令塔。"""
    generate_and_save_melody(
        motif_notes=config.INPUT_MOTIF,
        key=config.INPUT_KEY,
        chord_progression=config.INPUT_CHORD_PROGRESSION,
        num_measures=config.NUMBER_OF_MEASURES,
        ticks_per_beat=config.TICKS_PER_BEAT,
        output_path=config.OUTPUT_PATH,
        play_chords=config.PLAY_CHORDS,
        beats_per_measure=config.BEATS_PER_MEASURE,
    )


if __name__ == "__main__":
    main()