import requests
import pytesseract
from env import TESSERACT_DIR
from PIL import Image
import os
from typing import Union, TypedDict, Callable
import json
from bs4 import BeautifulSoup
from thefuzz import fuzz
from biedronka_leaflets import biedronka_ocr
from auchan import *


__all__ = (
    "get_shops_data",
    "ProductObj"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_DIR
StrOrBytesPath = Union[str | bytes | os.PathLike[str] | os.PathLike[bytes]]

def find_best_product_match(target_product:str, ocr_results:list[str]) -> dict:
    """
    Szuka najlepiej pasującego produktu w liście wyników OCR.
    
    Args:
        target_product (str): Czysta nazwa produktu z bazy (np. "Mleko Mlekovita")
        ocr_results (list): Lista brudnych stringów z OCR.
        
    Returns:
        dict: {"index": -1,
                "ocr_text": "",
                "score": 0}
    """
    best_match = {
        "index": -1,
        "ocr_text": "",
        "score": 0
    }

    clean_target = target_product.lower()

    for i, ocr_raw in enumerate(ocr_results):
        if not ocr_raw: continue # Pomiń puste

        # Używamy token_set_ratio - to jest "magiczna kula" na brudny OCR.
        # Ignoruje powtórzenia słów, kolejność i dodatkowe śmieci w stringu.
        score = fuzz.token_set_ratio(clean_target, ocr_raw)

        # Opcjonalnie: partial_ratio jest dobry, gdy słowa są w idealnej kolejności, 
        # ale w OCR często "Mlekovita" ląduje w linii pod "Mleko", więc token_set jest bezpieczniejszy.
        
        if score > best_match["score"]:
            best_match["score"] = score
            best_match["index"] = i
            best_match["ocr_text"] = ocr_raw

    return best_match

    
class ProductObj(TypedDict):
    Name:str
    Price:str
    Url:str
    Details:str
    Is_Discounted:bool
    Discounted_Price:str|None

biedronka_ids = {
    "Łódź Pabianicka, 77": "1vky6jn8e",
    "Łódź Krokusowa, 1": "1vky6jn8e",
    "Łódź Politechniki, 60": "irthpct6j",
    "Łódź Łazowskiego, 44": "irthpct6j",
    "Łódź Dostojewskiego, 2": "irthpct6j",
    "Łódź Kusocińskiego, 137": "irthpct6j"
}

lidl_ids = {
    "kuchnia,-sprzatanie-i-organizacja": 10067764,
    "warsztat-i-ogrod": 10067761,
    "sport-i-rekreacja": 10067763,
    "dom-i-wyposazenie-wnetrz": 10067762,
    "moda-i-akcesoria": 10067765,
    "produkty-niemowle-dziecko-i-zabawki": 10067767,
    "zywnosc-i-napoje": 10068374,
}


def call_biedronka(shop_id=biedronka_ids["Łódź Politechniki, 60"]) -> list[ProductObj]:
    products:list[ProductObj] = []
    for i in range(15): # weird shit, 12 is enough, but maybe something changes
        products += call_biedronka_page(i)
    print(f"Biedronka products found: {len(products)}")
    ocr_text_urls:list[tuple[str, str]] = biedronka_ocr(shop_id)
    ocrs = [item[0] for item in ocr_text_urls]
    for item in products:
        result = find_best_product_match(item["Name"], ocrs)
        if result["score"] > 85:
            item["Is_Discounted"] = True
            item["Details"] = ocr_text_urls[result["index"]][1]
    return products

def call_biedronka_page(page:int) -> list[ProductObj]:
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
            raise Exception("Lidl failed")
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
        print(f"Lidl category {id}: length:{len(l)}")
        products += l
    return products

def call_auchan():
    driver = init_driver()
    products = []
    try:
        product_ids = auchan_get_ids(driver)
        valid_headers = wait_for_headers(driver)
        if product_ids and valid_headers:
            details = call_auchan_api_secure(driver, product_ids, valid_headers)
            for det in details:
                p:ProductObj = {
                    "Name": det['name'],
                    "Price": det["price"]["amount"],
                    "Details": det["promotions"][0].get('description', "") if len(det["promotions"]) > 0 else "",
                    "Url": "",
                    "Is_Discounted": len(det["promotions"]) > 0, # fail
                    "Discounted_Price": det.get('promoPrice', {}).get('amount', None)
                }
                products.append(p)
        else:
            print("Nie udało się pobrać ID lub nagłówków.")
            raise Exception("Nie udało się pobrać ID lub nagłówków.")
    finally:
        driver.quit()
    return products

def retry_call(func:Callable, retries=5, delay=5):
    for i in range(retries + 1):
        try:
            return func()
        except Exception as e:
            if i == retries:
                raise
            print(f"Call to {func.__name__} failed, retrying...")
            time.sleep(delay)

def get_shops_data(biedronka_address:str="")->dict:
    b_id=biedronka_ids.get(biedronka_address, biedronka_ids["Łódź Politechniki, 60"])
    a = retry_call(call_auchan)
    b = call_biedronka(b_id)
    l = call_lidl()
    return {
        "Auchan": a,
        "Biedronka": b,
        "Lidl": l,
    } 

if __name__ == "__main__":
    with open("out.json", "w") as fp:
        fp.write(json.dumps(get_shops_data()))
