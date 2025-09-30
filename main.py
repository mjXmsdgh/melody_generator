from strategies import strategy_chord_progression
from midi_utils import create_midi_file
from music_theory import SCALES
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
    設定ファイルに基づいてメロディーを生成し、MIDIファイルとして出力します。
    """
    # 1. メロディー生成を実行
    print(f"--- メロディー生成を開始します ({num_measures}小節) ---")
    generated_melody = strategy_chord_progression(
        motif_notes=motif_notes,
        key=key,
        chord_progression=chord_progression,
        num_measures=num_measures
    )

    # 2. 生成されたメロディーデータをコンソールに表示
    print("\n--- 生成されたメロディーデータ (pitch, time, duration) ---")
    for note in generated_melody:
        print(f"  {note}")

    # 3. 生成されたメロディーをMIDIファイルに出力
    create_midi_file(
        melody_data=generated_melody,
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