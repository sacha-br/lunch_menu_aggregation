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
            # Автоматически определяем корректную кодировку (актуально для кириллицы)
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
    """Парсер для сайта pizzatempo.by"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        headers = soup.find_all("h3")

        for h3 in headers:
            title = h3.get_text(strip=True)
            if (
                not title
                or "Выберите город" in title
                or "Доставка из" in title
            ):
                continue

            parent = h3.parent
            desc_tag = parent.find("p") or h3.find_next_sibling("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Ищем цену (в структуре сайта обычно указана в формате "Xр. Yк.")
            price_tag = parent.find(
                text=lambda t: "р." in t or "BYN" in t
            ) or parent.find("span", class_="price")
            price = price_tag.strip() if price_tag else "Не указана"

            menu_items.append(
                {"title": title, "description": description, "price": price}
            )

        return menu_items


class VasilkiParser(BaseParser):
    """Парсер для сайта minsk.vasilki.by"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        # Платформа идентична Пицца Темпо, парсинг аналогичен
        headers = soup.find_all("h3")

        for h3 in headers:
            title = h3.get_text(strip=True)
            if (
                not title
                or "Выберите город" in title
                or "Доставка из" in title
            ):
                continue

            parent = h3.parent
            desc_tag = parent.find("p") or h3.find_next_sibling("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            price_tag = parent.find(
                text=lambda t: "р." in t or "BYN" in t
            ) or parent.find("span", class_="price")
            price = price_tag.strip() if price_tag else "Не указана"

            menu_items.append(
                {"title": title, "description": description, "price": price}
            )

        return menu_items


class EdaMarketParser(BaseParser):
    """Парсер для сайта edamarket.by"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        headers = soup.find_all("h4")

        for item in headers:
            title = item.get_text(strip=True)
            if not title:
                continue

            parent = item.parent

            # Извлечение описания состава
            desc_text = item.next_sibling
            description = (
                desc_text.strip()
                if desc_text and isinstance(desc_text, str)
                else ""
            )
            if not description:
                p_tag = parent.find("p")
                description = p_tag.get_text(strip=True) if p_tag else ""

            # Извлечение стоимости
            price_tag = parent.find("strong") or parent.find(
                text=lambda t: "BYN" in t
            )
            price = (
                price_tag.get_text(strip=True)
                if hasattr(price_tag, "get_text")
                else (price_tag.strip() if price_tag else "Не указана")
            )

            menu_items.append(
                {"title": title, "description": description, "price": price}
            )

        return menu_items


class TerraPizzaParser(BaseParser):
    """Парсер для сайта terrapizza.by на основе классов карточек"""

    def parse(self):
        soup = self.get_soup()
        if not soup:
            return []

        menu_items = []
        # Находим все контейнеры карточек блюд
        cards = soup.find_all("div", class_="menu-card")

        for card in cards:
            # Парсинг названия
            title_tag = card.find(class_="menu-card__title")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # Парсинг описания состава
            desc_tag = card.find(class_="menu-card__notice")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # Извлечение чистого числового значения цены и добавление валюты
            price_val_tag = card.find(class_="price-val")
            if price_val_tag:
                price_num = price_val_tag.get_text(strip=True)
                # Безопасно дописываем BYN на основе разметки
                price = f"{price_num} BYN"
            else:
                price = "Не указана"

            # Опционально: собираем вес блюда, если он необходим
            weight_tag = card.find(class_="product-weight")
            weight = weight_tag.get_text(strip=True) if weight_tag else ""

            # Формируем итоговый объект (можно добавить 'weight': weight при расширении)
            menu_items.append(
                {
                    "title": title,
                    "description": (
                        f"{description} ({weight})"
                        if description and weight
                        else (description or weight)
                    ),
                    "price": price,
                }
            )

        return menu_items


# =====================================================================
# КАРТА ПАРСЕРОВ (Для добавления нового сайта — просто внесите его сюда)
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

        # Сохраняем результат, используя URL как ключ
        all_menus[url] = menu
        print(f"-> Успешно собрано блюд: {len(menu)}")
        print("-" * 50)

    # Сохраняем все собранные данные в один файл конфигурации JSON
    output_filename = "all_lunch_menus.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_menus, f, ensure_ascii=False, indent=4)

    print(f"\n[ГОТОВО] Все меню успешно сохранены в файл: {output_filename}")


if __name__ == "__main__":
    main()
