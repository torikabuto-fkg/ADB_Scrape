import subprocess
import time
import os
import random

# --- 設定エリア ---

# 【修正済み】見つけていただいたBlueStacksのADBパス
# --- 設定エリア ---

# 【重要】WSL (Ubuntuなど) から実行する場合の書き方
# "C:\" は "/mnt/c/" に変わり、バックスラッシュ "\" はスラッシュ "/" になります
ADB_PATH = "/mnt/c/Program Files/BlueStacks_nxt/HD-Adb.exe"

# ポート番号
ADB_HOST = "XXX.0.0.X"
ADB_PORT = "XXXX"
ADB_ADDRESS = f"{ADB_HOST}:{ADB_PORT}"

# ...以下変更なし

# 保存先ディレクトリ
OUTPUT_DIR = "./hokuto_scrapes"

# 【修正】スワイプ設定 (1080x1920用・高速化)
# 以前の設定よりも、開始点(Start)を下げ、終了点(End)を上げました。
# これにより、一回の動作で画面の約80%を移動させます。

SWIPE_START_X = 540   # 画面横幅のちょうど真ん中
SWIPE_START_Y = 1700  # 画面のかなり下の方から掴んで...
SWIPE_END_X = 540     # 真上に引き上げる
SWIPE_END_Y = 300     # 画面の上の方まで持っていく（移動距離 1400px）

# 【修正】速度設定
# 数値が小さいほど「速いスワイプ（フリック）」になります。
# 800ms(遅い) → 400ms(速い) に変更。慣性がついてよく進みます。
SWIPE_DURATION = 850

# -----------------

def run_adb(cmd_list):
    """ADBコマンド実行ラッパー"""
    # ADB_PATHを使ってコマンドを組み立てます
    cmd = [ADB_PATH, "-s", ADB_ADDRESS] + cmd_list
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[Error] ADB Command Failed: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"[Error] Path not found: {ADB_PATH}")
        print("Please check if the file path is correct.")
        exit(1)

def connect():
    """ADB接続を試みる"""
    print(f"Connecting to {ADB_ADDRESS}...")
    run_adb(["disconnect"]) # リセット
    res = run_adb(["connect", ADB_ADDRESS])
    
    if res and ("connected" in res or "already connected" in res):
        print(f"[Success] Connected to BlueStacks.")
        return True
    else:
        print(f"[Failed] Could not connect. Connection result: {res}")
        return False

def get_file_size(filepath):
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0

def main():
    # 1. 接続
    if not connect():
        return

    # 2. フォルダ作成
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Output directory: {OUTPUT_DIR}")

    print("-" * 40)
    print("スクレイピングを開始します。")
    print("Hokutoの口コミ画面を開いておいてください。")
    print("3秒後に開始します...")
    print("-" * 40)
    time.sleep(3)

    prev_screenshot_size = -1
    consecutive_same_size = 0

    # 最大100ページ
    for i in range(1, 101):
        filename = f"review_page_{i:03d}.png"
        local_path = os.path.join(OUTPUT_DIR, filename)
        remote_path = f"/sdcard/temp_{filename}"

        print(f"[{i:03d}] Processing...")

        # A. 撮影 & 転送
        run_adb(["shell", "screencap", "-p", remote_path])
        run_adb(["pull", remote_path, local_path])
        run_adb(["shell", "rm", remote_path])
        
        # B. 終了判定（画面が動かなくなったら終了）
        current_size = get_file_size(local_path)
        if current_size == prev_screenshot_size and current_size > 0:
            consecutive_same_size += 1
            print("  -> [Stop Check] 画面に変化がありません。")
            if consecutive_same_size >= 2:
                print("終了: これ以上スクロールできません。")
                os.remove(local_path) # 重複画像を削除
                break
        else:
            consecutive_same_size = 0
        
        prev_screenshot_size = current_size

        # C. スクロール
        wait_time = random.uniform(1.5, 3.0)
        print(f"  -> Waiting {wait_time:.1f}s...")
        time.sleep(wait_time)

        run_adb(["shell", "input", "swipe", 
                 str(SWIPE_START_X), str(SWIPE_START_Y), 
                 str(SWIPE_END_X), str(SWIPE_END_Y), 
                 str(SWIPE_DURATION)])
        
        time.sleep(2.0) # 描画待ち

    print("完了しました。")

if __name__ == "__main__":
    main()
