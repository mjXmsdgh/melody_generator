import accompaniment

# --- メロディー生成に関する設定 ---

# 1拍あたりのTick数。分解能を表します。480が一般的です。
TICKS_PER_BEAT = 480

# 1小節あたりの拍数
BEATS_PER_MEASURE = 4

# 生成するキー
INPUT_KEY = 'C_major'

# 生成する小節数
NUMBER_OF_MEASURES = 8

# --- モチーフとコード進行 ---

# メロディーの元となるモチーフ
# 形式: [(MIDIノート番号, 継続時間(ticks)), ...]
# 例：ド（C4、四分音符）、レ（D4、八分音符）、ミ（E4、四分音符）
INPUT_MOTIF = [
    (76, 480),      # E5 (元の64 + 12)
    (74, 240),      # D5 (元の62 + 12)
    (72, 480+240),  # C5 (元の60 + 12)
    (74, 480)       # D5 (元の62 + 12)
]

# 使用するコード進行 (8小節分)
# ポップスでよく使われる「カノン進行」を少しアレンジしたものです
INPUT_CHORD_PROGRESSION = [
    'C', 'G', 'Am', 'Em',
    'F', 'C', 'F',  'G'
]

# --- 生成オプション ---

# 伴奏コードをMIDIファイルに含めるか
PLAY_CHORDS = True

# 使用する伴奏の生成スタイルを選択
# accompaniment.generate_block_chords や accompaniment.generate_arpeggio_up などを指定
ACCOMPANIMENT_GENERATOR = accompaniment.generate_arpeggio_up

# --- 出力設定 ---
OUTPUT_PATH = "C:\\Users\\masuda\\Desktop\\DTM\\strategy_random_output.mid"