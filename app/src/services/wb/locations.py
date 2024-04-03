from enum import Enum


class Location(str, Enum):
    MOSCOW = "Москва"
    ST_PETERBURG = "Санкт-Петербург"
    NOVOSIBIRSK = "Новосибирск"
    YEKATERENBURG = "Екатеринбург"
    KAZAN = "Казань"
    KRASNODAR = "Краснодар"
    KHABAROVSK = "Хабаровск"


LOCATIONS = {
    Location.MOSCOW: "-1257786",
    Location.ST_PETERBURG: "-1198055",
    Location.NOVOSIBIRSK: "-364763",
    Location.YEKATERENBURG: "-5803327",
    Location.KAZAN: "-2133462",
    Location.KRASNODAR: "12358062",
    Location.KHABAROVSK: "-1785058",
}
