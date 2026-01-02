#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Hokuto（BlueStacks）画面のUI階層を uiautomator dump でXML出力し、
XML内の text 属性を抽出して、1つのテキストファイルに保存します。

前提:
- BlueStacks の ADB が有効
- `adb devices` で 127.0.0.1:5556 が device として表示される状態
"""

import subprocess
import time
import os
import xml.etree.ElementTree as ET

# --- 設定 ---
ADB_PATH = "/mnt/c/Program Files/BlueStacks_nxt/HD-Adb.exe"
ADB_HOST = "127.0.0.1"
ADB_PORT = "5556"
ADB_ADDRESS = f"{ADB_HOST}:{ADB_PORT}"

# 出力先
OUTPUT_DIR = "./hokuto_scrapes_xml"
OUTPUT_FILE = "東大病院.txt"

# スワイプ設定（短めに）
SWIPE_START_X = 540
SWIPE_START_Y = 1400
SWIPE_END_X = 540
SWIPE_END_Y = 700
SWIPE_DURATION = 600


def run_adb(cmd_list, use_serial: bool = True):
    """ADBコマンド実行"""
    cmd = [ADB_PATH]
    if use_serial:
        cmd += ["-s", ADB_ADDRESS]
    cmd += cmd_list

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[Error] ADB Command Failed: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print(f"[Error] ADBが見つかりません: {ADB_PATH}")
        return None


def connect():
    """ADB接続"""
    print(f"Connecting to {ADB_ADDRESS}...")

    # connect/disconnect は -s を付けない方が安定します
    run_adb(["disconnect"], use_serial=False)
    res = run_adb(["connect", ADB_ADDRESS], use_serial=False)

    if res and ("connected" in res or "already connected" in res):
        print("[Success] Connected")
        return True

    print("[Failed] Could not connect")
    if res:
        print("  -> result:", res)
    return False


def dump_ui_xml(output_path="ui.xml"):
    """UIの階層構造をXMLとしてダンプ"""
    remote_path = "/sdcard/ui.xml"

    # UIをダンプ
    run_adb(["shell", "uiautomator", "dump", remote_path])

    # ローカルに転送
    run_adb(["pull", remote_path, output_path])

    # リモートファイル削除
    run_adb(["shell", "rm", remote_path])

    return output_path


def extract_text_from_xml(xml_path):
    """XMLからtext属性を持つすべての要素のテキストを抽出"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        texts = []
        for elem in root.iter():
            text = (elem.get("text") or "").strip()
            if text and text not in texts:  # 重複除去
                texts.append(text)

        return texts
    except Exception as e:
        print(f"[Error] XML解析エラー: {e}")
        return []


def main():
    # 1. 接続
    if not connect():
        return

    # 2. 出力ディレクトリ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_txt_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    print("-" * 40)
    print("UI XMLダンプによるスクレイピングを開始します")
    print("Hokutoの口コミ画面を開いておいてください")
    print("3秒後に開始...")
    print("-" * 40)
    time.sleep(3)

    all_texts = []  # 順序を保持するためにリストを使用
    prev_text_count = 0
    no_change_count = 0

    # 最大100回スクロール
    for i in range(1, 101):
        print(f"\n[{i:03d}] UIダンプ中...")

        # A. UI XMLをダンプ
        xml_path = f"temp_ui_{i:03d}.xml"
        dump_ui_xml(xml_path)

        # B. テキスト抽出
        texts = extract_text_from_xml(xml_path)

        # 新しいテキストを追加（順序を保持）
        new_texts = []
        for text in texts:
            if text not in all_texts:
                all_texts.append(text)
                new_texts.append(text)

        print(f"  -> 新規テキスト: {len(new_texts)}件")
        print(f"  -> 累計: {len(all_texts)}件")

        # プレビュー表示（新規テキストの最初の3行）
        if new_texts:
            print("  --- 新規テキストプレビュー ---")
            for j, text in enumerate(new_texts[:3], 1):
                preview = text[:50] + "..." if len(text) > 50 else text
                print(f"    {j}. {preview}")

        # XMLファイル削除
        try:
            os.remove(xml_path)
        except FileNotFoundError:
            pass

        # C. 終了判定
        if len(all_texts) == prev_text_count:
            no_change_count += 1
            print("  -> [Stop Check] 新しいテキストがありません")
            if no_change_count >= 3:
                print("終了: これ以上スクロールしても新しいテキストが見つかりません")
                break
        else:
            no_change_count = 0

        prev_text_count = len(all_texts)

        # D. スクロール
        time.sleep(2.0)

        run_adb([
            "shell", "input", "swipe",
            str(SWIPE_START_X), str(SWIPE_START_Y),
            str(SWIPE_END_X), str(SWIPE_END_Y),
            str(SWIPE_DURATION)
        ])

        time.sleep(2.0)  # 描画待ち

    # E. 結果をファイルに保存（元の順序を保持）
    print(f"\n結果を保存中: {output_txt_path}")
    with open(output_txt_path, "w", encoding="utf-8") as f:
        for text in all_texts:
            f.write(text + "\n")

    print("\n✅ 完了")
    print(f"抽出されたテキスト: {len(all_texts)}件")
    print(f"保存先: {output_txt_path}")


if __name__ == "__main__":
    main()
