import psycopg2
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import settings
from db import register_user, add_task, get_tasks, complete_task, get_user_id_by_telegram_id


app = Client(
    "my_task_bot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN
)
# обернуть в классы все стейты, добавить инлайн кнопки сделать класс состояний, добавить все переменные стейты
# добавить все модели с sql alchemy и добавить редактирование

USER_STATES_REG = {}
USER_DATA = {}
USER_STATES_ALL = {}
USER_STATES_ALL["STATE"] = 0

STATE_USERNAME = 1
STATE_NAME = 2
STATE_PASSWORD = 3
STATES_MACHINE_DICT = {}
STATES_MACHINE_DICT["STATE"] = ""

STATE_TITLE = "title"
STATE_DESCRIPTION = "description"
STATE_STATUS = "status"


@app.on_message(filters.command("register"))
def start_register(client, message):
    USER_STATES_ALL["STATE"] = 1
    user_id = message.from_user.id
    message.reply_text("Пожалуйста, введите ваше имя пользователя:")
    USER_STATES_REG[user_id] = STATE_USERNAME
    USER_DATA[user_id] = {"telegram_id": user_id}
    return

@app.on_callback_query()
def callback_query_handler(client, callback_query):
    if callback_query.data == "view_tasks":
        # Логика для отображения задач пользователя
        pass
    elif callback_query.data == "add_task":
        # Логика для добавления новой задачи
        pass

@app.on_message(filters.all)  #нужен допфильтр + понять как докеризировать
def input_handler(client, message):
    if USER_STATES_ALL["STATE"] == 1:
        user_id = message.from_user.id
        if user_id not in USER_STATES_REG:
            return

        state = USER_STATES_REG[user_id]

        if state == STATE_USERNAME:
            username = message.text
            USER_DATA[user_id]["username"] = username
            message.reply_text("Пожалуйста, введите ваше полное имя:")
            USER_STATES_REG[user_id] = STATE_NAME

        elif state == STATE_NAME:
            name = message.text
            USER_DATA[user_id]["name"] = name
            message.reply_text("Пожалуйста, введите ваш пароль (будет использован безопасный способ его сохранения):")
            USER_STATES_REG[user_id] = STATE_PASSWORD

        elif state == STATE_PASSWORD:
            password = message.text
            telegram_id = USER_DATA[user_id]["telegram_id"]
            username = USER_DATA[user_id]["username"]
            name = USER_DATA[user_id]["name"]

            try:
                register_user(telegram_id, username, password, name)
                message.reply_text("Регистрация прошла успешно!")
                USER_STATES_ALL["STATE"] = 0
            except Exception as e:
                message.reply_text(f"Ошибка при регистрации: {str(e)}")
            finally:
                del USER_STATES_REG[user_id]
                del USER_DATA[user_id]
    elif STATES_MACHINE_DICT["STATE"] == STATE_TITLE:
        telegram_id = message.from_user.id
        user_id = get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            message.reply_text("Пожалуйста, сначала зарегистрируйтесь с помощью команды /register.")
            return

        try:
            title = message.text
            USER_DATA["title"] = title
            message.reply_text("введите описание задачи:")
            STATES_MACHINE_DICT["STATE"] = STATE_DESCRIPTION

        except ValueError:
            message.reply_text("Неправильный формат. Используйте: /addtask Название Описание")

    elif STATES_MACHINE_DICT["STATE"] == STATE_DESCRIPTION:
        description = message.text
        USER_DATA["description"] = description
        message.reply_text("введите статус задачи:")
        STATES_MACHINE_DICT["STATE"] = STATE_STATUS

    elif STATES_MACHINE_DICT["STATE"] == STATE_STATUS:

        status = message.text
        USER_DATA["status"] = status

        STATES_MACHINE_DICT["STATE"] = ""

        add_task(message.from_user.id, USER_DATA["title"], USER_DATA["description"], USER_DATA["status"])
        message.reply_text("Задача успешно добавлена.")
    elif message.text == "/add_task":
        USER_STATES_ALL["STATE"] = 2
        STATES_MACHINE_DICT["STATE"] = STATE_TITLE
        message.reply_text("введите называние задачи:")
    elif message.text == "/start":
        message.reply_text(
            "Привет! Добро пожаловать в бота для управления задачами. Для регистрации введите /register.")
    elif message.text == "/my_tasks":
        telegram_id = message.from_user.id

        tasks = get_tasks(user_id=telegram_id)
        for task in tasks:
            message.reply_text(f"{task[1]} \n{task[2]} \n{task[3]}")

    return


if __name__ == "__main__":
    app.run()




