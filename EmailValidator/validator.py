import logging
from typing import Final
import dns.exception
import dns.resolver

from config import ValidationConfig
from exceptions import DNSValidationError, InvalidFormatException

# Настройка логгера для модуля
logger: Final[logging.Logger] = logging.getLogger(__name__)


class EmailValidator:
    """Класс для валидации email-адресов, объединяющий синтаксические и DNS проверки."""

    def __init__(self, config: ValidationConfig | None = None) -> None:
        """Инициализирует валидатор с переданной или дефолтной конфигурацией.

        Args:
            config: Объект конфигурации ValidationConfig.
        """
        self.config: ValidationConfig = config or ValidationConfig()

    def verify_syntax(self, email: str) -> tuple[str, str]:
        """Проверяет синтаксическую корректность email структуры.

        Args:
            email: Строка email-адреса для проверки.

        Returns:
            Tuple[str, str]: Кортеж из (local_part, domain).

        Raises:
            InvalidFormatException: Если email не соответствует паттерну или пуст.
        """
        if not email or not isinstance(email, str):
            raise InvalidFormatException("Email должен быть непустой строкой.")

        email = email.strip()
        if not self.config.syntax_pattern.match(email):
            logger.warning(f"Синтаксическая проверка провалена для: {email}")
            raise InvalidFormatException(
                f"Неверный формат email-адреса: {email}"
            )

        local_part, domain = email.rsplit("@", 1)
        return local_part, domain

    def verify_domain_dns(self, domain: str) -> bool:
        """Выполняет проверку существования домена через DNS (MX и/или A записи).

        Args:
            domain: Доменное имя для проверки.

        Returns:
            bool: True, если домен имеет валидные записи.

        Raises:
            DNSValidationError: Если домен не найден или сеть недоступна.
        """
        resolver = dns.resolver.Resolver()
        resolver.timeout = self.config.dns_timeout
        resolver.lifetime = self.config.dns_timeout

        records_to_check: list[str] = []
        if self.config.check_mx:
            records_to_check.append("MX")
        if self.config.check_a:
            records_to_check.append("A")

        for record_type in records_to_check:
            try:
                logger.debug(
                    f"Запрос {record_type}-записи для домена {domain}..."
                )
                resolver.resolve(domain, record_type)
                logger.info(
                    f"Успешно найдена {record_type}-запись для домена {domain}."
                )
                return True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                logger.debug(
                    f"Запись {record_type} не найдена для домена {domain}."
                )
                continue
            except dns.exception.Timeout:
                logger.error(
                    f"Таймаут DNS-запроса при проверке {domain} ({record_type})."
                )
                raise DNSValidationError(
                    f"Превышено время ожидания DNS для домена: {domain}"
                )
            except dns.exception.DNSException as e:
                logger.error(
                    f"Ошибка DNS при проверке {domain} ({record_type}): {e}"
                )
                raise DNSValidationError(
                    f"Ошибка DNS-сервера при валидации домена: {domain}"
                )

        logger.warning(f"Домен {domain} не имеет ни MX, ни A записей.")
        return False


def validate_email(
    email: str, config: ValidationConfig | None = None
) -> bool:
    """Удобный процедурный интерфейс (high-level API) для валидации email.

    Args:
        email: Строка email-адреса.
        config: Опциональная конфигурация для переопределения логики.

    Returns:
        bool: True, если email полностью валиден. False, если возникли ошибки.
    """
    validator = EmailValidator(config=config)
    try:
        _, domain = validator.verify_syntax(email)
        return validator.verify_domain_dns(domain)
    except (InvalidFormatException, DNSValidationError) as err:
        logger.info(f"Валидация email '{email}' не пройдена. Причина: {err}")
        return False

if __name__ == "__main__":
    emails = [
        "test@example.com",
        "invalid-email",
        "user@gmail.com",
        "bad@domain",
    ]

    for email in emails:
        result = validate_email(email)
        print(f"{email}: {result}")