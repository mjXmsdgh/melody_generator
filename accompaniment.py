from music_theory import CHORDS

def generate_block_chords(chord_name, ticks_per_measure, key, scale):
    """
    指定されたコードを全音符（ベタ打ち）で演奏する音符データを生成します。

    Args:
        chord_name (str): コード名 (例: 'C', 'Am')。
        ticks_per_measure (int): 1小節のティック数。
        key (str): 曲のキー（この関数では未使用）。
        scale (list): 曲のスケール（この関数では未使用）。

    Returns:
        list: 1小節分の音符データのリスト。
    """
    notes_data = []
    chord_notes = CHORDS.get(chord_name)

    if chord_notes:
        for pitch in chord_notes:
            notes_data.append({
                'pitch': pitch - 12,  # 1オクターブ下げる
                'time': 0,            # 小節の頭から
                'duration': ticks_per_measure
            })
    return notes_data

def generate_arpeggio_up(chord_name, ticks_per_measure, key, scale):
    """
    指定されたコードで、シンプルな上昇アルペジオ（四分音符）を生成します。
    パターン: ルート -> 3度 -> 5度 -> オクターブ上のルート

    Args:
        chord_name (str): コード名 (例: 'C', 'Am')。
        ticks_per_measure (int): 1小節のティック数。
        key (str): 曲のキー（この関数では未使用）。
        scale (list): 曲のスケール（この関数では未使用）。

    Returns:
        list: 1小節分の音符データのリスト。
    """
    notes_data = []
    chord_notes = CHORDS.get(chord_name)

    if chord_notes and len(chord_notes) >= 3:
        # 4/4拍子を想定し、四分音符の長さを計算
        ticks_per_beat = ticks_per_measure // 4

        # アルペジオのパターンを定義
        # ルート、3度、5度、オクターブ上のルート
        pattern_pitches = [
            chord_notes[0] - 12,  # ルート (1オクターブ下)
            chord_notes[1] - 12,  # 3度 (1オクターブ下)
            chord_notes[2] - 12,  # 5度 (1オクターブ下)
            chord_notes[0]        # ルート (元の高さ)
        ]

        for i, pitch in enumerate(pattern_pitches):
            notes_data.append({
                'pitch': pitch,
                'time': i * ticks_per_beat, # 各拍の頭から開始
                'duration': ticks_per_beat
            })
    return notes_data