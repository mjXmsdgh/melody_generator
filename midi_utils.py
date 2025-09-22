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
    midi_events = []
    for note in melody_data:
        midi_events.append({
            'type': 'note_on',
            'pitch': note['pitch'],
            'velocity': 64,  # 音の強さは64で固定
            'time': note['time']
        })
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
        delta_time = int(event['time'] - last_event_time)
        track.append(mido.Message(
            event['type'], note=event['pitch'], velocity=event['velocity'], time=int(delta_time)
        ))
        last_event_time = event['time']

    # 4. MIDIファイルを保存
    mid.save(output_filename)