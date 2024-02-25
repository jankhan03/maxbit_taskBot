from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

'''В этом файле мы создадим inline кнопки, для использования в остальном проекте'''

def task_buttons(task_id):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_{task_id}"),
             InlineKeyboardButton("❌ Удалить", callback_data=f"delete_{task_id}")]
        ]
    )

def send_status_selection(client, chat_id, user_id):
    status_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Задача создана", callback_data="status_задача создана")],
        [InlineKeyboardButton("Задача в процессе", callback_data="status_в процессе")],
        [InlineKeyboardButton("Задача завершена", callback_data="status_завершена")]
    ])
    client.send_message(chat_id, "После выбора статуса задачи перейдите в главное меню /start и продолжите работу.\nВыберите статус задачи:", reply_markup=status_buttons)

