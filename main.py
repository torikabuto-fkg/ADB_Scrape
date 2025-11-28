import subprocess
import time
import os
import random
import datetime
from config import *

class BlueStacksScraper:
    def __init__(self):
        self.adb_address = f"{ADB_HOST}:{ADB_PORT}"
        self._ensure_dir(OUTPUT_DIR)

    def _ensure_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"[Info] Created directory: {path}")

    def _run_adb(self, command_list):
        """ADBコマンドを実行するラッパー関数"""
        cmd = [ADB_PATH] + command_list
        try:
            # shell=TrueはWindowsでのパス解決等のために使用
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[Error] ADB Command Failed: {e}")
            return None

    def connect(self):
        """BlueStacksへADB接続"""
        print(f"[System] Connecting to {self.adb_address}...")
        res = self._run_adb(["connect", self.adb_address])
        if res and ("connected" in res or "already connected" in res):
            print("[Success] Connected.")
            return True
        else:
            print(f"[Failed] Could not connect. Ensure BlueStacks is running and ADB is enabled.")
            return False

    def take_screenshot(self, filename):
        """スクリーンショットを撮影しPCへ転送"""
        remote_path = "/sdcard/screen_tmp.png"
        local_path = os.path.join(OUTPUT_DIR, filename)

        # 1. キャプチャ
        self._run_adb(["-s", self.adb_address, "shell", "screencap", "-p", remote_path])
        # 2. PCへ転送
        self._run_adb(["-s", self.adb_address, "pull", remote_path, local_path])
        # 3. デバイス内のゴミ削除
        self._run_adb(["-s", self.adb_address, "shell", "rm", remote_path])
        
        print(f"[Capture] Saved: {local_path}")

    def scroll_page(self):
        """画面をスワイプして次ページへ"""
        cmd = [
            "-s", self.adb_address,
            "shell", "input", "swipe",
            str(SWIPE_START_X), str(SWIPE_START_Y),
            str(SWIPE_END_X), str(SWIPE_END_Y),
            str(SWIPE_DURATION_MS)
        ]
        self._run_adb(cmd)
        print("[Action] Scrolled.")

    def run(self, pages=TOTAL_PAGES):
        """メイン実行ループ"""
        if not self.connect():
            return

        print(f"[Start] Starting scrape for {pages} pages.")
        
        for i in range(1, pages + 1):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_{i:03d}_{timestamp}.png"
            
            # スクショ撮影
            self.take_screenshot(filename)
            
            # ランダム待機 (サーバー負荷軽減 & BAN対策)
            sleep_time = random.uniform(SLEEP_MIN, SLEEP_MAX)
            # print(f"Sleeping for {sleep_time:.2f}s...") # ログがうるさければコメントアウト
            time.sleep(sleep_time)

            # スクロール
            self.scroll_page()
            
            # スクロール後の描画待ち
            time.sleep(1.5)

        print("[Finish] Job completed.")

if __name__ == "__main__":
    scraper = BlueStacksScraper()
    scraper.run()
