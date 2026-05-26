from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
import uvicorn

# Импортируем архитектурные элементы твоего созданного модуля
from validator import EmailValidator
from exceptions import EmailValidationError

app = FastAPI(title="Enterprise Email Validator API")

# Подключаем статические файлы (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Схема входящих данных
class EmailRequest(BaseModel):
    email: str


# Схема ответа сервера
class EmailResponse(BaseModel):
    email: str
    valid: bool
    reason: str | None = None


@app.get("/")
async def read_index():
    """Отдает главную страницу интерфейса."""
    return FileResponse("static/index.html")


@app.post("/api/validate", response_model=EmailResponse)
def api_validate_email(payload: EmailRequest):
    validator = EmailValidator()

    try:
        # 1. Проверяем синтаксис
        _, domain = validator.verify_syntax(payload.email)

        # 2. Проверяем DNS
        is_valid_domain = validator.verify_domain_dns(domain)

        if is_valid_domain:
            return EmailResponse(email=payload.email, valid=True)
        else:
            return EmailResponse(
                email=payload.email,
                valid=False,
                reason="Домен не существует или не принимает почту (отсутствуют MX/A записи)."
            )

    except EmailValidationError as err:
        # Отлавливаем твои кастомные исключения (InvalidFormatException, DNSValidationError)
        return EmailResponse(email=payload.email, valid=False, reason=str(err))
    except Exception as e:
        # Глобальный перехватчик непредвиденных ситуаций
        return EmailResponse(email=payload.email, valid=False, reason="Внутренняя ошибка сервера при валидации.")


if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run("main.py:app", host="127.0.0.1", port=8000, reload=True)