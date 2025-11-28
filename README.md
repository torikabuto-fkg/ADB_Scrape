# Scraper for BlueStacks

BlueStacksエミュレータ上で動作するAndroidアプリの画面を自動で保存（スクリーンショット収集）するためのPythonツールです。
主に、病院の口コミ（マッチングの口コミ）や、電子書籍や学習アプリの個人的なアーカイブ（自炊）を効率化する目的で作成されました。

## Features
- **ADB接続**: BlueStacksのポートを指定して自動接続
- **自動ページめくり**: `input swipe` コマンドによる物理スワイプのエミュレーション
- **安全設計**: ランダムな待機時間を設け、人間らしい動作を模倣
- **クリーンアップ**: デバイス側のストレージを圧迫しないよう一時ファイルを自動削除

## Requirements
- Python 3.8+
- Android Emulator (BlueStacks 5 recommended)
- ADB (Android Debug Bridge) installed and added to PATH

## Setup

### 1. BlueStacksの設定
1. BlueStacksの設定画面を開く。
2. 「詳細設定」または「環境設定」へ移動。
3. **「Android Debug Bridge (ADB) を有効にする」** をONにする。
4. 表示されるIPとポート番号（例: `127.0.0.1:5555`）を控える。

### 2. コンフィグ設定
`config.py` を開き、自身の環境に合わせて修正してください。

```python
ADB_HOST = "127.0.0.1"
ADB_PORT = "5555" # BlueStacksで確認したポート
SWIPE_START_Y = 1500 # 画面サイズに応じて調整
