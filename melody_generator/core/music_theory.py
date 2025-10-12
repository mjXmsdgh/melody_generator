"""
音楽理論に関する定義とヘルパー関数をまとめたモジュール。
"""

# 主要なキーのスケール（音階）をMIDIノート番号で定義します。
# リストの最初の音（例: C_majorの60）がそのキーの主音（トニック）です。
SCALES = {
    'C_major': [60, 62, 64, 65, 67, 69, 71],  # ハ長調
    'G_major': [55, 57, 59, 60, 62, 64, 66],  # ト長調
    'D_major': [62, 64, 66, 67, 69, 71, 73],  # ニ長調
    'A_minor': [57, 59, 60, 62, 64, 65, 67],  # イ短調 (自然的短音階)
}

# Cメジャーキーでよく使われるコードの構成音を定義します。
# ルート音(根音)を基準とした相対的な音程ではなく、MIDIノート番号で直接定義します。
CHORDS = {
    # ダイアトニックコード
    'C':    [60, 64, 67],  # ド, ミ, ソ (I)
    'Dm':   [62, 65, 69],  # レ, ファ, ラ (ii)
    'Em':   [64, 67, 71],  # ミ, ソ, シ (iii)
    'F':    [65, 69, 72],  # ファ, ラ, ド (IV)
    'G':    [67, 71, 74],  # ソ, シ, レ (V)
    'Am':   [69, 72, 76],  # ラ, ド, ミ (vi)
    # セカンダリ・ドミナントなど
    'G7':   [67, 71, 74, 78], # ソ, シ, レ, ファ (V7)
}

def snap_to_scale(pitch, scale_notes):
    """指定された音(pitch)を、スケール内で最も近い音に補正するヘルパー関数。"""
    min_dist = float('inf')
    best_pitch = pitch
    # 複数のオクターブにまたがって最も近い音を探す
    for scale_note_base in scale_notes:
        for oct_offset in range(-2, 3):
            current_scale_note = scale_note_base + 12 * oct_offset
            dist = abs(pitch - current_scale_note)
            if dist < min_dist:
                min_dist = dist
                best_pitch = current_scale_note
    return best_pitch

def snap_to_chord(pitch, chord_notes):
    """指定された音(pitch)を、コード構成音(chord_notes)の中で最も近い音に補正するヘルパー関数。"""
    if not chord_notes:
        return pitch

    min_dist = float('inf')
    best_pitch = pitch
    for chord_note_base in chord_notes:
        for oct_offset in range(-2, 3):
            current_chord_note = chord_note_base + 12 * oct_offset
            dist = abs(pitch - current_chord_note)
            if dist < min_dist:
                min_dist = dist
                best_pitch = current_chord_note
    return best_pitch