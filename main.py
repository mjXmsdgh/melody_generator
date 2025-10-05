import config
from generator import MelodyGenerator

# このファイルがプログラムの実行起点となります。
# 今後、他のファイルは直接実行せず、この main.py を実行してください。

def main():
    """プログラムの実行を管理する司令塔。"""
    # 1. config.pyから設定を読み込み、辞書にまとめる
    app_config = {
        'motif_notes': config.INPUT_MOTIF,
        'key': config.INPUT_KEY,
        'chord_progression': config.INPUT_CHORD_PROGRESSION,
        'num_measures': config.NUMBER_OF_MEASURES,
        'ticks_per_beat': config.TICKS_PER_BEAT,
        'beats_per_measure': config.BEATS_PER_MEASURE,
        'play_chords': config.PLAY_CHORDS,
        'accompaniment_generator': config.ACCOMPANIMENT_GENERATOR,
    }

    # 2. MelodyGeneratorのインスタンスを生成
    generator = MelodyGenerator(config=app_config)

    # 3. メロディーを生成 (内部データが作成される)
    generator.generate()

    # 4. MIDIファイルとして保存
    generator.save_midi(config.OUTPUT_PATH)


if __name__ == "__main__":
    main()