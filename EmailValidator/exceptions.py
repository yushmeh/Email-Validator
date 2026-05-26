class EmailValidationError(Exception):
    """Базовое исключение для ошибок валидации email."""


class InvalidFormatException(EmailValidationError):
    """Вызывается, если синтаксис email-адреса неверен."""


class DNSValidationError(EmailValidationError):
    """Вызывается при проблемах с DNS-проверкой домена."""