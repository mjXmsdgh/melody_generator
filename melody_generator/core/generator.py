import logging

# 新しく作成したファイルからクラスをインポート
from melody_generator.core.melody_config import MelodyConfig
from melody_generator.core.melody_processor import MelodyProcessor
from melody_generator.core.accompaniment_processor import AccompanimentProcessor

# 既存のユーティリティと定義をインポート
from melody_generator.core.music_theory import SCALES
from melody_generator.utils.midi_utils import create_midi_file

class MelodyGenerator:
    """
    メロディー生成に関する状態と振る舞いを一元管理するクラス。
    GUIや他のクライアントコードから「部品」として利用されることを想定しています。
    """

    def __init__(self, config: MelodyConfig, logger=None):
        """
        コンストラクタ。メロディー生成に必要な設定オブジェクトを受け取ります。

        Args:
            config (MelodyConfig): 設定を保持するデータクラスのインスタンス。
            logger (logging.Logger, optional): ログ出力用のロガー。
                                               指定されない場合、標準出力にフォールバックします。
        """
        # --- ロガーの設定 ---
        self.logger = logger or logging.getLogger(__name__)
        # --- 設定の保持 ---
        self.config = config

        # --- プロセッサの初期化 ---
        # 依存するプロセッサをコンストラクタで生成することで、依存関係を明確にします。
        self.melody_processor = MelodyProcessor(logger=self.logger)
        self.accompaniment_processor = AccompanimentProcessor(logger=self.logger)

        # --- 生成結果の初期化 ---
        self.melody_data = None
        self.accompaniment_data = None

    def generate(self):
        """
        保持している設定に基づき、メロディーと伴奏の内部データを生成します。
        """
        self.logger.info(f"--- メロディー生成を開始します ({self.config.num_measures}小節) ---")

        # 1. 準備
        scale = SCALES[self.config.key]
        ticks_per_measure = self.config.ticks_per_beat * self.config.beats_per_measure

        # 2. 各プロセッサに処理を委譲
        self.melody_data = self.melody_processor.process(self.config)
        self.accompaniment_data = self.accompaniment_processor.process(self.config, scale, ticks_per_measure)

        self.logger.info("\nメロディーと伴奏の内部データ生成が完了しました。")

    def save_midi(self, output_path):
        """
        生成済みのメロディーデータをMIDIファイルとして保存します。
        """
        if self.melody_data is None:
            raise RuntimeError("メロディーがまだ生成されていません。先に .generate() を呼び出してください。")

        create_midi_file(
            melody_data=self.melody_data,
            output_filename=output_path,
            ticks_per_beat=self.config.ticks_per_beat,
            accompaniment_data=self.accompaniment_data
        )
        self.logger.info(f"MIDIファイル '{output_path}' を保存しました。")