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