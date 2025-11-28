import os
import glob
import img2pdf
import paddle # 追加: GPU設定用
from paddleocr import PaddleOCR
from natsort import natsorted
from docx import Document
from tqdm import tqdm
import logging

# ログ抑制
logging.getLogger("ppocr").setLevel(logging.WARNING)

# --- 設定エリア ---
IMAGE_DIR = "./hokuto_scrapes/"   # 画像の保存先
OUTPUT_DIR = "./koshigayashiritsu"     # 出力先
PDF_FILENAME = "koshigayashiritsu_reviews.pdf"
DOCX_FILENAME = "koshigayashiritsu_reviews.docx"
TXT_FILENAME = "koshigayashiritsu_raw_text.txt"

CONFIDENCE_THRESHOLD = 0.6 

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. GPU設定 (ここが修正ポイント)
    # CUDAが使える環境ならGPUを、だめならCPUを自動選択させたい場合はここを調整
    try:
        paddle.set_device('gpu') 
        print("✅ GPUモードで動作します")
    except Exception as e:
        print("⚠️ GPUが見つからないか設定できませんでした。CPUで動作します。")
        print(f"エラー詳細: {e}")
        paddle.set_device('cpu')

    # 2. 画像リスト取得
    img_paths = natsorted(glob.glob(os.path.join(IMAGE_DIR, "*.png")))
    if not img_paths:
        print(f"エラー: '{IMAGE_DIR}' に画像が見つかりません。")
        return

    print(f"対象画像: {len(img_paths)}枚")

    # =========================================================
    # Phase 1: PDF作成
    # =========================================================
    # ※ alpha channel のログは無視して大丈夫です
    print("\n[1/3] PDFを作成しています...")
    pdf_path = os.path.join(OUTPUT_DIR, PDF_FILENAME)
    
    try:
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(img_paths))
        print(f"  -> PDF保存完了: {pdf_path}")
    except Exception as e:
        print(f"  -> PDF作成エラー: {e}")

    # =========================================================
    # Phase 2: PaddleOCR実行 (引数を修正)
    # =========================================================
    print("\n[2/3] PaddleOCRで解析しています...")
    
    # 【重要修正】
    # 1. use_gpu=True を削除 (上で set_device しているため)
    # 2. use_angle_cls を use_textline_orientation に変更 (警告対応)
    # 3. show_log を削除（新しいバージョンで非対応）
    try:
        ocr = PaddleOCR(
            use_textline_orientation=True,  # 旧: use_angle_cls=True
            lang='japan'
        )
    except Exception as e:
        # 万が一新しい引数名が通らない場合のフォールバック
        print("警告: 新しい引数名が非対応のため、旧引数で再試行します")
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang='japan'
        )
    
    full_text_data = []

    for img_path in tqdm(img_paths, desc="OCR Progress"):
        file_name = os.path.basename(img_path)
        
        # OCR実行
        result = ocr.ocr(img_path, cls=True)
        
        page_text = []
        
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                score = line[1][1]
                
                if score >= CONFIDENCE_THRESHOLD:
                    page_text.append(text)
        
        full_text_data.append({
            "filename": file_name,
            "content": "\n".join(page_text)
        })

    # =========================================================
    # Phase 3: ファイル出力
    # =========================================================
    print("\n[3/3] 結果をファイルに書き出しています...")

    txt_path = os.path.join(OUTPUT_DIR, TXT_FILENAME)
    with open(txt_path, "w", encoding="utf-8") as f:
        for page in full_text_data:
            f.write(f"--- Page: {page['filename']} ---\n")
            f.write(page['content'])
            f.write("\n\n")
    
    docx_path = os.path.join(OUTPUT_DIR, DOCX_FILENAME)
    doc = Document()
    doc.add_heading('Hokuto Reviews (PaddleOCR)', 0)
    
    for page in full_text_data:
        doc.add_heading(f"Page: {page['filename']}", level=2)
        if page['content'].strip():
            doc.add_paragraph(page['content'])
        else:
            doc.add_paragraph("(テキストなし)")
            
    doc.save(docx_path)
    
    print(f"\n✅ 完了: {OUTPUT_DIR} を確認してください")

if __name__ == "__main__":
    main()
