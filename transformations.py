"""
メロディーを1小節単位で加工する「変換操作」のカタログ。
"""
from music_theory import snap_to_scale
import random

# 各変換操作（フィルタ）は、1小節分のメロディーデータを受け取り、
# 加工した1小節分のメロディーデータを返すように統一します。
#
# 入出力形式: [{'pitch': int, 'time': int, 'duration': int}, ...]
#
# これにより、フィルタチェーン（複数のフィルタの連続適用）が容易になります。

def transform_identity(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをそのまま演奏する。
    入力データをそのまま返す、最も基本的なフィルタ。
    """
    return measure_data[:] # コピーを返す

def transform_retrograde(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフを逆行させる（音の順番を逆にする）。
    """
    new_measure_data = []
    current_time = 0
    # 音符のリストを逆順にする
    reversed_notes = measure_data[::-1]
    for note in reversed_notes:
        new_measure_data.append({'pitch': note['pitch'], 'time': current_time, 'duration': note['duration']})
        current_time += note['duration']
    return new_measure_data

def transform_ending(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフを演奏し、最後を主音で解決させる。
    """
    new_measure_data = []
    tonic = scale[0]

    for i, note in enumerate(measure_data):
        final_pitch = note['pitch']
        if i == len(measure_data) - 1:  # モチーフの最後の音の場合
            # 元の音に近いオクターブの主音に補正
            final_pitch = snap_to_scale(tonic, [note['pitch']])
        new_measure_data.append({'pitch': final_pitch, 'time': note['time'], 'duration': note['duration']})
    return new_measure_data

def transform_rhythm_staccato(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を「8分音符 + 8分休符」のスタッカートにする。
    """
    new_measure_data = []
    note_duration = ticks_per_beat // 2  # 8分音符の長さ

    for note in measure_data:
        new_measure_data.append({'pitch': note['pitch'], 'time': note['time'], 'duration': note_duration})
    return new_measure_data

def transform_rhythm_double_time(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を半分の長さの音符2つに分割する（倍速化）。
    """
    new_measure_data = []
    for note in measure_data:
        half_duration = note['duration'] // 2
        # 1つ目の8分音符
        new_measure_data.append({'pitch': note['pitch'], 'time': note['time'], 'duration': half_duration})
        # 2つ目の8分音符
        new_measure_data.append({'pitch': note['pitch'], 'time': note['time'] + half_duration, 'duration': half_duration})
    return new_measure_data

def transform_syncopation_push(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を8分音符分「前」にずらす（食い気味のシンコペーション）。
    """
    new_measure_data = []
    push_amount = ticks_per_beat // 2  # 8分音符分ずらす

    for note in measure_data:
        # 8分音符分、前にずらす。ただし小節の頭(time=0)より前には行かない。
        start_time = max(0, note['time'] - push_amount)
        new_measure_data.append({'pitch': note['pitch'], 'time': start_time, 'duration': note['duration']})
    return new_measure_data

def transform_syncopation_pull(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を8分音符分「後」にずらす（もたらせるシンコペーション）。
    """
    new_measure_data = []
    pull_amount = ticks_per_beat // 2  # 8分音符分ずらす
    
    if not measure_data:
        return []
    measure_duration = max(n['time'] + n['duration'] for n in measure_data)

    for note in measure_data:
        start_time = note['time'] + pull_amount

        # 小節の長さを超えないように音符の長さを調整
        adjusted_duration = note['duration']
        if start_time + adjusted_duration > measure_duration:
            adjusted_duration = max(0, measure_duration - start_time)

        if adjusted_duration > 0:
            new_measure_data.append({'pitch': note['pitch'], 'time': start_time, 'duration': adjusted_duration})
    return new_measure_data

def transform_transpose_up(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをスケールに沿って2音上に移高する。
    """
    new_measure_data = []
    for note in measure_data:
        # 元の音からだいたい全音(2)分高い音をターゲットにし、スケールに最も近い音に補正
        transposed_pitch = snap_to_scale(note['pitch'] + 2, scale)
        new_measure_data.append({'pitch': transposed_pitch, 'time': note['time'], 'duration': note['duration']})
    return new_measure_data

def transform_transpose_down(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフをスケールに沿って2音下に移高する。
    """
    new_measure_data = []
    for note in measure_data:
        # 元の音からだいたい全音(2)分低い音をターゲットにし、スケールに最も近い音に補正
        transposed_pitch = snap_to_scale(note['pitch'] - 2, scale)
        new_measure_data.append({'pitch': transposed_pitch, 'time': note['time'], 'duration': note['duration']})
    return new_measure_data

def transform_rhythm_dotted(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: 各音符を「付点8分音符 + 16分音符」のリズムパターンに変換する。
    元の音符1つが、同じピッチの2つの音符（タータ）に置き換わります。
    """
    new_measure_data = []
    dotted_eighth_duration = int(ticks_per_beat * 0.75)  # 付点8分音符
    sixteenth_duration = int(ticks_per_beat * 0.25)      # 16分音符

    for note in measure_data:
        # 元の音符の長さが1拍以上の場合に適用
        if note['duration'] >= ticks_per_beat:
            num_beats = note['duration'] // ticks_per_beat
            current_time = note['time']
            for _ in range(num_beats):
                new_measure_data.append({'pitch': note['pitch'], 'time': current_time, 'duration': dotted_eighth_duration})
                current_time += dotted_eighth_duration
                new_measure_data.append({'pitch': note['pitch'], 'time': current_time, 'duration': sixteenth_duration})
                current_time += sixteenth_duration
        else: # 1拍未満の音符はそのまま
            new_measure_data.append(note.copy())
    return new_measure_data

def transform_rhythm_triplet(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフ内の長い音符(1拍以上)をランダムに1つ選び、8分音符の3連符に変換する。
    """
    new_measure_data = []
    triplet_duration = ticks_per_beat // 3 # 1拍を3分割した長さ

    # 1. 1拍以上の長い音符のインデックスをリストアップ
    long_note_indices = [i for i, note in enumerate(measure_data) if note['duration'] >= ticks_per_beat]

    # 2. 変換対象の音符をランダムに1つ選ぶ
    note_to_transform_index = random.choice(long_note_indices) if long_note_indices else -1

    # 3. モチーフを処理
    for i, note in enumerate(measure_data):
        if i == note_to_transform_index:
            # 選ばれた音符を3連符に変換
            num_beats = note['duration'] // ticks_per_beat
            current_time = note['time']
            for _ in range(num_beats):
                for _ in range(3):
                    new_measure_data.append({'pitch': note['pitch'], 'time': current_time, 'duration': triplet_duration})
                    current_time += triplet_duration
        else:
            # それ以外の音符はそのまま追加
            new_measure_data.append(note.copy())
    return new_measure_data

def transform_add_passing_notes(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフ内の音符間に経過音を挿入する。
    音符間に3度以上の跳躍があり、かつ元の音符が4分音符以上の場合に、間のスケール音を8分音符で埋める。
    """
    if not measure_data:
        return []

    new_measure_data = []
    passing_note_duration = ticks_per_beat // 2  # 8分音符
    min_duration_for_passing_note = ticks_per_beat # 4分音符以上の長さを持つ音符を対象とする

    for i in range(len(measure_data)):
        current_note = measure_data[i].copy()
        new_measure_data.append(current_note)

        # 次の音符があるかチェック
        if i + 1 < len(measure_data):
            next_note = measure_data[i+1]

            # 条件: 1. 音程が3度以上離れている 2. 現在の音符の長さが4分音符以上
            if abs(next_note['pitch'] - current_note['pitch']) >= 3 and current_note['duration'] >= min_duration_for_passing_note:
                # 1. 現在の音符の長さを8分音符分短くする
                current_note['duration'] -= passing_note_duration

                # 2. 経過音を生成して追加する
                step = 1 if next_note['pitch'] > current_note['pitch'] else -1
                passing_pitch_candidate = current_note['pitch'] + step
                passing_pitch = snap_to_scale(passing_pitch_candidate, scale)

                passing_note_time = current_note['time'] + current_note['duration']
                new_measure_data.append({'pitch': passing_pitch, 'time': passing_note_time, 'duration': passing_note_duration})

    return new_measure_data

def transform_slight_variation(measure_data, key, scale, ticks_per_beat=480):
    """
    変換操作: モチーフの最後の音をスケールに沿って1音上または下にずらす。
    Aセクション内のマイナーチェンジ(a -> a')を表現するために使用する。
    """
    if not measure_data:
        return []

    new_measure_data = measure_data[:] # コピーを作成
    if new_measure_data:
        last_note = new_measure_data[-1]
        direction = random.choice([-1, 1])
        last_note['pitch'] = snap_to_scale(last_note['pitch'] + direction, scale)
    return new_measure_data