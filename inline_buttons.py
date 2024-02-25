from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

'''В этом файле мы создадим inline кнопки, для использования в остальном проекте'''

def task_buttons(task_id):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❌ Удалить", callback_data=f"delete_{task_id}")]
            # [InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_{task_id}"),
            #  InlineKeyboardButton("❌ Удалить", callback_data=f"delete_{task_id}")]
        ]
    )

def send_status_selection(client, chat_id, user_id):
    status_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Задача создана", callback_data="status_задача создана")],
        [InlineKeyboardButton("Задача в процессе", callback_data="status_в процессе")],
        [InlineKeyboardButton("Задача завершена", callback_data="status_завершена")]
    ])
    client.send_message(chat_id, "После выбора статуса задачи перейдите в главное меню с помощью команды /start и продолжите работу.\nВыберите статус задачи:", reply_markup=status_buttons)

def back_to_menu_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Вернуться в меню")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def registration():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Регистрация")]
        ], resize_keyboard=True,
        one_time_keyboard=True
    )

def tasks():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Добавление задачи"), KeyboardButton("Мои задачи")]
        ], resize_keyboard=True,
        one_time_keyboard=True
    )