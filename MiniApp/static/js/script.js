document.addEventListener('DOMContentLoaded', function() {
    let tg = window.Telegram.WebApp
    if (!window.Telegram?.WebApp) {
        showError("Это приложение работает только внутри Telegram");
        return;
    }
    if (!tg.initData) {
        showError("Запустите приложение через меню команд бота");
        return;
    }

    // Получаем элементы дат
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    // Добавляем валидацию дат
    function validateDates() {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (startDate && endDate && startDate > endDate) {
            endDateInput.setCustomValidity('Дата окончания не может быть раньше даты начала');
            endDateInput.reportValidity();
            return false;
        } else {
            endDateInput.setCustomValidity('');
            return true;
        }
    }
    
    // Слушатели событий для валидации
    startDateInput.addEventListener('change', validateDates);
    endDateInput.addEventListener('change', validateDates);

    const form = document.getElementById('mainForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateDates()) {
            return;
        }
        
        // Проверяем заполнено ли поле запроса
        const userQuery = document.getElementById('user_query').value.trim();
        if (!userQuery) {
            alert('Пожалуйста, введите ваш запрос');
            document.getElementById('user_query').focus();
            return;
        }
        
        // Остальной код отправки формы...
        const url = new URL(window.location.href);
        const telegramUserId = url.searchParams.get('telegram_user_id');
        
        const formData = new FormData(form);
        if (telegramUserId) {
            formData.append('telegram_user_id', telegramUserId);
        }
        
        fetch(url.pathname, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

function showError(message) {
    document.getElementById('mainBlock').style.display = 'none';
    document.getElementById('errorBlock').style.display = 'block';
    document.getElementById('errorMessage').textContent = `Ошибка: ${message}`;
}