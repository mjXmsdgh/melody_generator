from .music_theory import CHORDS

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

def generate_alberti_bass(chord_name, ticks_per_measure, key, scale):
    """
    指定されたコードで、アルベルティ・バス（16分音符）を生成します。
    パターン: ルート -> 5度 -> 3度 -> 5度 を繰り返します。

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
        # 4/4拍子を想定し、16分音符の長さを計算
        ticks_per_16th = ticks_per_measure // 16

        # アルベルティ・バスのパターン (ルート, 5度, 3度, 5度)
        # 低い音域で演奏するため、1オクターブ下げる
        pattern_pitches = [
            chord_notes[0] - 12,  # ルート
            chord_notes[2] - 12,  # 5度
            chord_notes[1] - 12,  # 3度
            chord_notes[2] - 12,  # 5度
        ]

        # 1小節にパターンを4回繰り返す (16分音符 x 4 x 4 = 1小節)
        for i in range(16):
            pitch = pattern_pitches[i % 4]
            notes_data.append({
                'pitch': pitch,
                'time': i * ticks_per_16th,
                'duration': ticks_per_16th
            })
    return notes_data

# --- 伴奏スタイルのカタログ ---

# 利用可能な伴奏生成関数を、名前（文字列）と関数オブジェクトの辞書としてマッピングします。
# これにより、設定ファイルから文字列でスタイルを指定できるようになります。
ACCOMPANIMENT_MAP = {
    'block_chords': generate_block_chords,
    'arpeggio_up': generate_arpeggio_up,
    'alberti_bass': generate_alberti_bass,
}

# ランダム選択のために、利用可能なスタイル名のリストも用意します。
ACCOMPANIMENT_STYLES = list(ACCOMPANIMENT_MAP.keys())