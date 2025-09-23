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

def transform_rhythm_staccato(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を「8分音符 + 8分休符」のスタッカートにする。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat // 2  # 8分音符の長さ

    for pitch in motif_notes:
        # 8分音符を追加
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': note_duration})
        # 1拍分の時間を進める (8分音符 + 8分休符)
        current_time += ticks_per_beat
    return measure_data

def transform_rhythm_double_time(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を半分の長さの音符2つに分割する（倍速化）。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat // 2  # 8分音符の長さ

    for pitch in motif_notes:
        # 1つ目の8分音符
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration
        # 2つ目の8分音符
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration
    return measure_data

def transform_syncopation_push(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を8分音符分「前」にずらす（食い気味のシンコペーション）。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat
    push_amount = ticks_per_beat // 2  # 8分音符分ずらす

    for pitch in motif_notes:
        # 8分音符分、前にずらす。ただし小節の頭(time=0)より前には行かない。
        start_time = max(0, current_time - push_amount)
        measure_data.append({'pitch': pitch, 'time': start_time, 'duration': note_duration})
        # 時間の進行は本来の1拍ごと
        current_time += ticks_per_beat
    return measure_data

def transform_syncopation_pull(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を8分音符分「後」にずらす（もたらせるシンコペーション）。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat
    pull_amount = ticks_per_beat // 2  # 8分音符分ずらす
    measure_duration = len(motif_notes) * ticks_per_beat # この小節の想定される長さ

    for pitch in motif_notes:
        start_time = current_time + pull_amount
        # 小節の長さを超えないように音符の長さを調整
        adjusted_duration = note_duration
        if start_time + adjusted_duration > measure_duration:
            adjusted_duration = max(0, measure_duration - start_time)

        if adjusted_duration > 0:
            measure_data.append({'pitch': pitch, 'time': start_time, 'duration': adjusted_duration})
        # 時間の進行は本来の1拍ごと
        current_time += ticks_per_beat
    return measure_data

def transform_transpose_up(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをスケールに沿って2音上に移高する。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat

    for pitch in motif_notes:
        # 元の音からだいたい全音(2)分高い音をターゲットにし、スケールに最も近い音に補正
        transposed_pitch = snap_to_scale(pitch + 2, scale)
        measure_data.append({'pitch': transposed_pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration
    return measure_data

def transform_transpose_down(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをスケールに沿って2音下に移高する。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat

    for pitch in motif_notes:
        # 元の音からだいたい全音(2)分低い音をターゲットにし、スケールに最も近い音に補正
        transposed_pitch = snap_to_scale(pitch - 2, scale)
        measure_data.append({'pitch': transposed_pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration
    return measure_data