// Показываем блок загрузки
// document.getElementById('loadingBlock').style.display = 'block';
// document.getElementById('mainBlock').style.display = 'none';
// Проверяем, что Telegram WebApp инициализирован
if (window.Telegram && Telegram.WebApp) {
    // Показываем alert с initData
    Telegram.WebApp.showAlert(
        "Полученные данные:\n" + 
        JSON.stringify(Telegram.WebApp.initData, null, 2),
        (result) => {
            // Коллбек после закрытия alert
            console.log("Alert closed", result);
        }
    );
} else {
    console.error("Telegram WebApp environment not detected!");
}
initData = Telegram.WebApp.initData
// Отправляем на сервер для проверки
fetch('/verify', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
        'initData': initData
    })
})
.then(response => {
    if (!response.ok) {
        throw new Error('Ошибка проверки');
    }
    return response.json();
})
.then(data => {
    console.log("Server response:", data);  // Будет видно в консоли браузера
    Telegram.WebApp.showAlert(JSON.stringify(data));  // Покажет alert в Telegram
    if (data.status === 'ok') {
        // Успешная проверка - скрываем загрузку и показываем основной контент
        document.getElementById('loadingBlock').style.display = 'none';
        document.getElementById('mainBlock').style.display = 'block';
        
        // Дополнительно: расширяем WebApp на весь экран
        Telegram.WebApp.expand();
    } else {
        throw new Error('Проверка не пройдена');
    }
})
.catch(error => {
    console.error('Error:', error);
    // Показываем сообщение об ошибке
    document.getElementById('loadingBlock').innerHTML = `
        <div class="d-flex justify-content-center align-items-center" style="height: 100vh;">
            <div class="alert alert-danger" role="alert">
                Ошибка аутентификации: ${error.message}
            </div>
        </div>
    `;
});
