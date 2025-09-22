"""
メロディーを1小節単位で加工する「変換操作」のカタログ。
"""
from music_theory import snap_to_scale

# 各変換操作は、モチーフを受け取り、「1小節分」のメロディーデータを返すことを想定しています。
# 返されるデータ内の 'time' は、その小節の先頭を0とした相対時間です。

def transform_identity(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをそのまま演奏する。
    """
    measure_data = []
    current_time = 0
    # ここでは、モチーフ内の各音符を1拍の長さと仮定します。
    note_duration = ticks_per_beat
    for pitch in motif_notes:
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration
    return measure_data

def transform_retrograde(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフを逆行させる（音の順番を逆にする）。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat
    # モチーフの音の並びを逆順にする
    reversed_notes = motif_notes[::-1]
    for pitch in reversed_notes:
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration
    return measure_data

def transform_ending(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフを演奏し、最後を主音で解決させる。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat
    tonic = scale[0]

    for i, pitch in enumerate(motif_notes):
        final_pitch = pitch
        if i == len(motif_notes) - 1:  # モチーフの最後の音の場合
            # 元の音に近いオクターブの主音に補正
            final_pitch = snap_to_scale(tonic, [pitch])
        measure_data.append({'pitch': final_pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration
    return measure_data