document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('messageForm');
    const messagesContainer = document.getElementById('messagesContainer');
    let replyTo = null;
    
    // Обработка отправки формы
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const user = document.getElementById('userInput').value;
        const text = document.getElementById('messageInput').value;
        const replyToInput = document.getElementById('replyToInput').value;
        
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'user': user,
                'text': text,
                'reply_to': replyToInput || ''
            })
        });
        
        if (response.ok) {
            // Обновляем страницу после отправки
            window.location.reload();
        }
    });
    
    // Прокрутка вниз при загрузке
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
});
