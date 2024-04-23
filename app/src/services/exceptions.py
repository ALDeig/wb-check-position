class NotValideteUrl(Exception):
    pass


class SendError(Exception):
    pass


class EmptyPageError(Exception):
    pass


class BadWbResponse(Exception):
    pass


class BadUserRequest(Exception):
    """
    Пользователь отправил неверный запрос.
    Не удалось распаристь артикул и поисковый запрос
    """
