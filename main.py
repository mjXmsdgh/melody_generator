from strategies import strategy_chord_progression
from midi_utils import create_midi_file
from transformations import add_passing_notes
from music_theory import SCALES
import config

# このファイルがプログラムの実行起点となります。
# 今後、他のファイルは直接実行せず、この main.py を実行してください。

def main():
    """
    設定ファイルに基づいてメロディーを生成し、MIDIファイルとして出力します。
    """
    # 1. メロディー生成を実行
    print(f"--- メロディー生成を開始します ({config.NUMBER_OF_MEASURES}小節) ---")
    generated_melody = strategy_chord_progression(
        motif_notes=config.INPUT_MOTIF,
        key=config.INPUT_KEY,
        chord_progression=config.INPUT_CHORD_PROGRESSION,
        num_measures=config.NUMBER_OF_MEASURES
    )

    # 2. (オプション) 経過音を追加する後処理
    if config.USE_PASSING_NOTES:
        print("\n--- 経過音を追加します ---")
        final_melody = add_passing_notes(
            melody_data=generated_melody,
            scale=SCALES[config.INPUT_KEY],
            ticks_per_beat=config.TICKS_PER_BEAT
        )
    else:
        final_melody = generated_melody

    # 3. 生成されたメロディーデータをコンソールに表示
    print("\n--- 生成されたメロディーデータ (pitch, time, duration) ---")
    for note in final_melody:
        print(f"  {note}")

    # 4. 生成されたメロディーをMIDIファイルに出力
    create_midi_file(
        melody_data=final_melody,
        output_filename=config.OUTPUT_PATH,
        chord_progression=config.INPUT_CHORD_PROGRESSION if config.PLAY_CHORDS else None,
        beats_per_measure=config.BEATS_PER_MEASURE
    )
    print(f"\nMIDIファイル '{config.OUTPUT_PATH}' を生成しました。")


if __name__ == "__main__":
    main()