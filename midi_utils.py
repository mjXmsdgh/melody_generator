import mido
from music_theory import CHORDS

def create_midi_file(melody_data, output_filename, ticks_per_beat=480, chord_progression=None, beats_per_measure=4):
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
        chord_progression (list, optional): コード進行のリスト。指定された場合、伴奏トラックを追加する。
        beats_per_measure (int): 1小節あたりの拍数。
    """
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    melody_track = mido.MidiTrack()
    mid.tracks.append(melody_track)

    # --- 伴奏トラックの生成 (コード進行が指定されている場合) ---
    if chord_progression:
        chord_events = []
        ticks_per_measure = ticks_per_beat * beats_per_measure
        current_time = 0
        for chord_name in chord_progression:
            chord_notes = CHORDS.get(chord_name)
            if chord_notes:
                # 各コードの構成音を note_on/note_off イベントとして追加
                for pitch in chord_notes:
                    chord_events.append({'type': 'note_on', 'pitch': pitch, 'velocity': 40, 'time': current_time})
                    chord_events.append({'type': 'note_off', 'pitch': pitch, 'velocity': 64, 'time': current_time + ticks_per_measure})
            current_time += ticks_per_measure # 次の小節の開始時間を更新

        # イベントを時間順にソート
        chord_events.sort(key=lambda x: x['time'])

        # 伴奏トラックを作成してMIDIファイルに追加
        chord_track = mido.MidiTrack()
        mid.tracks.append(chord_track)

        # 絶対時間をデルタタイムに変換してトラックに追加
        last_event_time = 0
        for event in chord_events:
            delta_time = int(event['time'] - last_event_time)
            chord_track.append(mido.Message(
                event['type'], note=event['pitch'], velocity=event['velocity'], time=delta_time
            ))
            last_event_time = event['time']

    # --- メロディートラックの生成 ---
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
        melody_track.append(mido.Message(
            event['type'], note=event['pitch'], velocity=event['velocity'], time=int(delta_time)
        ))
        last_event_time = event['time']

    mid.save(output_filename)