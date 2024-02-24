from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_buttons(task_id):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{task_id}"),
             InlineKeyboardButton("❌ Delete", callback_data=f"delete_{task_id}")],
            [InlineKeyboardButton("➕ Add New Task", callback_data="add_new_task")]
        ]
    )

def send_status_selection(client, chat_id, user_id):
    status_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("задача создана", callback_data="status_задача создана")],
        [InlineKeyboardButton("в процессе", callback_data="status_в процессе")],
        [InlineKeyboardButton("завершена", callback_data="status_завершена")]
    ])
    client.send_message(chat_id, "Выберите статус задачи:", reply_markup=status_buttons)

