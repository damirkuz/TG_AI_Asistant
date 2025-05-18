// Функция для обработки инициализации WebApp
function initTelegramWebApp() {
    // Проверяем, что Telegram WebApp инициализирован
    let tg = window.Telegram.WebApp
    if (!window.Telegram?.WebApp) {
      showError("Это приложение работает только внутри Telegram");
      return;
    }
    if (!tg.initData) {
      showError("Запустите приложение через меню команд бота");
      return;
    }
    if (window.Telegram && Telegram.WebApp) {
      // Инициализируем WebApp
      tg.ready();
      tg.expand();
      // Получаем initData
      const initData = tg.initData;
    //   Telegram.WebApp.showAlert("InitData: " + Telegram.WebApp.initData);
      // Показываем блок загрузки
      document.getElementById('loadingBlock').style.display = 'block';
      document.getElementById('mainBlock').style.display = 'none';
      
      // Отправляем данные на сервер для проверки
      fetch('/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          initData: initData,
          initDataUnsafe: tg.initDataUnsafe
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Ошибка проверки');
        }
        return response.json();
      })
      .then(data => {
        if (data.status === 'ok') {
          // Успешная проверка
          Telegram.WebApp.expand(); // Расширяем WebApp
          
          // Скрываем загрузку и показываем основной контент
          document.getElementById('loadingBlock').style.display = 'none';
          document.getElementById('mainBlock').style.display = 'block';
        } else {
          throw new Error(data.message || 'Проверка не пройдена');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showError(error.message);
      });
    } else {
      showError("Telegram WebApp environment not detected!");
    }
  }
  
  // Функция для отображения ошибки
  function showError(message) {
    document.getElementById('loadingBlock').innerHTML = `
      <div class="error-container">
        <div class="alert alert-danger" role="alert">
          Ошибка: ${message}
        </div>
        <button onclick="location.reload()" class="btn btn-primary">Попробовать снова</button>
      </div>
    `;
  }
  
  // Запускаем инициализацию при загрузке страницы
  document.addEventListener('DOMContentLoaded', initTelegramWebApp);