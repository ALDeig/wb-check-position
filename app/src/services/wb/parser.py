import asyncio
import logging
import re
from asyncio.exceptions import TimeoutError
from collections import defaultdict
from json.decoder import JSONDecodeError

from httpx import AsyncClient
from pydantic import BaseModel

from app.src.services.exceptions import BadWbResponse, EmptyPageError, NotValideteUrl
from app.src.services.wb.headers import get_headers, get_params
from app.src.services.wb.locations import LOCATIONS, Location

logger = logging.getLogger(__name__)

SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v5/search"
TIMEOUT = 20
PAGE_COUNT = 60


class Position(BaseModel):
    """Локация артикула и его позиция в данной локации."""

    location: str
    page: int
    position: int
    promo_page: int | None = None
    promo_position: int | None = None


class Positions(BaseModel):
    """Список позиций артикула по всем локациям."""

    positions: list[Position] = []


class Parser:
    """Парсер WB."""

    def __init__(self, articules: list[int] | int, query: str) -> None:
        """Принимает список артикулов или один артикул и поисковый запрос."""
        self._articules = articules if isinstance(articules, list) else [articules]
        self._query = query

    async def get_positions(self) -> dict[int, Positions]:
        """Возвращает словарь с артикулами и позициями."""
        articules_positions = defaultdict(Positions)

        # каждая локация собирается конкурентно
        tasks = [
            asyncio.create_task(self._find_position_by_location(location))
            for location in Location
        ]
        for task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=60)
            except TimeoutError:
                logger.exception("TimeoutError")
                continue
            # result = await task
            for articule, position in result.items():
                articules_positions[articule].positions.append(position)

        # каждая локация собирается последовательно
        # for location in Location:
        #     print(location)
        #     result = await self._find_position_by_location(location)
        #     for articule, position in result.items():
        #         articules_positions[articule].positions.append(position)
        return articules_positions

    async def is_exists(self) -> bool:
        """Проверяет существует ли такой артикул на WB."""
        async with AsyncClient() as client:
            params = {
                "appType": 1,
                "dest": -1257786,
                "spp": 30,
                "nm": self._articules[0],
            }
            response = await client.get(
                "https://card.wb.ru/cards/v2/detail", params=params
            )
        try:
            return bool(response.json()["data"]["products"])
        except JSONDecodeError:
            return False

    async def _find_position_by_location(
        self, location: Location
    ) -> dict[int, Position]:
        """Находит позции артикулов в одном регионе."""
        positions = {}
        not_found_articules = set(self._articules)
        last_page = PAGE_COUNT
        page = 1
        while page != last_page + 1:
            # получаем товары на странице
            try:
                page_articules = await self._get_products_on_page(
                    LOCATIONS[location], page
                )
            except EmptyPageError:
                # если приходит пустой ответ, то сразу останавливаем цикл
                last_page = page
                break
            except BadWbResponse:
                continue
            # проходим по артикулам, которые нужно найти
            for articule in self._articules:
                position = self._check_articule_on_page(
                    articule, page_articules, location, page
                )
                if position is not None:
                    # если позиция найдена, то добавляет ее в результат
                    # и удалаяет артикул из списка артикулов, которые нужно найти
                    positions[articule] = position
                    try:
                        not_found_articules.remove(articule)
                    except KeyError:
                        logger.exception(
                            "KeyError: not_found_articules=%s. "
                            "Remove - articule=%s. self._articules=%s",
                            not_found_articules,
                            articule,
                            self._articules,
                        )
            if not not_found_articules:
                return positions
            page += 1
        for articule in not_found_articules:
            # проходит по артикулам, которые не удалось найти и заполняет данные по ним
            positions[articule] = Position(
                location=location.value, page=last_page, position=0
            )
        return positions

    def _check_articule_on_page(
        self,
        articule: int,
        page_articules: dict[int, dict],
        location: Location,
        page: int,
    ) -> Position | None:
        """Вызывает функцию проверки артикула на странице, и если артикул найден,
        то формирует данные по позиции.
        """
        # вызываем функцию, которая находит позицию, если не находит, то 0
        position = self._fing_position_in_page_articules(articule, page_articules)
        if not position:
            return
        if promo := page_articules[articule].get("log"):
            page, position = self._calculate_page_and_position(promo["position"])
            promo_page, promo_position = self._calculate_page_and_position(
                promo["promoPosition"]
            )
        else:
            promo_page, promo_position = None, None
        return Position(
            location=location.value,
            page=page,
            position=position,
            promo_page=promo_page,
            promo_position=promo_position,
        )

    async def _get_products_on_page(self, dest: str, page: int) -> dict[int, dict]:
        """Собирает артикулы на странице."""
        headers = get_headers(page, self._query)
        params = get_params(self._query, dest, page)
        async with AsyncClient(timeout=TIMEOUT, headers=headers) as client:
            await client.options(SEARCH_URL, params=params)
            response = await client.get(SEARCH_URL, params=params)
        try:
            result = {item["id"]: item for item in response.json()["data"]["products"]}
            # if len(result) == 1:
            #     raise BadWbResponse
            # return result
        except KeyError:
            raise EmptyPageError from None
        except JSONDecodeError:
            raise BadWbResponse from None
        else:
            if len(result) == 1:
                raise BadWbResponse
            return result

    @staticmethod
    def _fing_position_in_page_articules(
        articule: int, page_articules: dict[int, dict]
    ) -> int:
        """Находит позицию артикула из списка артикулов на странице. Если артикула нет
        то возвращает 0.
        """
        try:
            return tuple(page_articules.keys()).index(articule) + 1
        except ValueError:
            return 0

    @staticmethod
    def _calculate_page_and_position(absolute_position: int) -> tuple[int, int]:
        page = absolute_position // 100
        position = absolute_position % 100
        return page if page else 1, position


def get_article(article_or_url: str) -> int:
    """Если передается артикул, то он и возвращается типом int, если url, то
    достается артикул и приводится к int.
    """
    if article_or_url.isdigit():
        return int(article_or_url)
    url_without_params = article_or_url.split("?")[0]
    digits = re.search(r"\d+", url_without_params)
    if digits is None:
        raise NotValideteUrl
    return int(digits.group())
