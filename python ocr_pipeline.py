import os
import glob
import img2pdf
import easyocr
from natsort import natsorted
from docx import Document
from tqdm import tqdm # 進捗バー表示用

# --- 設定 ---
IMAGE_DIR = "./hokuto_scrapes/"   # 画像の保存先
OUTPUT_DIR = "./output"     # 出力先
PDF_FILENAME = "output.pdf"
DOCX_FILENAME = "output.docx"
TXT_FILENAME = "output_raw_text.txt"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. 画像リストの取得とソート
    # natsortedを使うことで page_001 -> page_002 -> page_010 の順序を保証
    img_paths = natsorted(glob.glob(os.path.join(IMAGE_DIR, "*.png")))
    
    if not img_paths:
        print("画像が見つかりません。ディレクトリを確認してください。")
        return

    print(f"画像枚数: {len(img_paths)}枚")

    # ---------------------------------------------------------
    # Step 1: PDF化 (Goodnotesなどで読む用)
    # ---------------------------------------------------------
    print("\n[1/3] PDFを作成しています...")
    pdf_path = os.path.join(OUTPUT_DIR, PDF_FILENAME)
    
    with open(pdf_path, "wb") as f:
        # 画像データをそのままPDFバイナリに変換（劣化なし）
        f.write(img2pdf.convert(img_paths))
    
    print(f" -> PDF保存完了: {pdf_path}")

    # ---------------------------------------------------------
    # Step 2: OCR処理 (EasyOCR by GPU)
    # ---------------------------------------------------------
    print("\n[2/3] OCR処理を開始します (GPU使用)...")
    
    # Githubのコードと同様の設定
    reader = easyocr.Reader(['ja', 'en'], gpu=True)
    
    full_text_lines = []

    for img_path in tqdm(img_paths):
        # detail=0 にするとテキストのリストだけ返ってくる
        # paragraph=True にするとある程度の塊で結合してくれる
        result = reader.readtext(img_path, detail=0, paragraph=True)
        
        # ページごとの区切り文字を入れる（分析時にページを意識させるため）
        full_text_lines.append(f"\n--- Page {os.path.basename(img_path)} ---\n")
        full_text_lines.extend(result)

    # ---------------------------------------------------------
    # Step 3: Word & Text出力
    # ---------------------------------------------------------
    print("\n[3/3] ファイルに出力しています...")

    # A. テキストファイル出力（LLMに投げる用）
    txt_path = os.path.join(OUTPUT_DIR, TXT_FILENAME)
    all_text_str = "\n".join(full_text_lines)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(all_text_str)

    # B. Wordファイル出力（人間が読む用）
    docx_path = os.path.join(OUTPUT_DIR, DOCX_FILENAME)
    doc = Document()
    doc.add_heading('Hokuto Reviews OCR Result', 0)
    
    for line in full_text_lines:
        if line.startswith("--- Page"):
            doc.add_heading(line.strip(), level=2)
        else:
            doc.add_paragraph(line)
            
    doc.save(docx_path)
    
    print(f" -> Text保存完了: {txt_path}")
    print(f" -> Word保存完了: {docx_path}")
    print("\nすべての処理が完了しました。")

if __name__ == "__main__":
    main()
