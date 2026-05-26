from unittest.mock import MagicMock, patch

import dns.exception
import dns.resolver
import pytest

from exceptions import DNSValidationError
from validator import EmailValidator, validate_email


@pytest.fixture
def default_validator() -> EmailValidator:
    return EmailValidator()


class TestEmailSyntax:
    """Тестирование синтаксического парсинга email."""

    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "very.common@example.com",
            "disposable.style.email.with+symbol@example.com",
            "other.email-with-hyphen@example.com",
            "x@example.com",
            "user.name+tag+sorting@example.com",
        ],
    )
    def test_valid_syntax_formats(
        self, default_validator: EmailValidator, email: str
    ) -> None:
        local_part, domain = default_validator.verify_syntax(email)
        assert local_part is not None
        assert domain is not None

class TestDomainDNS:
    """Тестирование DNS проверок домена с использованием моков."""

    @patch("dns.resolver.Resolver.resolve")
    def test_dns_mx_record_success(
        self, mock_resolve: MagicMock, default_validator: EmailValidator
    ) -> None:
        # Симулируем успешный ответ для MX записи
        mock_resolve.return_value = ["mock_mx_record"]

        assert default_validator.verify_domain_dns("gmail.com") is True
        mock_resolve.assert_called_with("gmail.com", "MX")

    @patch("dns.resolver.Resolver.resolve")
    def test_dns_mx_fails_but_a_record_success(
        self, mock_resolve: MagicMock, default_validator: EmailValidator
    ) -> None:
        # Симулируем: MX бросает ошибку NoAnswer, но следующая проверка A-записи успешна
        mock_resolve.side_effect = [dns.resolver.NoAnswer(), ["mock_a_record"]]

        assert default_validator.verify_domain_dns("example.com") is True
        assert mock_resolve.call_count == 2

    @patch("dns.resolver.Resolver.resolve")
    def test_dns_domain_not_found(
        self, mock_resolve: MagicMock, default_validator: EmailValidator
    ) -> None:
        # Домен не существует
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()

        assert default_validator.verify_domain_dns("non-existent-domain.xyz") is False

    @patch("dns.resolver.Resolver.resolve")
    def test_dns_timeout_exception(
        self, mock_resolve: MagicMock, default_validator: EmailValidator
    ) -> None:
        # Эмуляция таймаута сети
        mock_resolve.side_effect = dns.exception.Timeout()

        with pytest.raises(DNSValidationError, match="Превышено время ожидания"):
            default_validator.verify_domain_dns("example.com")


class TestHighLevelAPI:
    """Интеграционные тесты для функции верхнего уровня validate_email."""

    @patch("dns.resolver.Resolver.resolve")
    def test_validate_email_end_to_end_success(self, mock_resolve: MagicMock) -> None:
        mock_resolve.return_value = ["valid"]
        result = validate_email("success@valid-domain.com")
        assert result is True

    @patch("dns.resolver.Resolver.resolve")
    def test_validate_email_end_to_end_fail(self, mock_resolve: MagicMock) -> None:
        # Комбинация: невалидный домен возвращает False вместо падения приложения
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()
        result = validate_email("user@bad-dns-domain.com")
        assert result is False

    def test_validate_email_invalid_syntax_returns_false(self) -> None:
        result = validate_email("plainaddress")
        assert result is False