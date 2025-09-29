import mido
from music_theory import CHORDS

def _create_track_from_notes(notes_data, velocity=64):
    """
    音符データのリストからMIDIトラックを生成するヘルパー関数。
    絶対時間で記述された音符リストを、デルタタイムを持つMIDIイベントに変換します。

    Args:
        notes_data (list): 音符の辞書を含むリスト。
            各辞書は {'pitch': int, 'time': int, 'duration': int} の形式。
        velocity (int): MIDIノートのベロシティ（音の強さ）。

    Returns:
        mido.MidiTrack: 生成されたMIDIトラック。
    """
    track = mido.MidiTrack()
    midi_events = []

    # 1. 音符データを note_on/note_off イベントに変換
    for note in notes_data:
        midi_events.append({'type': 'note_on', 'pitch': note['pitch'], 'velocity': velocity, 'time': note['time']})
        midi_events.append({'type': 'note_off', 'pitch': note['pitch'], 'velocity': velocity, 'time': note['time'] + note['duration']})

    # 2. イベントを時間順にソート
    midi_events.sort(key=lambda x: x['time'])

    # 3. 絶対時間をデルタタイムに変換してトラックに追加
    last_event_time = 0
    for event in midi_events:
        delta_time = int(event['time'] - last_event_time)
        track.append(mido.Message(
            event['type'], note=event['pitch'], velocity=event['velocity'], time=delta_time
        ))
        last_event_time = event['time']

    return track

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

    # --- メロディートラックの生成 ---
    # ヘルパー関数を使ってメロディートラックを生成
    melody_track = _create_track_from_notes(melody_data, velocity=64)
    mid.tracks.append(melody_track) # 常にトラック0として追加

    # --- 伴奏トラックの生成 (コード進行が指定されている場合) ---
    if chord_progression:
        chord_notes_data = []
        ticks_per_measure = ticks_per_beat * beats_per_measure
        current_time = 0

        for chord_name in chord_progression:
            chord_notes = CHORDS.get(chord_name)
            if chord_notes:
                # 各コードの構成音を1オクターブ下げて、音符データリストに追加
                for pitch in chord_notes:
                    chord_notes_data.append({
                        'pitch': pitch - 12,  # 1オクターブ下げる
                        'time': current_time,
                        'duration': ticks_per_measure
                    })
            current_time += ticks_per_measure

        # ヘルパー関数を使って伴奏トラックを生成
        chord_track = _create_track_from_notes(chord_notes_data, velocity=40)
        mid.tracks.append(chord_track)

    mid.save(output_filename)