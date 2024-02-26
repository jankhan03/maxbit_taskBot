from typing import Any
from pyrogram import Client
from logger import logger
from db import add_task, delete_task
from states import UserState


def register_callbacks(client: Client, user_state: UserState) -> None:
    @client.on_callback_query()
    def callback_query_handler(_, callback_query: Any) -> None:
        """
        Обрабатывает нажатия на inline-кнопки, выполняя соответствующие действия в зависимости от данных кнопки.

        Аргументы:
            client: Клиент бота.
            callback_query: CallbackQuery от нажатия на кнопку.

        Возвращает:
            None
        """
        data = callback_query.data
        user_id = callback_query.from_user.id

        if data == "add_task":
            client.send_message(user_id, "Введите название новой задачи:")

        elif data.startswith("delete_"):
            task_id = int(data.split("_")[1])
            delete_task(task_id)
            client.answer_callback_query(callback_query.id, "Задача успешно удалена.")
            client.delete_messages(chat_id=callback_query.message.chat.id, message_ids=[callback_query.message.chat.id])

        elif data.startswith("status_"):
            status = data.split("_")[1]
            title = user_state.get_data(user_id, "title")
            description = user_state.get_data(user_id, "description")
            add_task(user_id, title, description, status)
            logger.info(f"Task added with title: {title}, description: {description}, status: {status}")
            client.answer_callback_query(callback_query.id, "Задача успешно добавлена.")
            user_state.delete_state(user_id)
            user_state.delete_data(user_id)

        elif data.startswith("edit_"):
            task_id = data.split("_")[1]
            logger.info(f"task_id {task_id}")
            delete_task(task_id)
            user_state.set_state(user_id, "STATE_EDIT_TASK")