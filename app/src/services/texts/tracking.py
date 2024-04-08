from app.src.services.wb.parser import Positions


SUBSCRIBE_CHANNEL = "Вы не подписаны на канал"
_EMOJI = {True: "✅", False: "❌"}
_HEADER_TEXT = (
    'Артикул {} по запросу <strong>"{}"</strong>\n\n'
    "Бот присылает информацию в формате\n"
    "✅ - есть, ❌ - нет;\n"
    "📊 32/2 — органическая позиция/страница;\n"
    "📢 23/1 — рекламная позиция/страница\n\n"
)
_FOOTER_TEXT = "Вы можете включить регулярное отслеживание позиций для этого товара"


def query_text(query: str, articule: str | int, tracking: Positions) -> str:
    text = get_tracking_text(query, articule, tracking)
    text += f"\n\n{_FOOTER_TEXT}"
    return text


def get_tracking_text(query: str, articule: str | int, tracking: Positions) -> str:
    text = _HEADER_TEXT.format(articule, query)
    for location in tracking.positions:
        promo_position_text = _get_promo_text(
            location.promo_position, location.promo_page
        )
        text += (
            f"\n{_EMOJI[bool(location.position)]} {location.location} - "
            f"{promo_position_text}"
            f"📊 {location.position}/{location.page}"
        )

    return text


def get_text_track(query: str, articule: int) -> str:
    return f"Артикул: {articule}\nЗапрос: {query}"


def _get_promo_text(promo_position: int | None, promo_page: int | None) -> str:
    if not promo_position:
        return ""
    promo_position_text = f"📢 {promo_position}/{promo_page}; "
    return promo_position_text
