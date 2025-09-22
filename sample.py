import mido

# 1. 新しいMIDIファイルとトラックを作成
# type=0は単一トラックのMIDIファイル形式です
mid = mido.MidiFile(type=0)
track = mido.MidiTrack()
mid.tracks.append(track)

# 2. C, D, E の音符をトラックに追加
# MIDIノート番号: C4=60, D4=62, E4=64
# 1拍の長さをティックで指定します (midoのデフォルトは1拍=480ティック)
ticks_per_beat = mid.ticks_per_beat

notes = [60, 62, 64]  # C, D, E

for note_value in notes:
    # note_on: 音を鳴らし始めるメッセージ
    #   note: MIDIノート番号
    #   velocity: 音の強さ (0-127の範囲)
    #   time: 前のイベントからの経過時間 (ティック)。ここでは前の音を止めた直後に鳴らすので0。
    track.append(mido.Message('note_on', note=note_value, velocity=64, time=0))
    # note_off: 音を止めるメッセージ
    #   time: note_onからの経過時間、つまり音の長さ。ここでは1拍分(480ティック)とします。
    track.append(mido.Message('note_off', note=note_value, velocity=64, time=ticks_per_beat))

# 3. MIDIファイルを保存
output_filename = 'c_d_e.mid'
mid.save(output_filename)

print(f"MIDIファイル '{output_filename}' を生成しました。")