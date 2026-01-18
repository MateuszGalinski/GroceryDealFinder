import requests
import os
import sys
from PIL import Image
from io import BytesIO
import re
try:
    from scrapers.biedronka_ocr import extract_text
except:
    from biedronka_ocr import extract_text


API_URL = "https://leaflet-api.prod.biedronka.cloud/api/leaflets/{id}?ctx=web"

OUTPUT_DIR = "biedronka_pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_leaflet_id(shop_id:str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pl,en-US;q=0.9,en;q=0.8",
    }
    link = f"https://www.biedronka.pl/pl/press,id,{shop_id}"
    r = requests.get(link, headers=headers)
    leaflet_match = re.search(r'window.galleryLeaflet.init\("(.*?)"\)', r.text)
    assert leaflet_match, "Leaflet not found"
    leaflet = leaflet_match.group(1)
    return leaflet

def get_leaflet_data(leaflet_id):
    url = API_URL.format(id=leaflet_id)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def extract_image_urls(data):
    images = []
    for page in data.get("images_desktop", []):
        for img in page.get("images", []):
            if img and img.startswith("http"):
                images.append(img)
    return images

def download_image(url, idx):
    # print(f"Pobieram stronę {idx}: {url}")
    r = requests.get(url)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content))
    path = os.path.join(OUTPUT_DIR, f"page_{idx}.png")
    img.save(path)
    return path
    

def biedronka_ocr(shop_id="irthpct6j") -> list[tuple[str, str]]:
    """out: [(text, url)]"""
    l_id = get_leaflet_id(shop_id)
    data = get_leaflet_data(l_id)
    image_urls = extract_image_urls(data)

    # print(f"Znaleziono {len(image_urls)} stron.")
    all_results = []

    for i, url in enumerate(image_urls):
        sys.stdout.write('\r')
        sys.stdout.write("Leaflet %d" % (i+1))
        sys.stdout.flush()
        img_path = download_image(url, i)
        text = extract_text(img_path)
        all_results.append((text, url))
    return all_results

if __name__ == "__main__":
    print(biedronka_ocr())
