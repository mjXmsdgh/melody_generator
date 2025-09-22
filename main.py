from strategies import strategy_random_choice
from midi_utils import create_midi_file

# このファイルがプログラムの実行起点となります。
# 今後、他のファイルは直接実行せず、この main.py を実行してください。

def main():
    """
    メイン処理
    """
    # 1. 生成に使用するパラメータを設定
    input_motif = [64, 62, 60]  # モチーフ: ドレミ (C4, D4, E4)
    input_key = 'C_major'
    number_of_measures = 8      # 生成する小節数

    # 2. メロディー生成を実行
    print(f"--- メロディー生成を開始します ({number_of_measures}小節) ---")
    generated_melody = strategy_random_choice(
        motif_notes=input_motif,
        key=input_key,
        num_measures=number_of_measures
    )

    # 3. 生成されたメロディーをMIDIファイルに出力
    output_path = "C:\\Users\\masuda\\Desktop\\DTM\\strategy_random_output.mid"
    create_midi_file(generated_melody, output_path)
    print(f"\nMIDIファイル '{output_path}' を生成しました。")


if __name__ == "__main__":
    main()