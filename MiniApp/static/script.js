function showTab(tabId) {
    // Скрываем все вкладки
    document.querySelectorAll(".tab").forEach(tab => {
        tab.classList.remove("active");
    });

    // Убираем активность у всех кнопок
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    // Показываем нужную вкладку
    document.getElementById(tabId).classList.add("active");

    // Делаем кнопку активной
    event.currentTarget.classList.add("active");
}

function handleChatChange() {
    const selectElement = document.getElementById('fruits');
    const selectedFruit = selectElement.value;
    alert('Вы выбрали: ' + selectedFruit);
  }