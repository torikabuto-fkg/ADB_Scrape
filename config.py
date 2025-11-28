# config.py

# BlueStacksのADBポート
# 設定 > 詳細設定 > ADBデバッグ をONにした際に表示されるポート
# デフォルトは 127.0.0.1:5555 が多いですが、インスタンスによって変わります
ADB_HOST = "127.0.0.1"
ADB_PORT = "5555"

# adbのパス (環境変数に通っていない場合はフルパスを指定: "C:\\Program Files\\...\\adb.exe")
ADB_PATH = "adb"

# 保存先ディレクトリ
OUTPUT_DIR = "./screenshots"

# スクロール設定 (BlueStacksの解像度に合わせる)
# 例: 1080x1920の場合、下(y=1500)から上(y=500)へスワイプ
SWIPE_START_X = 540
SWIPE_START_Y = 1500
SWIPE_END_X = 540
SWIPE_END_Y = 500
SWIPE_DURATION_MS = 800

# 待機時間設定 (秒) - アカBAN対策のためランダム性を持たせる
SLEEP_MIN = 2.0
SLEEP_MAX = 4.0

# 取得ページ数
TOTAL_PAGES = 100
