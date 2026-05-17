import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin

# ======================== настройки ========================

BASE_URL = 'https://mashina.kg'
CATALOG_URL = f'{BASE_URL}/search/passenger'

OUTPUT_FILE = 'mashina_kg.csv'

DELAY_SEC = 1.5
PAGE_TO_PARSE = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ======================== загрузка html ========================

def fetch_html(url: str, retries: int = 3) -> str | None:

    for attempt in range(1, retries + 1):

        try:
            response = SESSION.get(url, timeout=15)

            response.raise_for_status()

            return response.text

        except requests.RequestException as e:

            print(f'Ошибка {attempt}/{retries} -> {url}: {e}')

            if attempt == retries:
                return None

            time.sleep(2 ** attempt)

    return None

# ======================== очистка ========================

def extract_digits(text: str) -> int | None:

    if not text:
        return None

    digits = re.sub(r'\D', '', text)

    return int(digits) if digits else None

def extract_year_and_mileage(text: str):

    """
    2019/113413 km
    """

    year = None
    mileage = None

    if not text:
        return year, mileage

    match = re.search(r'(\d{4})\s*/\s*([\d\s]+)', text)

    if match:

        year = int(match.group(1))

        mileage = extract_digits(match.group(2))

    return year, mileage

# ======================== пагинация ========================

def get_total_pages(soup: BeautifulSoup) -> int:

    pages = []

    for button in soup.select('button.pagination_button'):

        text = button.get_text(strip=True)

        if text.isdigit():
            pages.append(int(text))

    return max(pages) if pages else 1

# ======================== парсинг карточки ========================

def parse_card(card) -> dict | None:

    href = card.get('href', '')

    if not href.startswith('/details/'):
        return None

    full_url = urljoin(BASE_URL, href)

    # ===================== Название =====================

    title_tag = card.find('h3')

    title = title_tag.get_text(strip=True) if title_tag else None

    # ===================== Картинки =====================

    img_tag = card.find('img')

    image_url = ''

    if img_tag:
        image_url = img_tag.get('src', '')

    # ===================== Город =====================

    city = None

    city_tag = card.select_one('span.text-white')

    if city_tag:
        city = city_tag.get_text(strip=True)

    # ===================== year mileage =====================

    year = None
    mileage_km = None

    year_mileage_tag = card.select_one('span.whitespace-nowrap.shrink-0')

    if year_mileage_tag:

        year, mileage_km = extract_year_and_mileage(
            year_mileage_tag.get_text(" ", strip=True)
        )

    # ===================== prices =====================

    price_kgs = None
    price_usd = None

    spans = card.find_all('span')

    for span in spans:

        text = span.get_text(" ", strip=True)

        if '$' in text and price_usd is None:
            price_usd = extract_digits(text)

        if '⃀' in text and price_kgs is None:
            price_kgs = extract_digits(text)

    # ===================== engine transmission =====================

    engine = None
    transmission = None

    for span in spans:

        text = span.get_text(" ", strip=True)

        if ' / ' in text and 'л.' in text:

            parts = text.split('/')

            if len(parts) == 2:

                engine = parts[0].strip()

                transmission = parts[1].strip()

                break

    return {
        'url': full_url,
        'title': title,
        'price_usd': price_usd,
        'price_kgs': price_kgs,
        'year': year,
        'mileage_km': mileage_km,
        'engine': engine,
        'transmission': transmission,
        'city': city,
        'image_url': image_url,
    }

# ======================== парсинг страницы ========================

def parse_page(html: str) -> list[dict]:

    soup = BeautifulSoup(html, 'lxml')

    cars = []

    cards = soup.select('a[href*="/details/"]')

    for card in cards:

        parsed = parse_card(card)

        if parsed:
            cars.append(parsed)

    return cars

# ======================== главный парсер ========================

def fetch_all_pages(max_pages: int):

    all_cars = []

    unique_urls = set()

    first_html = fetch_html(CATALOG_URL)

    if not first_html:
        print('Не удалось получить первую страницу')
        return []

    soup = BeautifulSoup(first_html, 'lxml')

    total_pages = get_total_pages(soup)

    print(f'Всего страниц: {total_pages}')

    if max_pages:
        total_pages = min(total_pages, max_pages)

    # ======================== цикл ========================

    for page_num in range(1, total_pages + 1):

        if page_num == 1:
            html = first_html
        else:

            url = f'{CATALOG_URL}?page={page_num}'

            html = fetch_html(url)

        if not html:

            print(f'Пропуск страницы {page_num}')

            continue

        cars = parse_page(html)

        added = 0

        for car in cars:

            if car['url'] not in unique_urls:

                unique_urls.add(car['url'])

                all_cars.append(car)

                added += 1

        print(f'Страница {page_num}: +{added} машин')

        time.sleep(DELAY_SEC)

    return all_cars

# ======================== csv ========================

def save_to_csv(data, filename):

    df = pd.DataFrame(data)

    df.to_csv(
        filename,
        index=False,
        encoding='utf-8-sig'
    )

# ======================== main ========================

if __name__ == '__main__':

    cars = fetch_all_pages(PAGE_TO_PARSE)

    save_to_csv(cars, OUTPUT_FILE)

    print(f'Сохранено машин: {len(cars)}')