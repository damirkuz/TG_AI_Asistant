function initTelegramWebApp() {
    let tg = window.Telegram.WebApp
    if (!window.Telegram?.WebApp) {
      showError("Это приложение работает только внутри Telegram");
      return;
    }
    if (!tg.initData) {
      showError("Запустите приложение через меню команд бота");
      return;
    }
    
    tg.ready();
    tg.expand();
    
    document.getElementById('loadingBlock').style.display = 'flex';
    
    fetch('/verify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            initData: tg.initData,
            initDataUnsafe: tg.initDataUnsafe
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка проверки');
        return response.json();
    })
    .then(data => {
        if (data.status === 'ok') {
            // Перенаправляем на главную страницу с параметром user_id
            window.location.href = `/?telegram_user_id=${tg.initDataUnsafe.user.id}`;
        } else {
            throw new Error(data.message || 'Проверка не пройдена');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError(error.message);
    });
}

function showError(message) {
    document.getElementById('loadingBlock').style.display = 'none';
    document.getElementById('errorBlock').style.display = 'block';
    document.getElementById('errorMessage').textContent = `Ошибка: ${message}`;
}

document.addEventListener('DOMContentLoaded', initTelegramWebApp);