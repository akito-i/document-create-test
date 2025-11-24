import os
import time
import glob
import google.generativeai as genai

# --- 設定 ---
SOURCE_DIR = 'specs'  # 仕様書を入れるフォルダ
OUTPUT_DIR = 'marp'   # スライドが出力されるフォルダ
MODEL_NAME = 'gemini-2.5-flash' # エラーが出る場合は 'gemini-1.5-flash'
# ------------

# APIキーの設定
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    # ローカルテスト用に環境変数がない場合は警告を出して終了
    print("Warning: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel(MODEL_NAME)

# 出力ディレクトリの作成
os.makedirs(OUTPUT_DIR, exist_ok=True)

# specフォルダ内のMarkdownファイルをすべて取得
source_files = glob.glob(os.path.join(SOURCE_DIR, "*.md"))

if not source_files:
    print(f"No markdown files found in {SOURCE_DIR}/")
    exit(0)

print(f"Checking {len(source_files)} files in '{SOURCE_DIR}'...")

for source_path in source_files:
    filename = os.path.basename(source_path)
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    # 1. 更新チェック (スライドが既にあり、かつ仕様書より新しい場合はスキップ)
    if os.path.exists(output_path):
        source_mtime = os.path.getmtime(source_path)
        output_mtime = os.path.getmtime(output_path)
        
        if output_mtime > source_mtime:
            print(f"[SKIP] {filename} (No changes detected)")
            continue

    print(f"[PROCESSING] {filename} ...")

    # 2. 仕様書の読み込み
    with open(source_path, 'r', encoding='utf-8') as f:
        spec_content = f.read()

    # 3. プロンプト作成
    prompt = f"""
    あなたは優秀なプレゼンテーション作成者です。
    以下の仕様書をもとに、Marp用のスライド資料を作成してください。

    【重要：出力形式】
    - 出力は**Marp対応のMarkdownコードのみ**にしてください。
    - 冒頭の ```markdown や 末尾の ``` は不要です。
    - 先頭には必ず以下のヘッダーを付けてください。
    ---
    marp: true
    theme: default
    paginate: true
    ---

    【仕様書の内容】
    {spec_content}
    """

    # 4. 生成実行
    try:
        # レート制限対策（連続実行時のウェイト）
        time.sleep(5)
        
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```markdown", "").replace("```", "").strip()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        
        print(f" -> Generated: {output_path}")

    except Exception as e:
        print(f" -> Error processing {filename}: {e}")

print("All tasks finished.")