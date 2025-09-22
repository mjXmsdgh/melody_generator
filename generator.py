import mido

def create_midi_file(melody_data, output_filename, ticks_per_beat=480):
    """
    メロディーデータからMIDIファイルを生成する関数。

    Args:
        melody_data (list): 音符の辞書を含むリスト。
            各辞書は {'pitch': int, 'time': int, 'duration': int} の形式。
            - pitch: MIDIノート番号
            - time: 曲の先頭からの絶対開始時間 (ティック単位)
            - duration: 音の長さ (ティック単位)
        output_filename (str): 出力するMIDIファイル名。
        ticks_per_beat (int): 1拍あたりのティック数。
    """
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # 1. メロディーデータを note_on/note_off イベントのリストに変換する
    #    この時点では時間は「絶対時間」で保持する
    midi_events = []
    for note in melody_data:
        # note_on イベントを追加
        midi_events.append({
            'type': 'note_on',
            'pitch': note['pitch'],
            'velocity': 64,  # 音の強さは64で固定
            'time': note['time']
        })
        # note_off イベントを追加
        midi_events.append({
            'type': 'note_off',
            'pitch': note['pitch'],
            'velocity': 64,
            'time': note['time'] + note['duration']
        })

    # 2. イベントを時間順にソートする
    midi_events.sort(key=lambda x: x['time'])

    # 3. 絶対時間を「前のイベントからの経過時間 (デルタタイム)」に変換してトラックに追加
    last_event_time = 0
    for event in midi_events:
        delta_time = event['time'] - last_event_time
        track.append(mido.Message(
            event['type'],
            note=event['pitch'],
            velocity=event['velocity'],
            time=delta_time
        ))
        last_event_time = event['time']

    # 4. MIDIファイルを保存
    mid.save(output_filename)

# --- メロディー生成ロジック ---

# 1. スケール定義
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

# --- 変換操作 (Transformations) ---
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

def strategy_a_simple_sequence(motif_notes, key, ticks_per_beat=480):
    """
    生成戦略A: モチーフをシーケンス（反復進行）させて4小節のメロディーを生成する。
    - 1小節目: モチーフ
    - 2小節目: モチーフを2度上にシーケンス
    - 3小節目: モチーフを5度上にシーケンス
    - 4小節目: モチーフに戻り、主音で解決
    """
    if key not in SCALES:
        raise ValueError(f"キー '{key}' は定義されていません。利用可能なキー: {list(SCALES.keys())}")

    scale = SCALES[key]
    tonic = scale[0]  # キーの主音
    melody_data = []
    current_time = 0
    note_duration = ticks_per_beat  # 各音符を1拍（4分音符）とする

    # --- 4小節のメロディーを構成 ---
    # 1小節目: 元のモチーフ
    for pitch in motif_notes:
        melody_data.append({'pitch': pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration

    # 2小節目: 2度上 (長2度 = 2半音) にシーケンス
    for pitch in motif_notes:
        transposed_pitch = pitch + 2
        snapped_pitch = snap_to_scale(transposed_pitch, scale)
        melody_data.append({'pitch': snapped_pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration

    # 3小節目: 5度上 (完全5度 = 7半音) にシーケンス
    for pitch in motif_notes:
        transposed_pitch = pitch + 7
        snapped_pitch = snap_to_scale(transposed_pitch, scale)
        melody_data.append({'pitch': snapped_pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration

    # 4小節目: 元のモチーフに戻り、最後を主音で解決させる
    for i, pitch in enumerate(motif_notes):
        final_pitch = pitch
        if i == len(motif_notes) - 1:  # モチーフの最後の音の場合
            final_pitch = snap_to_scale(tonic, [pitch]) # 元の音に近いオクターブの主音に補正
        melody_data.append({'pitch': final_pitch, 'time': current_time, 'duration': note_duration})
        current_time += note_duration

    return melody_data


# --- メインの実行ブロック ---
if __name__ == "__main__":
    # 1. 生成に使用するモチーフとキーを定義
    # モチーフ: ドレミ (C4, D4, E4)
    input_motif = [60, 62, 64]
    input_key = 'C_major'
    scale_notes = SCALES[input_key]

    # --- (A) 既存の戦略の実行 (比較のため残しています) ---
    print("--- 戦略Aの実行 ---")
    strategy_a_melody = strategy_a_simple_sequence(input_motif, input_key)
    create_midi_file(strategy_a_melody, 'strategy_a_output.mid')
    print(f"MIDIファイル 'strategy_a_output.mid' を生成しました。\n")

    # --- (B) 新しい変換操作のテスト実行 ---
    # これらは1小節分のメロディーデータを生成します。
    print("--- 新しい変換操作のテスト ---")

    # Identity (そのまま)
    identity_melody = transform_identity(input_motif, input_key, scale_notes)
    create_midi_file(identity_melody, 'transform_identity_output.mid')
    print(f"-> MIDIファイル 'transform_identity_output.mid' を生成しました。 (モチーフ: ドレミ)")

    # Retrograde (逆行)
    retrograde_melody = transform_retrograde(input_motif, input_key, scale_notes)
    create_midi_file(retrograde_melody, 'transform_retrograde_output.mid')
    print(f"-> MIDIファイル 'transform_retrograde_output.mid' を生成しました。 (モチーフ: ミレド)")