LEXICON_COMMANDS_RU = {
    '/start': 'Запустить бота',
    '/help': 'Справка по работе бота'
}

LEXICON_ANSWERS_RU = {
    '/start': "👋 Привет! "
              "Я — Telegram AI Assistant. Помогу найти и проанализировать информацию в твоих чатах.",
    '/help': "🤖 Этот бот умеет:\n"
             "— Искать нужную информацию в твоих чатах\n"
             "— Анализировать переписки и создавать досье\n"
             "— Экспортировать результаты в удобный формат\n\n"
             "Напиши /start, чтобы начать.",
    'agree_rules': "📜 Прежде чем продолжить, пожалуйста, ознакомься с правилами использования бота:\n"
                   "🔗 [Открыть правила](https://teletype.in/@be_2nd/TG\\_AI\\_Assistant\\_Rules)\n\n"
                   "Продолжая использовать бота, ты подтверждаешь согласие с этими условиями",
    'back_to_main_menu': "Меню:",
    'accept_retry': "Чтобы использовать бота, вы должны согласиться с правилами",
    'accept_success': "Отлично, теперь ты можешь авторизоваться",
    'other_messages': "Извини, но я не понимаю тебя :(",
    'auth_request_phone': "Введи свой телефон или поделись номером",
    'auth_incorrect_phone': "Неправильный номер телефона, пришли его в формате 79998887766",
    'auth_banned_phone': "Данный номер забанен в Telegram",
    'auth_request_code': "Отлично, теперь пришли код, что тебе пришёл от Telegram, добавив к нему 1\n"
                         "К примеру тебе пришло 34502, тогда тебе надо прислать 34503",
    'auth_message_incorrect_code': "Отправь корректный код в формате 12345",
    'auth_invalid_code': "Отправьте именно тот код, что вам пришёл от Telegram, добавив к нему 1\n"
                         "К примеру тебе пришло 34502, тогда тебе надо прислать 34503",
    'auth_expired_code': "Данный код уже истёк, отправил вам новый",
    'auth_need_password': "На аккаунте включена двухфакторная аутентификация, пришлите пароль от неё",
    'auth_invalid_password': "Неправильный пароль, попробуйте ещё раз",
    'auth_successful': "Успешная авторизация",
    'not_done': "Ещё не реализовано",
    'settings_menu': "Здесь ты можешь настроить бота",
    'settings_add_telegram_menu': "Добавить аккаунт можно двумя способами",
    'settings_add_telegram_session': "Отправь в чат session файл",
    'settings_add_telegram_session_bad': "Извини, но я не понимаю тебя.\nОтправь корректный session файл",
    'settings_add_telegram_session_good': "Отлично, теперь ты можешь пользоваться ботом",
    'admin_menu_start': "😎 Меню администратора:",
    'admin_statistics': (
        "📊 <b>Статистика</b>\n"
        "• 👤 <b>Пользователи:</b> {users_count}\n"
        "• 🔗 <b>Аккаунтов:</b> {accounts_count}\n"
        "• ⚡ <b>Действий сегодня:</b> {daily_actions}\n"
        "• 🗓 <b>Всего действий:</b> {total_actions}"
    ),
    'admin_find_user': "Отправь телеграм id/username пользователя или перешли его сообщение",
    'admin_users_panel': "Меню взаимодействия с пользователями",
    'admin_not_find_user': "Данный пользователь не найден, отправь телеграм id/username пользователя или перешли его сообщение",
    'admin_detailed_user_me': (
        "📊 <b>О пользователе</b> @{username}\n"
        "<b>Telegram id:</b> {telegram_id}\n"
        "<b>Полное имя:</b> {full_name}\n"
        "<b>Администратор:</b> {is_admin}\n"
        "<b>Активен:</b> {is_active}\n"
        "<b>Заблокирован:</b> {is_banned}\n"
        "<b>Зарегистрировался:</b> {register_date}"
    ),
    'admin_detailed_user_account': (
        "Аккаунт привязанный пользователем\n"
        "<b>Telegram id:</b> {telegram_id}\n"
        "<b>Полное имя:</b> {full_name}\n"
        "<b>Телефон:</b> {phone_number}\n"
    ),
    'admin_user_was_banned': "Пользователь заблокирован",
    'admin_user_was_unbanned': "Пользователь разблокирован",
    'you_banned': "😔 Вы заблокированы",
    'admin_user_maked_admin': "Пользователь назначен администратором",
    'admin_user_unmaked_admin': "Пользователь разжалован",
    'settings_delete_my_data': ("Данные о вас удалены\n"
                                "Чтобы начать заново нажмите /start")
}

LEXICON_BUTTONS_RU = {
    'register': 'Авторизоваться',
    'share_phone': 'Поделиться номером',
    'person_analyze': 'Анализ человека',
    'assistant_start': 'Личный ассистент',
    'accept_rules': 'Согласен',
    'back_to_main_menu': '🏠 В главное меню',
    'menu_settings': '⚙️ Настройки',
    'menu_find': '🔍 Найти информацию в чатах',
    'menu_dossier': '📝 Составить досье',
    'menu_admin': '🛠 Админ-панель',
    'settings_add_telegram': '🔐 Подключить Telegram',
    'settings_AI_API_key': '🔑 Мой OpenAI API-ключ',
    'settings_LLM_model': '🧠 Модель LLM',
    'settings_history_actions': '📌 История действий',
    'settings_my_statistics': '📊 Моя статистика',
    'settings_delete_my_data': '🗑️ Удалить данные о себе',
    'settings_add_telegram_session': '📤 Загрузить session-файл',
    'settings_add_telegram_phone': '🔢 Войти по номеру и коду',
    'admin_statistics': "📊 Статистика",
    'admin_users': "👥 Пользователи",
    'admin_users_panel_detailed': "🔍 Подробнее",
    'admin_users_panel_ban': "🚫 Заблокировать",
    'admin_users_panel_unban': "✅ Разблокировать",
    'admin_users_panel_make_admin': "🛠 Назначить администратором",
    'admin_users_panel_unmake_admin': "🛠 Разжаловать администратора"
}
