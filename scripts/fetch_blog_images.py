#!/usr/bin/env python3
import json
import os
import re
import sys
from urllib.parse import urljoin, urlparse, quote_plus
from urllib.request import urlopen, Request, urlretrieve

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'blogs.json')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'images', 'blogs')

OG_PATTERNS = [
    re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', re.I),
]

def slugify(text: str) -> str:
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
    return text or 'image'

def guess_ext(url: str) -> str:
    path = urlparse(url).path
    _, _, name = path.rpartition('/')
    _, dot, ext = name.rpartition('.')
    if dot and ext:
        ext = ext.split('?')[0].split('#')[0]
        if len(ext) <= 5:
            return '.' + ext
    return '.jpg'

def find_image_url(html: bytes, base_url: str) -> str:
    text = html.decode('utf-8', errors='ignore')
    for pat in OG_PATTERNS:
        m = pat.search(text)
        if m:
            src = m.group(1).strip()
            if src:
                return urljoin(base_url, src)
    # Fallback: link rel="image_src"
    m = re.search(r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)["\']', text, re.I)
    if m:
        return urljoin(base_url, m.group(1).strip())
    # Fallback: first <img> tag
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.I)
    if m:
        return urljoin(base_url, m.group(1).strip())
    return ''

def fetch(url: str) -> bytes:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read()
    except Exception:
        # Fallback via read-only proxy that returns readable HTML
        proxy_url = 'https://r.jina.ai/http/' + url
        req2 = Request(proxy_url, headers={'User-Agent': headers['User-Agent']})
        with urlopen(req2, timeout=20) as resp2:
            return resp2.read()

def main():
    data_path = os.path.abspath(DATA_PATH)
    out_dir = os.path.abspath(OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)

    with open(data_path, 'r', encoding='utf-8') as f:
        items = json.load(f)

    updated = False
    # Simple keyword mapping for fallback images
    keyword_map = {
        'zookeeper': 'zookeeper,distributed systems',
        'project management': 'project management,ai,planning',
        'chess': 'chess,board',
        'scikit': 'machine learning,python,code',
        'small data': 'data,statistics,analytics',
    }
    for i, item in enumerate(items):
        url = item.get('url')
        title = item.get('title') or f'post-{i+1}'
        if not url:
            continue
        try:
            html = fetch(url)
            img_url = find_image_url(html, url)
            if not img_url:
                # Fallback: fetch a related image from Unsplash by keyword
                lower = title.lower()
                kw = None
                for key, val in keyword_map.items():
                    if key in lower:
                        kw = val
                        break
                if not kw:
                    # generic keyword
                    kw = 'technology,blog'
                # Use picsum placeholder seeded by title for stable unique images
                seed = quote_plus(title)
                img_url = f"https://picsum.photos/seed/{seed}/800/500"
                print(f"[info] Using fallback image for '{title}' via picsum")
            fname = slugify(title) + guess_ext(img_url)
            out_path = os.path.join(out_dir, fname)
            urlretrieve(img_url, out_path)
            rel_path = os.path.relpath(out_path, os.path.join(os.path.dirname(__file__), '..'))
            rel_path = rel_path.replace('\\', '/').replace('\\', '/')
            if item.get('image') != rel_path:
                item['image'] = rel_path
                updated = True
            print(f"[ok] {title} -> {rel_path}")
        except Exception as e:
            print(f"[error] {title}: {e}")

    if updated:
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"Updated {data_path}")
    else:
        print("No updates to blogs.json")

if __name__ == '__main__':
    sys.exit(main())
