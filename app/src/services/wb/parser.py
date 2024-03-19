import re


def get_article(article_or_url: str) -> int:
    """Если передается артикул, то он и возвращается типом int, если url, то
    достается артикул и приводится к int"""
    if article_or_url.isdigit():
        return int(article_or_url)
    url_without_params = article_or_url.split("?")[0]
    digits = re.search(r"\d+", url_without_params)
    if digits is None:
        raise NotValideteUrl
    return int(digits.group())

