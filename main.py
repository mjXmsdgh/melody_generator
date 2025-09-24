from strategies import strategy_random_choice
from midi_utils import create_midi_file

# このファイルがプログラムの実行起点となります。
# 今後、他のファイルは直接実行せず、この main.py を実行してください。

def main():
    """
    メイン処理
    """
    # 1. 生成に使用するパラメータを設定
    # モチーフ：[(MIDIノート番号, 継続時間(ticks)), ...]
    # 例：ド（C4、四分音符）、レ（D4、八分音符）、ミ（E4、四分音符）
    input_motif = [(64, 1920//4), (62, 1920//4), (60, 1920//4),(62,1920//4)]

    input_key = 'C_major'
    number_of_measures = 8      # 生成する小節数

    # 2. メロディー生成を実行
    print(f"--- メロディー生成を開始します ({number_of_measures}小節) ---")
    generated_melody = strategy_random_choice(
        motif_notes=input_motif,
        key=input_key,
        num_measures=number_of_measures
    )

    # 3. 生成されたメロディーデータを確認
    print("\n--- 生成されたメロディーデータ (pitch, time, duration) ---")
    for note in generated_melody:
        print(f"  {note}")

    # 4. 生成されたメロディーをMIDIファイルに出力
    output_path = "C:\\Users\\masuda\\Desktop\\DTM\\strategy_random_output.mid"
    create_midi_file(generated_melody, output_path)
    print(f"\nMIDIファイル '{output_path}' を生成しました。")


if __name__ == "__main__":
    main()