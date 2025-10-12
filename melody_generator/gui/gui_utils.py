import re

class ParsingError(ValueError):
    """GUIの入力テキストのパース中に発生したエラー"""
    pass

def parse_chord_progression(text: str) -> list[str]:
    """
    カンマ区切りのコード進行文字列を文字列のリストに変換します。
    空白や空の要素は無視されます。

    Args:
        text (str): GUIのテキストボックスから取得した文字列。

    Returns:
        list[str]: パースされたコード名のリスト。
        例: "C, G, Am" -> ['C', 'G', 'Am']
    """
    if not text:
        return []
    return [chord.strip() for chord in text.split(',') if chord.strip()]

def parse_motif(text: str) -> list[tuple[int, int]]:
    """
    モチーフのテキスト表現を(ピッチ, 長さ)のタプルのリストに変換します。
    ast.literal_evalの代わりに、正規表現を使って安全にパースします。

    Args:
        text (str): GUIのテキストボックスから取得した文字列。

    Returns:
        list[tuple[int, int]]: パースされた(ピッチ, 長さ)のタプルのリスト。
        例: "(76, 480),\n(74, 240)" -> [(76, 480), (74, 240)]

    Raises:
        ParsingError: テキストの形式が不正な場合。
    """
    text = text.strip()
    if not text:
        return []

    # 許可する文字以外が含まれていないかチェック
    if not re.fullmatch(r'[\d\s,()]*', text):
        raise ParsingError("モチーフには数字、カンマ、丸括弧、空白以外は使用できません。")

    try:
        # 正規表現で `(数字, 数字)` のパターンをすべて見つける
        # 各マッチで、2つの数字をキャプチャする
        tuples_str = re.findall(r'\(\s*(\d+)\s*,\s*(\d+)\s*\)', text)
        
        # キャプチャした文字列のペアを、整数のタプルに変換
        motif_notes = [(int(pitch), int(duration)) for pitch, duration in tuples_str]
        return motif_notes
    except (ValueError, TypeError) as e:
        raise ParsingError(f"モチーフの数値変換中にエラーが発生しました: {e}") from e
    except Exception as e:
        raise ParsingError(f"モチーフの解析中に予期せぬエラーが発生しました: {e}") from e