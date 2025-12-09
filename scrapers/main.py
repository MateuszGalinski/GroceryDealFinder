import requests
import pytesseract
from env import TESSERACT_DIR
from PIL import Image
import os
from typing import Union, TypedDict
import json
from bs4 import BeautifulSoup
import re

__all__ = [
    "get_shops_data",
    "ProductObj"
]

# pytesseract.pytesseract.tesseract_cmd = TESSERACT_DIR
# StrOrBytesPath = Union[str | bytes | os.PathLike[str] | os.PathLike[bytes]]

# def text_from_image(path:StrOrBytesPath):
#     return pytesseract.image_to_string(Image.open(path), lang="pol")
    # print(text_from_image('kakałko.jpg'))
    
class ProductObj(TypedDict):
    Name:str
    Price:str
    Url:str
    Details:str
    Is_Discounted:bool
    Discounted_Price:str|None


def call_biedronka() -> list:
    j = []
    for i in range(15):
        j += call_biedronka_page(i)
    print(len(j))
    return j

def call_biedronka_page(page:int) -> list[dict]:
    r = requests.get(f"https://zakupy.biedronka.pl/polecane/?page={page}")
    if not r.ok:
        raise RuntimeError(f"NOT OK \n {r.raw}")
    soup = BeautifulSoup(r.text, features="html.parser")
    products_list = []

    for tile in soup.select("div.product-tile.js-product-tile"):
        link_tag = tile.select_one("a.product-tile-clickable.js-product-link")
        name_tag = tile.select_one("div.product-tile__name")
        price_tag = tile.select_one("div.price-tile__sales")
        details_tag = tile.select_one("div.packaging-details")

        if link_tag and name_tag and price_tag:
            price_text = price_tag.get_text(separator=" ", strip=True)
            price_text = price_text.replace(" ", ".", 1)
            details_text = details_tag.get_text(" ", strip=True) if details_tag else ""
            link = link_tag["href"]
            assert isinstance(link, str)
            product:ProductObj = {
                "Name": name_tag.get_text(strip=True),
                "Price": price_text,
                "Url": link,
                "Details": details_text,
                "Is_Discounted": False,
                "Discounted_Price": None
            }
            products_list.append(product)

    # return json.dumps(products_list, ensure_ascii=False, indent=2)
    return products_list

# def carrefour_init() -> tuple[requests.Session, dict]:
#     session = requests.Session()

#     headers = {
#         "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#         "Accept": "application/json, text/plain, */*",
#         "Referer": "https://www.carrefour.pl/",
#         "Origin": "https://www.carrefour.pl",
#         "x-requested-with": "XMLHttpRequest",
#         "Accept-Language": "pl-PL,pl;q=0.9",
#     }

#     session.get("https://www.carrefour.pl/", headers=headers)

#     return session, headers

# def call_carrefour_page(page:int, session: requests.Session, headers:dict):
#     link = f"https://www.carrefour.pl/web/catalog?sort=-popularity&available=true&categorySlugs=artykuly-spozywcze&resolveAttributes=false&resolveBrands=false&resolveProductLabels=false&resolveCreateDate=now-30d%2Fd&page={page}"
#     print(link)
#     r = session.get(link, headers=headers)
#     if not r.ok:
#         raise RuntimeError(f"NOT OK \n {r.status_code}")
    
#     products_list = []
#     with open("a.json", "w") as fp:
#         fp.write(r.json())

lidl_ids = {
    "kuchnia,-sprzatanie-i-organizacja": 10067764,
    "warsztat-i-ogrod": 10067761,
    "sport-i-rekreacja": 10067763,
    "dom-i-wyposazenie-wnetrz": 10067762,
    "moda-i-akcesoria": 10067765,
    "produkty-niemowle-dziecko-i-zabawki": 10067767,
    "zywnosc-i-napoje": 10068374,
}


def call_lidl_page(offset:int=0, category_id:int=10068374) -> dict:
    link = f"https://www.lidl.pl/q/api/search?offset={offset}&fetchsize=1000&locale=pl_PL&assortment=PL&version=2.1.0&store=1&category.id={category_id}"
    r = requests.get(link)
    if not r.ok:
        raise RuntimeError(f"NOT OK \n {r.raw}")
    return r.json()


def parse_lidl(resp):
    products_list = []
    for i in resp["items"]:
        try:
            data = i["gridbox"]["data"] if "data" in i["gridbox"].keys() else i["gridbox"]
            # if "Solevita Sok 100% pomar" in data["fullTitle"]:
            #     pass
            lidlPlus:list = data.get("lidlPlus", [])
            if "oldPrice" in data["price"] and "price" in data["price"]:
                old_price = data["price"]["oldPrice"]
                price = data["price"]["price"]
                if old_price == 0.0:
                    old_price = price
                    price = None
            else:
                old_price:float|None = data.get("price", dict()).get("price", None)
                price=None
            if old_price is None:
                if len(lidlPlus) > 0:
                    old_price = data["lidlPlus"][0]["price"]["oldPrice"] if "oldPrice" in data["lidlPlus"][0]["price"] else None
                    price = data["lidlPlus"][0]["price"]["price"]
                else:
                    print(json.dumps(i))
                    raise KeyError("No price found")
            if len(lidlPlus):
                details = lidlPlus[0].get("price").get("discount").get("discountText") or "" + lidlPlus[0].get("highlightText") or ""
            else:
                details = ""
            product:ProductObj = {
                "Url": "https://www.lidl.pl" + data["canonicalUrl"],
                "Name": data["fullTitle"],
                "Price": str(old_price) if old_price else str(price),
                "Details": details,
                "Is_Discounted": bool(price),
                "Discounted_Price": str(price) if price else None
            }
        except:
            print(json.dumps(i))
            raise
        products_list.append(product)
    return products_list


def call_lidl_category(category_id:int):
    off = 0
    list_of_products = []
    while True:
        resp = call_lidl_page(off, category_id=category_id)
        if "items" not in resp.keys():
            return list_of_products
        off += len(resp["items"])
        a = parse_lidl(resp)
        list_of_products += a

def call_lidl():
    products = []
    for id in lidl_ids.values():
        l = call_lidl_category(id)
        print(len(l))
        products += l
    return products


def auchan_init(session:requests.Session) -> tuple[list[str], requests.Session]:
    headers = {
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language":"pl,en-US;q=0.9,en;q=0.8",
    "cache-control":"max-age=0",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 OPR/124.0.0.0"
    }
    link = "https://zakupy.auchan.pl/categories"
    session.headers=headers
    r = session.get(link)

    xsrf_token = session.cookies.get('XSRF-TOKEN')
    if xsrf_token:
        session.headers.update({'X-XSRF-TOKEN': xsrf_token})
        print(f"Znaleziono i ustawiono X-XSRF-TOKEN: {xsrf_token[:10]}...")
    else:
        print("UWAGA: Nie znaleziono ciasteczka XSRF-TOKEN via cookies.get")

    session.headers.update({
        "Origin": "https://zakupy.auchan.pl",
        "Referer": "https://zakupy.auchan.pl/categories",
        "Content-Type": "application/json"
    })

    matches = re.findall(r'"products":\[".*?"\]', r.text)
    if not matches:
        print("Substring not found")
        return ([], session)
    products = []
    
    for match in matches:
        products_str = match[12:]  
        products_str = products_str.replace('"', "") 
        products_list = products_str.split(",")  
        products.extend(products_list)
    print(len(products))
    print(products[0:3])
    return products, session

def call_auchan_api(uuids:list[str], session:requests.Session):
    for i in range(0, len(uuids), 24):
        batch = uuids[i:i+24]
        resp = session.put(
            "https://zakupy.auchan.pl/api/webproductpagews/v6/products",
            json=batch,
        )
        print(resp.json())
    
def get_shops_data():
    b = call_biedronka()
    l = call_lidl()
    return {
        "Biedronka": b,
        "Lidl": l
    }

if __name__ == "__main__":
    # session = requests.Session()
    # call_auchan_api(*auchan_init(session))
    with open("data.json", "w") as fp:
        fp.write(json.dumps(get_shops_data()))
