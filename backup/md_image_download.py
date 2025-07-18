import os
import re
import argparse
import requests
from pathlib import Path
from urllib.parse import urlparse

def download_image(url, output_dir):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            # 从URL提取文件名，若无效则生成随机文件名
            filename = os.path.basename(urlparse(url).path) or f"image_{hash(url)}.jpg"
            local_path = os.path.join(output_dir, filename)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return local_path
    except Exception as e:
        print(f"[ERROR] Failed to download {url}: {e}")
    return None

def process_markdown(md_path, image_dir):
    # 确保图片目录存在
    Path(image_dir).mkdir(parents=True, exist_ok=True)
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配Markdown图片链接 ![alt](url) 和 HTML <img> 标签
    #pattern = r'!\[(.*?)\]\((.*?)\)|<img.*?src=["\'](.*?)["\'].*?>'
    pattern = r'!\[.*?\]\((.*?)\)'
    matches = re.findall(pattern, content)
    
    for url in matches:
        # 处理 ![alt](url) 或 <img src="url">
        #url = match[1] if match[0] else match[2]
        #print("url:", url)
        if url and url.startswith(('http://', 'https://')):
            local_path = download_image(url, image_dir)
            if local_path:
                # 计算相对于Markdown文件的路径
                relative_path = os.path.relpath(local_path, os.path.dirname(md_path))
                content = content.replace(url, relative_path)
    
    # 保存修改后的内容
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[SUCCESS] Processed: {md_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download external images in Markdown and replace with local paths.")
    parser.add_argument("--md", required=True, help="Path to the Markdown file")
    parser.add_argument("--img-dir", default="images", help="Directory to save downloaded images (default: 'images')")
    args = parser.parse_args()

    if not os.path.isfile(args.md):
        print(f"[ERROR] Markdown file not found: {args.md}")
        exit(1)

    process_markdown(args.md, args.img_dir)
