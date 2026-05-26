document.addEventListener('DOMContentLoaded', () => {
    // Инициализация иконок Lucide
    lucide.createIcons();

    const form = document.getElementById('validatorForm');
    const emailInput = document.getElementById('emailInput');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');
    const liveStatus = document.getElementById('liveStatus');

    const resultContainer = document.getElementById('resultContainer');
    const resultTitle = document.getElementById('resultTitle');
    const resultDesc = document.getElementById('resultDesc');
    const successIcon = document.getElementById('errorIcon');
    const errorIcon = document.getElementById('successIcon');
    const resultIconWrapper = document.getElementById('resultIconWrapper');

    // Базовый RegExp для фронтенд-подсветки
    const basicRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // 1. Валидация "на лету" (Live Feedback)
    emailInput.addEventListener('input', () => {
        const value = emailInput.value.trim();

        if (value === '') {
            liveStatus.innerHTML = '';
            return;
        }

        if (basicRegex.test(value)) {
            liveStatus.innerHTML = '<i data-lucide="circle-check" style="color: #10b981; width: 18px; height: 18px;"></i>';
        } else {
            liveStatus.innerHTML = '<i data-lucide="circle-alert" style="color: #ef4444; width: 18px; height: 18px;"></i>';
        }
        lucide.createIcons();
    });

    // 2. Основной запрос к бэкенду
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = emailInput.value.trim();

        if (!email) return;

        // Эффект загрузки (Loading State)
        submitBtn.disabled = true;
        btnText.style.opacity = '0.5';
        spinner.classList.remove('hidden');
        resultContainer.classList.add('hidden');

        try {
            // Вызов нашего FastAPI эндпоинта
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });

            const data = await response.json();

            // Рендеринг результата
            resultContainer.classList.remove('hidden', 'result-success', 'result-error');

            if (data.valid) {
                resultContainer.classList.add('result-success');
                resultTitle.textContent = "Валидный email";
                resultDesc.textContent = `Адрес успешно прошел проверку формата и DNS домена.`;

                document.getElementById('successIcon').classList.remove('hidden');
                document.getElementById('errorIcon').classList.add('hidden');
            } else {
                resultContainer.classList.add('result-error');
                resultTitle.textContent = "Невалидный email";
                resultDesc.textContent = data.reason || "Неверный синтаксис или домен не существует.";

                document.getElementById('errorIcon').classList.remove('hidden');
                document.getElementById('successIcon').classList.add('hidden');
            }

        } catch (error) {
            // Обработка непредвиденных сетевых ошибок фронтенда
            resultContainer.classList.remove('hidden', 'result-success');
            resultContainer.classList.add('result-error');
            resultTitle.textContent = "Ошибка сети";
            resultDesc.textContent = "Не удалось связаться с сервером валидации.";
        } finally {
            // Возвращаем кнопку в исходное состояние
            submitBtn.disabled = false;
            btnText.style.opacity = '1';
            spinner.classList.add('hidden');
            lucide.createIcons();
        }
    });
});