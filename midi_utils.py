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

def create_midi_file(melody_data, output_filename, ticks_per_beat=480, accompaniment_data=None):
    """
    メロディーデータからMIDIファイルを生成する関数。

    Args:
        melody_data (list): 音符の辞書を含むリスト。
        output_filename (str): 出力するMIDIファイル名。
        ticks_per_beat (int): 1拍あたりのティック数。
        accompaniment_data (list, optional): 伴奏の音符データのリスト。指定された場合、伴奏トラックを追加する。
    """
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)

    # --- メロディートラックの生成 ---
    # ヘルパー関数を使ってメロディートラックを生成
    melody_track = _create_track_from_notes(melody_data, velocity=64)
    mid.tracks.append(melody_track)

    # --- 伴奏トラックの生成 (伴奏データが指定されている場合) ---
    if accompaniment_data:
        # ヘルパー関数を使って伴奏トラックを生成
        chord_track = _create_track_from_notes(accompaniment_data, velocity=40)
        mid.tracks.append(chord_track)

    mid.save(output_filename)