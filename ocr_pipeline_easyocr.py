import os
import sys
import glob
import subprocess
from datetime import datetime

from natsort import natsorted
from PIL import Image


# ========= 設定 =========

# もとの画像が入っているフォルダ
#   例: ./hokuto_scrapes/さいたま赤十字
IMAGE_DIR = "./hokuto_scrapes/さいたま赤十字"

# 作業＆出力フォルダ
OUTPUT_DIR = "./output_easyocr"

# 中間 PDF / OCR 済み PDF のファイル名
INPUT_PDF_NAME = "scanned_from_images.pdf"
OCR_PDF_NAME = "scanned_from_images_ocr_easyocr.pdf"

# OCR 言語（EasyOCR プラグインでも -l は使われる）
# jpn+eng など複数指定も可
OCR_LANG = "jpn"

# ocrmypdf 実行時の並列ジョブ数
OCR_JOBS = 4

# ========= ユーティリティ =========


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def collect_images(image_dir: str):
    """
    対象フォルダから PNG/JPG を自然順で集める
    """
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff"]
    paths = []
    for pat in patterns:
        paths.extend(glob.glob(os.path.join(image_dir, pat)))

    if not paths:
        raise FileNotFoundError(f"画像が見つかりません: {image_dir}")

    # 01, 02, 10 ... のように自然順で並べる
    paths = natsorted(paths)
    return paths


def build_pdf_from_images(img_paths, pdf_path: str):
    """
    Pillow だけを使って、複数画像 → 1 本の PDF にまとめる
    ExifTags などは使わないので、Pillow のバージョン差異の影響を受けにくい
    """
    log(f"PDF 作成開始: {len(img_paths)} 枚 -> {pdf_path}")

    images = []
    for p in img_paths:
        img = Image.open(p)
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)

    if not images:
        raise RuntimeError("PDF に変換する画像がありません")

    first = images[0]
    rest = images[1:]

    # save_all + append_images で 1 本のマルチページ PDF
    first.save(pdf_path, save_all=True, append_images=rest)
    log("PDF 作成完了")


def run_ocrmypdf_easyocr(
    input_pdf: str,
    output_pdf: str,
    sidecar_txt: str | None = None,
    lang: str = "jpn",
    jobs: int = 4,
):
    """
    OCRmyPDF + EasyOCR プラグインで PDF を OCR する
    - 事前に ocrmypdf-easyocr をインストールしておく
    - CLI の --plugin オプションで EasyOCR プラグインを明示的に有効化
      参考: ocrmypdf plugins ドキュメント
    """
    cmd = [
        "ocrmypdf",
        "--plugin",
        "ocrmypdf_easyocr",       # プラグイン名（パッケージ名と同じ）
        "-l",
        lang,                     # 例: jpn, jpn+eng
        "--jobs",
        str(jobs),
        "--optimize",
        "1",                      # 軽めの最適化
        "--output-type",
        "pdfa",                   # PDF/A にしたくない場合は pdf
        "--skip
