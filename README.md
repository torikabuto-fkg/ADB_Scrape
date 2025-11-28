Medical Edge Scraper & OCR Pipeline

<div align="center">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3.8%252B-blue" alt="Python Version">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Platform-Windows%2520%257C%2520WSL-lightgrey" alt="Platform">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Tools-BlueStacks%2520%257C%2520PaddleOCR-orange" alt="Tools">
</div>

概要 (Overview)

医学部の学習・マッチング活動を効率化するための「エッジ攻略」ツールセットです。
Androidエミュレータ上のアプリ画面（Hokutoなど）を自動でスクロール＆キャプチャし、AI-OCRを用いてテキストデータ化・PDF化を一括で行います。

取得したデータはLLM（ChatGPT/Claude）に投入することで、数年分の口コミを数秒で分析・要約することが可能です。

機能 (Features)

1. Scraper (hokuto_scrape.py)

BlueStacks (Androidエミュレータ) とADB接続し、自動スクロール＆スクリーンショット撮影を行います。

重複検知機能により、リストの最後まで到達すると自動停止します。

BAN対策: 人間らしいランダムな待機時間を実装済み。

2. OCR Pipeline (ocr_pipeline.py)

収集した画像を結合してPDF化（Goodnotesなどで閲覧用）。

PaddleOCR (GPU対応) を使用し、高精度に日本語テキストを抽出。

Word (.docx) および Text (.txt) 形式で出力し、分析に即座に利用可能。

必要要件 (Requirements)

Python 3.8+

Android Emulator (BlueStacks 5 推奨)

ADB (BlueStacks同梱のものを使用)

NVIDIA GPU (推奨・OCR高速化のため)

インストール (Installation)

1. リポジトリのクローン

git clone [https://github.com/torikabuto-fkg/medical-edge-scraper.git](https://github.com/torikabuto-fkg/medical-edge-scraper.git)
cd medical-edge-scraper


2. ライブラリのインストール

GPUを使用する場合（推奨）:

python -m pip install paddlepaddle-gpu==2.6.1
pip install -r requirements.txt


CPUのみの場合:

python -m pip install paddlepaddle
pip install -r requirements.txt


使い方 (Usage)

Step 1: BlueStacksの設定とスクレイピング

BlueStacksの設定で ADBデバッグ を有効にします。

対象アプリ（Hokutoなど）の口コミ画面を開きます。

スクリプトを実行します。

python hokuto_scrape.py


※ hokuto_scrape.py 内の ADB_PATH はご自身の環境に合わせて書き換えてください。

Step 2: OCR & PDF化

画像が ./hokuto_scrapes/ に保存されたら、解析パイプラインを実行します。

python ocr_pipeline.py


Step 3: 出力結果の確認

./output_data/ ディレクトリに以下のファイルが生成されます。

hokuto_reviews.pdf: 結合されたPDF

hokuto_reviews.docx: OCR結果のWordファイル

hokuto_raw_text.txt: AI分析用のテキストデータ

AI分析のヒント (Tips for AI Analysis)

生成された hokuto_raw_text.txt の内容をコピーし、ChatGPTやClaudeに以下のプロンプトと共に投げることで、病院情報の要約レポートを作成できます。

プロンプト例:

"添付のテキストは病院口コミのOCRデータです。重複を除去し、給与・当直回数・病院の雰囲気について要約してください。"

注意事項 (Disclaimer)

本ツールは技術的な検証および私的利用を目的としています。

対象アプリの利用規約（ToS）を遵守し、サーバーへの過度な負荷をかける行為や、取得したデータの再配布は行わないでください。

本ツール使用によるアカウント停止等の不利益について、著者は一切の責任を負いません。

License

MIT
