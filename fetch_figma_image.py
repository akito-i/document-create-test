import os
import requests
import time

# --- 設定 ---
FILE_KEY = 'bxE0kCXyrW8ouvarTmHbz6'
NODE_ID = '3-83' # URLのまま(ハイフン)でOKです
OUTPUT_DIR = 'marp'
IMAGE_DIR_NAME = 'images'
OUTPUT_FILENAME = 'figma_image_slide.md'
IMAGE_FILENAME = 'figma_import.png'
# ------------

FIGMA_API_KEY = os.environ.get("FIGMA_API_KEY")
if not FIGMA_API_KEY:
    print("Error: FIGMA_API_KEY not found.")
    exit(1)

# ディレクトリ準備
image_output_dir = os.path.join(OUTPUT_DIR, IMAGE_DIR_NAME)
os.makedirs(image_output_dir, exist_ok=True)
md_output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
image_save_path = os.path.join(image_output_dir, IMAGE_FILENAME)

headers = {"X-Figma-Token": FIGMA_API_KEY}

print(f"Requesting image rendering for node {NODE_ID}...")

# 1. 画像レンダリングAPIを叩く
# APIリクエスト時はハイフンのままでもFigmaが解釈してくれます
render_url = f"https://api.figma.com/v1/images/{FILE_KEY}?ids={NODE_ID}&format=png&scale=2"

try:
    response = requests.get(render_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    api_node_id = NODE_ID.replace('-', ':')
    
    image_url = data['images'].get(api_node_id)
    
    # 万が一、元のID(ハイフン)で返ってきた場合の保険
    if not image_url:
        image_url = data['images'].get(NODE_ID)

    if not image_url:
        print(f"Error: Failed to generate image URL for node {NODE_ID} (checked as {api_node_id}).")
        print(f"API Response: {data}")
        exit(1)
    # ----------------------------------------
        
    print(f"Image rendered. Downloading from: {image_url}")

    # 2. 画像の実データをダウンロード
    time.sleep(2)
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    
    with open(image_save_path, 'wb') as f:
        f.write(image_response.content)
        
    print(f"Image saved to: {image_save_path}")

except requests.exceptions.RequestException as e:
    print(f"Error during image fetching process: {e}")
    exit(1)


# 3. Marp用Markdownの生成
print(f"Generating Marp markdown at {md_output_path}...")

markdown_content = f"""---
marp: true
theme: default
paginate: true
style: |
  section {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
  }}
  img {{
    max-width: 80%;
    max-height: 80%;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }}
---

# Figma インポート結果
（Node ID: `{NODE_ID}`）

---

![]({IMAGE_DIR_NAME}/{IMAGE_FILENAME})

"""

with open(md_output_path, 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("Successfully generated output files.")