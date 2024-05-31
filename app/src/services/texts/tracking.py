from app.src.services.wb.parser import Position, Positions

SUBSCRIBE_CHANNEL = "Вы не подписаны на канал"
_EMOJI = {True: "✅", False: "❌"}
_DIFF_EMOJI = {True: "⤴️", False: "⤵️"}
_HEADER_TEXT = (
    'Артикул {} по запросу <strong>"{}"</strong>\n\n'
    "Бот присылает информацию в формате\n"
    "✅ - есть, ❌ - нет;\n"
    "📊 32/2 — органическая позиция/страница;\n"
    "📢 23/1 — рекламная позиция/страница\n\n"
)
_FOOTER_TEXT = "Вы можете включить регулярное отслеживание позиций для этого товара"


def query_text(
    query: str,
    articule: str | int,
    tracking: Positions,
    old_positions: Positions | None = None,
) -> str:
    text = get_tracking_text(query, articule, tracking, old_positions)
    text += f"\n\n{_FOOTER_TEXT}"
    return text


def get_tracking_text(
    query: str,
    articule: str | int,
    tracking: Positions,
    old_positions: Positions | None = None,
) -> str:
    text = _HEADER_TEXT.format(articule, query)
    for location in tracking.positions:
        promo_position_text = _get_promo_text(
            location.promo_position, location.promo_page
        )
        diff_text = _diff_position_text(location, old_positions)
        text += (
            f"\n{_EMOJI[bool(location.position)]} {location.location} - "
            f"{promo_position_text}"
            f"📊 {location.position}/{location.page} {diff_text}"
        )

    return text


def _diff_position_text(position: Position, old_positins: Positions | None) -> str:
    if old_positins is None:
        return ""
    for old_position in old_positins.positions:
        if old_position.location == position.location:
            diff = (
                old_position.page * old_position.position
                - position.page * position.position
            )
            # если diff отрицательный - позиция опустилась, если положительный поднялась
            if not diff:
                return ""
            diff_str = str(diff) if diff < 0 else f"+{diff}"
            return f"{_DIFF_EMOJI[diff > 0]} ({diff_str})"
    return ""


def get_text_track(query: str, articule: int) -> str:
    return f"Артикул: {articule}\nЗапрос: {query}"


def _get_promo_text(promo_position: int | None, promo_page: int | None) -> str:
    if not promo_position:
        return ""
    return f"📢 {promo_position}/{promo_page}; "
