import json
import os

# 1. Читаем JSON из файла
json_filename = 'all_lunch_menus.json'

if not os.path.exists(json_filename):
    demo_data = {
        "url1 (Terra Pizza)": [
            {
                "title": "Салат с ветчиной, свежими овощами и копченым сыром",
                "description": "Ветчина, сыр моцарелла, капуста пекинская, томат и огурец свежие, майонез, сыр копченый",
                "weight": "150 г",
                "price_delivery": "7.50 BYN",
                "image": "https://terrapizza.by"
            }
        ],
        "url2 (Pizza Tempo)": [
            {
                "title": "Пицца \\Гавайская\\ 26 см на тонком тесте",
                "description": "соус из томатов, Моцарелла, ветчина, ананасы, масло чесночное.",
                "weight": "330 г",
                "price_delivery": "9.99 BYN",
                "image": "https://pizzatempo.by"
            }
        ]
    }
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=4)

with open(json_filename, "r", encoding="utf-8") as f:
    menu_data = json.load(f)


# 2. Генерируем HTML с исправленным синтаксисом шаблона
html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Обеденное меню</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html {{ scroll-behavior: smooth; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f9fafb; color: #1f2937; padding: 24px; }}
        
        .container {{ max-width: 1200px; margin: 0 auto; display: flex; gap: 32px; align-items: flex-start; }}
        .main-content {{ flex-grow: 1; min-width: 0; }}
        
        header {{ border-bottom: 1px solid #e5e7eb; padding-bottom: 16px; margin-bottom: 32px; }}
        h1 {{ font-size: 28px; font-weight: 800; color: #111827; }}
        
        nav.nav-sidebar {{ 
            position: sticky; 
            top: 24px; 
            width: 260px; 
            background: #ffffff; 
            border: 1px solid #e5e7eb; 
            border-radius: 12px; 
            padding: 16px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            flex-shrink: 0;
        }}
        .nav-title {{ font-size: 12px; font-weight: 700; color: #9ca3af; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.05em; }}
        .nav-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
        .nav-item a {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 8px 12px; 
            color: #4b5563; 
            text-decoration: none; 
            font-size: 14px; 
            font-weight: 500; 
            border-radius: 8px; 
            transition: background 0.15s, color 0.15s; 
        }}
        .nav-item a:hover {{ background: #f3f4f6; color: #4f46e5; }}
        .nav-count {{ font-size: 11px; background: #e5e7eb; color: #4b5563; padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
        
        .menu-section {{ background: #ffffff; border-radius: 16px; padding: 24px; margin-bottom: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f3f4f6; scroll-margin-top: 24px; }}
        .section-title {{ font-size: 20px; font-weight: 700; color: #4f46e5; margin-bottom: 24px; display: flex; align-items: center; gap: 8px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }}
        .card {{ display: flex; flex-direction: column; background: #f9fafb; border-radius: 12px; overflow: hidden; border: 1px solid #f3f4f6; transition: transform 0.2s, box-shadow 0.2s; }}
        .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        
        .image-container {{ height: 192px; overflow: hidden; background: #e5e7eb; position: relative; }}
        .image-container img {{ width: 100%; height: 100%; object-fit: cover; }}
        .weight-tag {{ position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.6); color: #ffffff; font-size: 12px; padding: 2px 8px; border-radius: 6px; backdrop-filter: blur(4px); }}
        
        .card-content {{ padding: 16px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
        .card-title {{ font-size: 16px; font-weight: 700; color: #111827; margin-bottom: 8px; line-height: 1.4; }}
        .card-desc {{ font-size: 14px; color: #4b5563; margin-bottom: 16px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
        
        .card-footer {{ padding-top: 12px; border-top: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
        .price-label {{ font-size: 11px; color: #9ca3af; text-transform: uppercase; display: block; }}
        .price-value {{ font-size: 20px; font-weight: 900; color: #10b981; }}

        @media (max-width: 768px) {{
            .container {{ flex-direction: column; }}
            nav.nav-sidebar {{ position: relative; width: 100%; top: 0; margin-bottom: 24px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav-sidebar">
            <div class="nav-title">Быстрый переход</div>
            <ul class="nav-list" id="nav-list"></ul>
        </nav>

        <div class="main-content">
            <header>
                <h1>🍔 Меню на сегодня</h1>
            </header>
            <div id="menu-container"></div>
        </div>
    </div>

    <script>
        const menuData = {json.dumps(menu_data, ensure_ascii=False)};
        const container = document.getElementById('menu-container');
        const navList = document.getElementById('nav-list');

        Object.entries(menuData).forEach(([sourceKey, items]) => {{
            if (!items || items.length === 0) return;

            const sectionId = 'sec-' + sourceKey.replace(/[^a-zA-Z0-9]/g, '-');
            
            const navItem = document.createElement('li');
            navItem.className = 'nav-item';
            navItem.innerHTML = `
                <a href="#${{sectionId}}">
                    <span>📂 ${{sourceKey}}</span>
                    <span class="nav-count">${{items.length}}</span>
                </a>
            `;
            navList.appendChild(navItem);

            const section = document.createElement('section');
            section.className = 'menu-section';
            section.id = sectionId;
            
            section.innerHTML = `
                <div class="section-title">
                    📂 ${{sourceKey}}
                </div>
                <div class="grid" id="grid-${{sectionId}}"></div>
            `;
            container.appendChild(section);

            const grid = document.getElementById(`grid-${{sectionId}}`);
            
            items.forEach(item => {{
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div class="image-container">
                        <img src="${{item.image || ''}}" alt="${{item.title || ''}}" onerror="this.src='https://placehold.co'">
                        <span class="weight-tag">${{item.weight || '📈'}}</span>
                    </div>
                    <div class="card-content">
                        <div>
                            <div class="card-title">${{item.title || 'Без названия'}}</div>
                            <div class="card-desc">${{item.description || 'Описание отсутствует.'}}</div>
                        </div>
                        <div class="card-footer">
                            <div>
                                <span class="price-label">Цена</span>
                                <span class="price-value">${{item.price_delivery || item.price_takeaway || '—'}}</span>
                            </div>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }});
    </script>
</body>
</html>
"""

output_html = "view_menu.html"
with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Готово! Ошибка исправлена. Обновленный файл сохранен как '{output_html}'.")
