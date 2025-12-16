import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    options = Options()
    # options.add_argument("--headless") # Odkomentuj dla trybu bez okna
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1920, 1080)
    return driver

def setup_header_stealer(driver):
    """
    Wstrzykuje kod JS, który nasłuchuje na poprawne zapytanie do API
    i zapisuje jego nagłówki do zmiennej globalnej window.CAPTURED_HEADERS.
    """
    script = """
    window.CAPTURED_HEADERS = null;
    const originalFetch = window.fetch;
    
    window.fetch = async function(...args) {
        const [resource, config] = args;
        
        // Sprawdzamy czy zapytanie idzie do API produktów i czy ma nagłówki
        if (resource.includes('api/webproductpagews') && config && config.headers) {
            console.log("Przechwycono nagłówki z zapytania:", resource);
            window.CAPTURED_HEADERS = config.headers;
            
            // Przywracamy oryginał po pierwszym sukcesie, żeby nie śmiecić
            window.fetch = originalFetch;
        }
        return originalFetch(...args);
    };
    """
    driver.execute_script(script)

def wait_for_headers(driver):
    """
    Scrolluje stronę, aby wymusić request i czeka na przechwycenie nagłówków.
    """
    print("--- Próba przechwycenia tokenów sesji (CSRF) ---")
    
    # Scrollujemy w dół, aby strona doładowała produkty i wysłała request
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # Sprawdzamy czy mamy nagłówki (próbujemy przez 10 sekund)
    for _ in range(10):
        headers = driver.execute_script("return window.CAPTURED_HEADERS;")
        if headers:
            print("SUKCES: Przechwycono poprawne nagłówki i tokeny!")
            return headers
        time.sleep(1)
        driver.execute_script("window.scrollBy(0, -200);") # Lekki ruch myszką/scrollem
        
    print("BŁĄD: Nie udało się przechwycić nagłówków. Strona nie wykonała zapytania API.")
    raise Exception("BŁĄD: Nie udało się przechwycić nagłówków. Strona nie wykonała zapytania API.")

def call_auchan_api_secure(driver, uuids: list[str], captured_headers):
    print("--- Pobieranie detali produktów (używając skradzionych nagłówków) ---")
    results = []
    url = "https://zakupy.auchan.pl/api/webproductpagews/v6/products"
    
    # Klonujemy nagłówki i nadpisujemy (lub dodajemy) precyzyjny Content-Type
    base_headers = captured_headers.copy()
    
    # Tego wymaga serwer. Zwróć uwagę na charset.
    base_headers['Content-Type'] = 'application/json; charset=utf-8'
    base_headers['Accept'] = 'application/json; charset=utf-8' # Dodajemy też explicit Accept
    
    for i in range(0, len(uuids), 24):
        batch = uuids[i:i+24]
        
        script = """
        var callback = arguments[arguments.length - 1];
        var url = arguments[0];
        var data = arguments[1];
        var headers = arguments[2]; // Teraz to jest base_headers z poprawnym Content-Type

        fetch(url, {
            method: 'PUT',
            headers: headers, // Używamy poprawnych nagłówków
            body: JSON.stringify(data) // Gwarantuje sformatowanie jako ["id1", "id2", ...]
        })
        .then(async response => {
            if (!response.ok) {
                let text = await response.text();
                callback({status: response.status, error_text: text, is_error: true});
            } else {
                return response.json();
            }
        })
        .then(json => callback(json))
        .catch(err => callback({error: err.toString(), is_error: true}));
        """
        
        try:
            # Przekazujemy teraz base_headers zamiast captured_headers
            response_data = driver.execute_async_script(script, url, batch, base_headers) 
            
            # ... (Reszta obsługi odpowiedzi pozostaje bez zmian) ...
            if isinstance(response_data, dict) and response_data.get('is_error'):
                print(f"Batch {i//24 + 1} BŁĄD: Status {response_data.get('status')} - {response_data.get('error_text')}")
                if response_data.get('status') == 403:
                    print("Krytyczny błąd autoryzacji. Przerywam.")
                    break
            elif isinstance(response_data, list):
                print(f"Batch {i//24 + 1}: Pobrano {len(response_data)} produktów.")
                results.extend(response_data)
            elif isinstance(response_data, dict):
                products = [p for p in response_data['products'] if p['available']]
                print(f"Batch {i//24 + 1}: Pobrano {len(products)} produktów.")
                results.extend(products)
                
            else:
                print(f"Batch {i//24 + 1}: Dziwna odpowiedź: {str(response_data)[:100]}")
                
            time.sleep(1.5)
            
        except Exception as e:
            print(f"Wyjątek Pythona przy batchu {i}: {e}")

    return results

def auchan_get_ids(driver) -> list[str]:
    # Tutaj logika pobierania ID, którą już masz
    # WAŻNE: W tym kroku wstrzykujemy też nasz "nasłuchiwacz"
    
    link = "https://zakupy.auchan.pl/categories"
    driver.get(link)
    
    # Wstrzykujemy szpiega zanim zaczniemy scrollować
    setup_header_stealer(driver)
    
    time.sleep(3) # Czekamy na załadowanie DOM
    
    # Pobieramy ID (z page source)
    page_source = driver.page_source
    matches = re.findall(r'"products":\[".*?"\]', page_source)
    products = []
    if matches:
        for match in matches:
            products_str = match[12:-1].replace('"', "")
            products.extend(products_str.split(","))
            
    products = list(filter(None, set(products)))
    print(f"Znaleziono {len(products)} ID.")
    return products



if __name__ == "__main__":
    from scraper import ProductObj
    driver = init_driver()
    try:
        # 1. Pobieramy ID i przy okazji przygotowujemy "Header Stealer"
        product_ids = auchan_get_ids(driver)
        
        # 2. Wymuszamy na stronie wygenerowanie poprawnych nagłówków
        valid_headers = wait_for_headers(driver)
        products = []
        if product_ids and valid_headers:
            # 3. Używamy tych nagłówków do pobrania naszych danych
            # Testujemy na pierwszych 50 sztukach
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
                products.extend(p)
            # with open("data_auchan_full.json", "w", encoding="utf-8") as fp:
            #     json.dump(details, fp, ensure_ascii=False, indent=4)
            # print(f"Zapisano {len(details)} produktów.")
        else:
            print("Nie udało się pobrać ID lub nagłówków.")
        
        with open("data_auchan_full.json", "w", encoding="utf-8") as fp:
            json.dump(products, fp, ensure_ascii=False, indent=4)
    finally:
        driver.quit()