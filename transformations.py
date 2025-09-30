"""
メロディーを1小節単位で加工する「変換操作」のカタログ。
"""
from music_theory import snap_to_scale
import random

# 各変換操作は、モチーフを受け取り、「1小節分」のメロディーデータを返すことを想定しています。
# 返されるデータ内の 'time' は、その小節の先頭を0とした相対時間です。

def transform_identity(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをそのまま演奏する。
    """
    measure_data = []
    current_time = 0
    for note in motif_notes:
        pitch, duration = note
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': duration})
        current_time += duration
    return measure_data

def transform_retrograde(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフを逆行させる（音の順番を逆にする）。
    """
    measure_data = []
    current_time = 0
    # モチーフの音の並びを逆順にする
    reversed_notes = motif_notes[::-1]
    for note in reversed_notes:
        pitch, duration = note
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': duration})
        current_time += duration
    return measure_data

def transform_ending(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフを演奏し、最後を主音で解決させる。
    """
    measure_data = []
    current_time = 0
    tonic = scale[0]

    for i, note in enumerate(motif_notes):
        pitch, duration = note
        final_pitch = pitch
        if i == len(motif_notes) - 1:  # モチーフの最後の音の場合
            # 元の音に近いオクターブの主音に補正
            final_pitch = snap_to_scale(tonic, [pitch])
        measure_data.append({'pitch': final_pitch, 'time': current_time, 'duration': duration})
        current_time += duration
    return measure_data

def transform_rhythm_staccato(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を「8分音符 + 8分休符」のスタッカートにする。
    """
    measure_data = []
    current_time = 0
    note_duration = ticks_per_beat // 2  # 8分音符の長さ

    for pitch, duration in motif_notes:
        # 8分音符を追加
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': note_duration})
        # 元の音符の長さだけ時間を進める (8分音符 + 残りの休符)
        current_time += duration
    return measure_data

def transform_rhythm_double_time(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を半分の長さの音符2つに分割する（倍速化）。
    """
    measure_data = []
    current_time = 0

    for pitch, duration in motif_notes:
        half_duration = duration // 2
        # 1つ目の8分音符
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': half_duration})
        current_time += half_duration
        # 2つ目の8分音符
        measure_data.append({'pitch': pitch, 'time': current_time, 'duration': half_duration})
        current_time += half_duration
    return measure_data

def transform_syncopation_push(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を8分音符分「前」にずらす（食い気味のシンコペーション）。
    """
    measure_data = []
    current_time = 0
    push_amount = ticks_per_beat // 2  # 8分音符分ずらす

    for note in motif_notes:
        pitch, duration = note
        # 8分音符分、前にずらす。ただし小節の頭(time=0)より前には行かない。
        start_time = max(0, current_time - push_amount)
        measure_data.append({'pitch': pitch, 'time': start_time, 'duration': duration})
        # 次の音符の基準位置を更新
        current_time += duration
    return measure_data

def transform_syncopation_pull(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を8分音符分「後」にずらす（もたらせるシンコペーション）。
    """
    measure_data = []
    current_time = 0
    pull_amount = ticks_per_beat // 2  # 8分音符分ずらす
    # 1小節の長さを、モチーフの音符の長さの合計から計算する
    measure_duration = sum(duration for _, duration in motif_notes)

    for note in motif_notes:
        pitch, duration = note
        start_time = current_time + pull_amount

        # 小節の長さを超えないように音符の長さを調整
        adjusted_duration = duration
        if start_time + adjusted_duration > measure_duration:
            adjusted_duration = max(0, measure_duration - start_time)

        if adjusted_duration > 0:
            measure_data.append({'pitch': pitch, 'time': start_time, 'duration': adjusted_duration})
        # 次の音符の基準位置を更新
        current_time += duration
    return measure_data

def transform_transpose_up(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをスケールに沿って2音上に移高する。
    """
    measure_data = []
    current_time = 0

    for pitch, duration in motif_notes:
        # 元の音からだいたい全音(2)分高い音をターゲットにし、スケールに最も近い音に補正
        transposed_pitch = snap_to_scale(pitch + 2, scale)
        measure_data.append({'pitch': transposed_pitch, 'time': current_time, 'duration': duration})
        current_time += duration
    return measure_data

def transform_transpose_down(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをスケールに沿って2音下に移高する。
    """
    measure_data = []
    current_time = 0

    for pitch, duration in motif_notes:
        # 元の音からだいたい全音(2)分低い音をターゲットにし、スケールに最も近い音に補正
        transposed_pitch = snap_to_scale(pitch - 2, scale)
        measure_data.append({'pitch': transposed_pitch, 'time': current_time, 'duration': duration})
        current_time += duration
    return measure_data

def transform_rhythm_dotted(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を「付点8分音符 + 16分音符」のリズムパターンに変換する。
    元の音符1つが、同じピッチの2つの音符（タータ）に置き換わります。
    """
    measure_data = []
    current_time = 0
    dotted_eighth_duration = int(ticks_per_beat * 0.75)  # 付点8分音符
    sixteenth_duration = int(ticks_per_beat * 0.25)      # 16分音符

    for pitch, duration in motif_notes:
        # 元の音符の長さが1拍以上の場合に適用
        if duration >= ticks_per_beat:
            num_beats = duration // ticks_per_beat
            for _ in range(num_beats):
                measure_data.append({'pitch': pitch, 'time': current_time, 'duration': dotted_eighth_duration})
                current_time += dotted_eighth_duration
                measure_data.append({'pitch': pitch, 'time': current_time, 'duration': sixteenth_duration})
                current_time += sixteenth_duration
        else: # 1拍未満の音符はそのまま
            measure_data.append({'pitch': pitch, 'time': current_time, 'duration': duration})
            current_time += duration
    return measure_data

def transform_rhythm_triplet(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフ内の長い音符(1拍以上)をランダムに1つ選び、8分音符の3連符に変換する。
    """
    measure_data = []
    current_time = 0
    triplet_duration = ticks_per_beat // 3 # 1拍を3分割した長さ

    # 1. 1拍以上の長い音符のインデックスをリストアップ
    long_note_indices = [i for i, (pitch, duration) in enumerate(motif_notes) if duration >= ticks_per_beat]

    # 2. 変換対象の音符をランダムに1つ選ぶ
    note_to_transform_index = random.choice(long_note_indices) if long_note_indices else -1

    # 3. モチーフを処理
    for i, (pitch, duration) in enumerate(motif_notes):
        if i == note_to_transform_index:
            # 選ばれた音符を3連符に変換
            num_beats = duration // ticks_per_beat
            for _ in range(num_beats):
                for _ in range(3):
                    measure_data.append({'pitch': pitch, 'time': current_time, 'duration': triplet_duration})
                    current_time += triplet_duration
        else:
            # それ以外の音符はそのまま追加
            measure_data.append({'pitch': pitch, 'time': current_time, 'duration': duration})
            current_time += duration
    return measure_data

def transform_add_passing_notes(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフ内の音符間に経過音を挿入する。
    音符間に3度以上の跳躍があり、かつ十分な休符がある場合に、間のスケール音を16分音符で埋める。
    """
    if not motif_notes:
        return []

    # まず、モチーフを基本的なメロディーデータに変換
    base_measure_data = []
    current_time = 0
    for pitch, duration in motif_notes:
        base_measure_data.append({'pitch': pitch, 'time': current_time, 'duration': duration})
        current_time += duration

    # 経過音を追加するロジック
    new_measure_data = [base_measure_data[0]] # 最初の音符は必ず追加
    passing_note_duration = ticks_per_beat // 4  # 16分音符

    for i in range(1, len(base_measure_data)):
        # 処理済みの最後の音符と、現在の音符を取得
        prev_note = new_measure_data[-1]
        current_note = base_measure_data[i]

        # 2つの音符間の時間的な隙間（休符）を計算
        gap = current_note['time'] - (prev_note['time'] + prev_note['duration'])

        # 音程が3度以上離れていて(MIDIノート番号で3以上)、16分音符以上の隙間があるか
        if abs(current_note['pitch'] - prev_note['pitch']) >= 3 and gap >= passing_note_duration:
            step = 1 if current_note['pitch'] > prev_note['pitch'] else -1
            passing_pitch_candidate = prev_note['pitch'] + step
            passing_pitch = snap_to_scale(passing_pitch_candidate, scale)

            passing_note_time = prev_note['time'] + prev_note['duration']
            new_measure_data.append({'pitch': passing_pitch, 'time': passing_note_time, 'duration': passing_note_duration})

        new_measure_data.append(current_note)

    return new_measure_data

def transform_slight_variation(motif_notes, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフの最後の音をスケールに沿って1音上または下にずらす。
    Aセクション内のマイナーチェンジ(a -> a')を表現するために使用する。
    """
    measure_data = []
    current_time = 0

    if not motif_notes:
        return []

    for i, note in enumerate(motif_notes):
        pitch, duration = note
        final_pitch = pitch
        if i == len(motif_notes) - 1:  # モチーフの最後の音の場合
            # スケールに沿って1音上か下にランダムでずらす
            direction = random.choice([-1, 1])
            final_pitch = snap_to_scale(pitch + direction, scale)
        measure_data.append({'pitch': final_pitch, 'time': current_time, 'duration': duration})
        current_time += duration
    return measure_data