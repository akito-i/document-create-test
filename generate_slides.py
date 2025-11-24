import os
import time
import google.generativeai as genai

# APIキーの設定
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key not found. Please set GEMINI_API_KEY in secrets.")

genai.configure(api_key=api_key)

# モデル設定 (Gemini 2.5 Flash)
# ※万が一エラーが出る場合は 'gemini-1.5-flash' に変更してください
model = genai.GenerativeModel('gemini-2.5-flash')

# 仕様書の読み込み
try:
    with open('spec.md', 'r', encoding='utf-8') as f:
        spec_content = f.read()
except FileNotFoundError:
    print("Error: spec.md not found.")
    exit(1)

# プロンプト（Marp形式での出力を強力に指示）
prompt = f"""
あなたは優秀なプレゼンテーション作成者です。
以下の仕様書をもとに、スライド資料を作成してください。

【重要：出力形式】
- 出力は**Marp対応のMarkdownコードのみ**にしてください。
- 冒頭の ```markdown や 末尾の ``` は不要です。そのままファイルに保存できる形式で出力してください。
- 先頭には必ず以下のヘッダーを付けてください。
---
marp: true
theme: default
paginate: true
---

【スライド構成の指示】
1. **表紙**: アプリ名と「仕様説明資料」というタイトル
2. **概要**: 箇条書きで簡潔に
3. **ターゲット**: アイコンなどを活用（絵文字で代用可）
4. **機能一覧**: 重要な機能を強調
5. **スケジュール**: 矢印などを使って流れを表現
6. **まとめ**: 今後のアクション

【仕様書の内容】
{spec_content}
"""

print("Generating slides with Gemini...")

# レート制限対策（念のため5秒待機）
time.sleep(5)

try:
    response = model.generate_content(prompt)
    
    # 結果を保存
    # GeminiがMarkdownコードブロック記号を含めて返すことがあるため削除処理
    clean_text = response.text.replace("```markdown", "").replace("```", "").strip()

    with open('slides.md', 'w', encoding='utf-8') as f:
        f.write(clean_text)
    
    print("Success! 'slides.md' has been generated.")

except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)