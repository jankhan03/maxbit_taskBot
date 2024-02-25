from logger import logger
from pyrogram import Client, filters
import settings
from db import register_user, add_task, get_tasks, complete_task, user_exists, delete_task

from states import UserState
from inline_buttons import task_buttons, send_status_selection
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


user_state = UserState()

app = Client(
    "my_task_bot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN
)


@app.on_message(filters.command("register"))
def start_register(client, message):
    user_id = message.from_user.id
    user_state.set_state(user_id, "STATE_USERNAME")
    user_state.set_data(user_id, "telegram_id", user_id)
    logger.info(f"User {user_id} started registration process.")
    message.reply_text("Пожалуйста, введите ваше имя пользователя:")

import text
@app.on_message(filters.command("start"))
def start(client, message):
    user_id = message.from_user.id
    if user_exists(user_id):
        # Пользователь существует, показываем кнопки для существующих пользователей
        buttons = ReplyKeyboardMarkup(
            [
                [KeyboardButton("/add_task"), KeyboardButton("/my_tasks")]
            ], resize_keyboard=True, one_time_keyboard=True
        )
        message.reply_text("Выберите действие:", reply_markup=buttons)
    else:
        # Пользователь не найден, показываем кнопку регистрации
        buttons = ReplyKeyboardMarkup(
            [
                [KeyboardButton("/register")]
            ], resize_keyboard=True, one_time_keyboard=True
        )
        message.reply_text("Добро пожаловать! Для начала работы с ботом, пожалуйста, зарегистрируйтесь.", reply_markup=buttons)

@app.on_message(filters.command("add_task"))
def add_task_start(client, message):
    user_id = message.from_user.id
    user_state.set_state(user_id, "STATE_TITLE")
    logger.info(f"User {user_id} started adding a task.")
    message.reply_text("Введите название задачи:")

@app.on_message(filters.command("my_tasks"))
def show_tasks(client, message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested to see their tasks.")
    try:
        tasks = get_tasks(user_id=user_id)
        if tasks:
            for task in tasks:
                task_id = task[0]  # Assuming the first element of the task is the task ID.
                task_message = f"Title: {task[1]}\nDescription: {task[2]}\nStatus: {task[3]}"
                message.reply_text(task_message, reply_markup=task_buttons(task_id))
        else:
            message.reply_text("You have no tasks.", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("➕ Add New Task", callback_data="/add_task")]] #не работает, перенести логику
            ))
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {e}")
        message.reply_text("There was an error retrieving your tasks. Please try again later.")


@app.on_callback_query()
def callback_query_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "/add_task": #не работает, перенести логику
        # add_task_start(client, message=())
        # Logic to start the process of adding a new task
        client.send_message(user_id, "Send me the title of the new task:")
    elif data.startswith("edit_"):
        task_id = data.split("_")[1]
        # Logic to start editing the specified task
        client.send_message(user_id, f"Send me the new details for task {task_id}:")


    elif data.startswith("delete_"):
        task_id = int(data.split("_")[1])  # Преобразуем ID задачи из строки в число
        delete_task(task_id)  # Вызываем функцию удаления задачи
        client.answer_callback_query(callback_query.id, "Задача успешно удалена.")
        client.delete_messages(chat_id=callback_query.message.chat.id,
                               message_ids=[
                                   callback_query.message.chat.id])  # Опционально: удаляем сообщение с задачей

    elif data.startswith("status_"):
        status = data.split("_")[1]
        title = user_state.get_data(user_id, "title")
        description = user_state.get_data(user_id, "description")
        add_task(user_id, title, description, status)
        logger.info(f"Task added with title: {title}, description: {description}, status: {status}")
        client.answer_callback_query(callback_query.id, "Задача успешно добавлена.")
        user_state.delete_state(user_id)
        user_state.delete_data(user_id)

@app.on_message(filters.all)
def input_handler(client, message):
    user_id = message.from_user.id
    current_state = user_state.get_state(user_id)

    logger.info(f"User {user_id} is in state {current_state} and sent message: {message.text}")

    if current_state == "STATE_USERNAME":
        username = message.text
        user_state.set_data(user_id, "username", username)
        logger.info(f"User {user_id} entered username: {username}")
        message.reply_text("Пожалуйста, введите ваше полное имя:")
        user_state.set_state(user_id, "STATE_NAME")

    elif current_state == "STATE_NAME":
        name = message.text
        user_state.set_data(user_id, "name", name)
        logger.info(f"User {user_id} entered name: {name}")
        message.reply_text("Пожалуйста, введите ваш пароль (будет использован безопасный способ его сохранения):")
        user_state.set_state(user_id, "STATE_PASSWORD")

    elif current_state == "STATE_PASSWORD":
        password = message.text
        telegram_id = user_state.get_data(user_id, "telegram_id")
        username = user_state.get_data(user_id, "username")
        name = user_state.get_data(user_id, "name")
        logger.info(f"User {user_id} entered password")
        register_user(telegram_id, username, password, name)
        logger.info(f"User {user_id} registered successfully")
        message.reply_text("Регистрация прошла успешно!")
        user_state.delete_state(user_id)
        user_state.delete_data(user_id)

    elif current_state == "STATE_TITLE":
        title = message.text
        user_state.set_data(user_id, "title", title)
        logger.info(f"User {user_id} entered title: {title}")
        message.reply_text("Введите описание задачи:")
        user_state.set_state(user_id, "STATE_DESCRIPTION")


    elif current_state == "STATE_DESCRIPTION":
        description = message.text
        user_state.set_data(user_id, "description", description)
        logger.info(f"User {user_id} entered description: {description}")
        send_status_selection(client, message.chat.id, user_id)  # Call to send status buttons

    elif current_state == "STATE_STATUS":
        status = message.text
        title = user_state.get_data(user_id, "title")
        description = user_state.get_data(user_id, "description")
        logger.info(f"User {user_id} entered status: {status}")
        add_task(user_id, title, description, status)
        logger.info(f"User {user_id} added task with title: {title}, description: {description}, status: {status}")
        message.reply_text("Задача успешно добавлена.")
        user_state.delete_state(user_id)
        user_state.delete_data(user_id)

if __name__ == "__main__":
    app.run()