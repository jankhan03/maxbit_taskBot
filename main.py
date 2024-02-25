from typing import Any
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from logger import logger
import settings
from db import register_user, add_task, get_tasks, user_exists, delete_task, edit_task_status
from states import UserState
from inline_buttons import task_buttons, send_status_selection

user_state = UserState()

app = Client(
    "my_task_bot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN
)

@app.on_message(filters.command("register"))
def start_register(client: Client, message: Message) -> None:
    """
    Запускает процесс регистрации пользователя.

    Аргументы:
        client: Клиент бота.
        message: Сообщение от пользователя.

    Возвращает:
        None
    """
    user_id = message.from_user.id
    user_state.set_state(user_id, "STATE_USERNAME")
    user_state.set_data(user_id, "telegram_id", user_id)
    logger.info(f"User {user_id} started registration process.")
    message.reply_text("Пожалуйста, введите ваше имя пользователя:")

@app.on_message(filters.command("start"))
def start(client: Client, message: Message) -> None:
    """
    Обрабатывает команду /start, отправляя пользователю клавиатуру для регистрации или добавления задачи.

    Аргументы:
        client: Клиент бота.
        message: Сообщение от пользователя.

    Возвращает:
        None
    """
    user_id = message.from_user.id
    if user_exists(user_id):
        buttons = ReplyKeyboardMarkup(
            [
                [KeyboardButton("Добавление задачи"), KeyboardButton("Мои задачи")]
            ], resize_keyboard=True, one_time_keyboard=True
        )
        message.reply_text("Вы уже зарегестрированы в системе!\nВыберите действие:", reply_markup=buttons)
    else:
        buttons = ReplyKeyboardMarkup(
            [
                [KeyboardButton("Регистрация")]
            ], resize_keyboard=True, one_time_keyboard=True
        )
        message.reply_text("Для начала работы с ботом зарегистрируйтесь, пожалуйста.", reply_markup=buttons)

@app.on_message(filters.command("add_task"))
def add_task_start(client: Client, message: Message) -> None:
    """
    Начинает процесс добавления новой задачи, устанавливая состояние пользователя на добавление заголовка задачи.

    Аргументы:
        client: Клиент бота.
        message: Сообщение от пользователя.

    Возвращает:
        None
    """
    user_id = message.from_user.id
    user_state.set_state(user_id, "STATE_TITLE")
    logger.info(f"User {user_id} started adding a task.")
    message.reply_text("Введите название задачи:")

@app.on_message(filters.command("my_tasks"))
def show_tasks(client: Client, message: Message) -> None:
    """
    Отображает задачи пользователя, отправляя их списком в чат.

    Аргументы:
        client: Клиент бота.
        message: Сообщение от пользователя.

    Возвращает:
        None
    """
    user_id = message.from_user.id
    logger.info(f"User {user_id} requested to see their tasks.")
    try:
        tasks = get_tasks(user_id=user_id)
        if tasks:
            for task in tasks:
                task_id = task[0]
                task_message = f"Title: {task[1]}\nDescription: {task[2]}\nStatus: {task[3]}"
                message.reply_text(task_message, reply_markup=task_buttons(task_id))
        else:
            message.reply_text("У вас нет задач. Перейдите в главное меню командой /start и добавьте задачу.")
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {e}")
        message.reply_text("Произошла ошибка при получении списка ваших задач. Пожалуйста, попробуйте позже.")

@app.on_callback_query()
def callback_query_handler(client: Client, callback_query: Any) -> None:
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
        user_state.set_state(user_id, "STATE_EDIT_TASK")
        user_state.set_data(user_id, "task_id", task_id)  # Сохраняем ID задачи для дальнейшего использования
        delete_task(task_id)
        send_status_selection(client, callback_query.message.chat.id, user_id)  # Отправляем меню выбора статуса задачи


@app.on_message(filters.all)
def input_handler(client: Client, message: Message) -> None:
    """
    Обрабатывает все текстовые сообщения, не соответствующие другим фильтрам команд.

    Аргументы:
        client: Клиент бота.
        message: Сообщение от пользователя.

    Возвращает:
        None
    """
    user_id = message.from_user.id
    current_state = user_state.get_state(user_id)
    text = message.text

    if text == "Регистрация":
        start_register(client, message)
    elif text == "Добавление задачи":
        add_task_start(client, message)
    elif text == "Мои задачи":
        show_tasks(client, message)
    logger.info(f"User {user_id} is in state {current_state} and sent message: {text}")

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
        message.reply_text("Регистрация прошла успешно!\n Для создания задач перейдите в главное меню с помощью команды /start.")
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


    elif current_state == "STATE_EDIT_TASK":
        if text.startswith("status_"):
            new_status = text.split("_")[1]
            task_id = user_state.get_data(user_id, "task_id")
            if edit_task_status(task_id, new_status):
                message.reply_text(f"Статус задачи успешно изменен на {new_status}.")
            else:
                message.reply_text("Произошла ошибка при изменении статуса задачи.")
            user_state.delete_state(user_id)
            user_state.delete_data(user_id, "task_id")
        else:
            message.reply_text("Пожалуйста, выберите статус задачи из предложенного меню.")

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