from app.src.services.wb.parser import Positions


EMOJI = {True: "✅", False: "❌"}
HEADER_TEXT = (
    'Артикул {} по запросу <strong>"{}"</strong>\n\n'
    "Бот присылает информацию в формате\n"
    "✅ - есть, ❌ - нет;\n"
    "📊 органическая позиция 32, страница 2;\n"
    "📢 рекламная позиция 23, страница 1\n\n"
)
FOOTER_TEXT = "Вы можете включить регулярное отслеживание позиций для этого товара"


def get_tracking_text(query: str, articule: str | int, tracking: Positions) -> str:
    text = HEADER_TEXT.format(articule, query)
    for location in tracking.positions:
        if location.promo_position:
            promo_position_text = (
                f"📢 позиция {location.promo_position}, "
                f"страница {location.promo_page}; "
            )
        else:
            promo_position_text = ""
        text += (
            f"\n{EMOJI[bool(location.position)]} {location.location} - "
            f"{promo_position_text}"
            f"📊 позиция {location.position}, страница {location.page}"
        )
    text += f"\n\n{FOOTER_TEXT}"
    
    return text


def get_text_track(query: str, articule: int) -> str:
    return f"Артикул: {articule}\nЗапрос: {query}"
