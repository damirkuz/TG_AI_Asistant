from flask import Flask, render_template

app = Flask(__name__)

# Функция проверки админа (в реальном приложении — аутентификация)
def is_admin():
    return False  # По умолчанию False (попробуйте поменять на True)

@app.route("/")
def home():
    chat_list = ['Общий чат', 'Техподдержка', 'Разработка', 'Маркетинг', 'Администрация']
    return render_template('index.html', chat_list=chat_list)

if __name__ == "__main__":
    app.run(debug=True)