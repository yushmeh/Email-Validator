from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class ValidationConfig:
    """Конфигурация для процесса валидации email."""

    # Базовый регулярный вызов для проверки синтаксиса (RFC 5322 упрощенный)
    syntax_pattern: re.Pattern[str] = field(
        default=re.compile(
            r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        )
    )
    dns_timeout: float = 1.5
    check_mx: bool = True
    check_a: bool = True