import json
import requests
from bs4 import BeautifulSoup


class BaseParser:
    """Базовый класс для всех парсеров сайтов."""

    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get_soup(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"Ошибка при загрузке {self.url}: {e}")
            return None

    def parse(self):
        raise NotImplementedError(
            "Метод parse() должен быть переопределен в дочернем классе"
        )


class PizzaTempoParser(BaseParser):
    """Парсер для сайта pizzatempo.by на базе структуры .item_product"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        cards = soup.find_all("div", class_="item_product")

        for card in cards:
            title_tag = card.find("h3")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            desc_tag = card.find("div", class_="composition")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            size_tag = card.find("div", class_="size")
            weight = size_tag.get_text(strip=True) if size_tag else ""

            img_tag = card.find("div", class_="photo").find("img") if card.find("div", class_="photo") else None
            image_url = img_tag.get("src") if img_tag else ""
            if image_url and image_url.startswith("/"):
                image_url = f"https://pizzatempo.by{image_url}"

            price_takeaway_tag = card.find("div", class_="price_takeaway")
            price_takeaway = "Не указана"
            if price_takeaway_tag and price_takeaway_tag.find("span", class_="price_byn"):
                price_takeaway = f"{price_takeaway_tag.find('span', class_='price_byn').get('data-price')} BYN"

            price_delivery = "Не указана"
            price_wrappers = card.find_all("div", class_="price_wrapper")
            for wrap in price_wrappers:
                if "price_takeaway" not in wrap.get("class", []):
                    span_btn = wrap.find("span", class_="price_byn")
                    if span_btn:
                        price_delivery = f"{span_btn.get('data-price')} BYN"

            menu_items.append({
                "title": title,
                "description": description,
                "weight": weight,
                "price_takeaway": price_takeaway,
                "price_delivery": price_delivery,
                "image": image_url
            })

        return menu_items


class VasilkiParser(BaseParser):
    """Парсер для сайта minsk.vasilki.by"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        cards = soup.find_all("div", class_="item_product")

        for card in cards:
            title_tag = card.find("h3")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            desc_tag = card.find("div", class_="composition")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            size_tag = card.find("div", class_="size")
            weight = size_tag.get_text(strip=True) if size_tag else ""

            img_tag = card.find("div", class_="photo").find("img") if card.find("div", class_="photo") else None
            image_url = img_tag.get("src") if img_tag else ""
            if image_url and image_url.startswith("/"):
                image_url = f"https://vasilki.by{image_url}"

            price_takeaway_tag = card.find("div", class_="price_takeaway")
            price_takeaway = "Не указана"
            if price_takeaway_tag and price_takeaway_tag.find("span", class_="price_byn"):
                price_takeaway = f"{price_takeaway_tag.find('span', class_='price_byn').get('data-price')} BYN"

            price_delivery = "Не указана"
            price_wrappers = card.find_all("div", class_="price_wrapper")
            for wrap in price_wrappers:
                if "price_takeaway" not in wrap.get("class", []):
                    span_btn = wrap.find("span", class_="price_byn")
                    if span_btn:
                        price_delivery = f"{span_btn.get('data-price')} BYN"

            menu_items.append({
                "title": title,
                "description": description,
                "weight": weight,
                "price_takeaway": price_takeaway,
                "price_delivery": price_delivery,
                "image": image_url
            })

        return menu_items


class EdaMarketParser(BaseParser):
    """Парсер для сайта edamarket.by на базе структуры .product-thumb"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        cards = soup.find_all("div", class_="product-thumb")

        for card in cards:
            caption = card.find("div", class_="caption")
            if not caption:
                continue

            # Название блюда
            title_tag = caption.find("h4")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # Описание/Состав (первый тег p внутри caption)
            desc_tag = caption.find("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Вес/Выход из таблицы характеристик
            weight = ""
            table = caption.find("table")
            if table:
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) == 2 and "Выход" in cells[0].get_text():
                        weight = f"{cells[1].get_text(strip=True)} г"
                        break

            # Цена
            price_tag = caption.find(class_="price")
            price = price_tag.get_text(strip=True) if price_tag else "Не указана"

            # Ссылка на изображение
            image_url = ""
            img_container = card.find("div", class_="image")
            if img_container:
                img_tag = img_container.find("img")
                if img_tag:
                    image_url = img_tag.get("src", "")

            menu_items.append({
                "title": title,
                "description": description,
                "weight": weight,
                "price_takeaway": price,
                "price_delivery": price,  # Для единого формата выгрузки
                "image": image_url
            })

        return menu_items


class TerraPizzaParser(BaseParser):
    """Парсер для сайта terrapizza.by на основе классов карточек"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        cards = soup.find_all("div", class_="menu-card")

        for card in cards:
            title_tag = card.find(class_="menu-card__title")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            desc_tag = card.find(class_="menu-card__notice")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            price_val_tag = card.find(class_="price-val")
            price = f"{price_val_tag.get_text(strip=True)} BYN" if price_val_tag else "Не указана"

            weight_tag = card.find(class_="product-weight")
            weight = weight_tag.get_text(strip=True) if weight_tag else ""

            img_tag = card.find("div", class_="menu-card__img").find("img") if card.find("div", class_="menu-card__img") else None
            image_url = img_tag.get("src") if img_tag else ""

            menu_items.append({
                "title": title,
                "description": description,
                "weight": weight,
                "price_takeaway": price,
                "price_delivery": price,
                "image": image_url
            })

        return menu_items


# =====================================================================
# КАРТА ПАРСЕРОВ
# =====================================================================
PARSERS_MAP = {
    "https://www.pizzatempo.by/menu/obed.html": PizzaTempoParser,
    "https://minsk.vasilki.by/menu/obed.html": VasilkiParser,
    "https://edamarket.by": EdaMarketParser,
    "https://terrapizza.by/catalog/lunch": TerraPizzaParser,
}


def main():
    all_menus = {}

    print("=== ЗАПУСК ПАРСЕРА ОБЕДЕННЫХ МЕНЮ ===\n")

    for url, ParserClass in PARSERS_MAP.items():
        print(f"Обработка: {url}")
        parser = ParserClass(url)
        menu = parser.parse()

        all_menus[url] = menu
        print(f"-> Успешно собрано блюд: {len(menu)}")
        print("-" * 50)

    output_filename = "all_lunch_menus.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_menus, f, ensure_ascii=False, indent=4)

    print(f"\n[ГОТОВО] Все структурированные меню сохранены в: {output_filename}")


if __name__ == "__main__":
    main()
 