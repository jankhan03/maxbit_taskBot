import psycopg2
from pyrogram import Client, filters
import settings
from settings import DATABASE_URL
from db import register_user, add_task, get_tasks, complete_task

app = Client(
    "my_task_bot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN
)
# обернуть в классы все стейты, добавить инлайн кнопки сделать класс состояний, добавить все переменные стейты
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


def get_user_id_by_telegram_id(telegram_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user_id = cursor.fetchone()[0]
        return user_id
    except TypeError:
        return None
    finally:
        cursor.close()
        conn.close()

# @app.on_message(filters.command("addtask"))
# def handle_add_task(client, message):
#     telegram_id = message.from_user.id
#     user_id = get_user_id_by_telegram_id(telegram_id)
#     if not user_id:
#         message.reply_text("Пожалуйста, сначала зарегистрируйтесь с помощью команды /register.")
#         return
#
#     try:
#         title, description = message.text.split(maxsplit=2)[1:]
#         add_task(user_id, title, description)
#         message.reply_text("Задача успешно добавлена.")
#     except ValueError:
#         message.reply_text("Неправильный формат. Используйте: /addtask Название Описание")

# @app.on_message(filters.command("tasks"))
# def handle_list_tasks(client, message):
#     user_id = message.from_user.id
#     tasks = get_tasks(user_id)
#     if tasks:
#         reply_message = "\n".join([f"{task[0]}: {task[1]} - {task[2]} (Статус: {task[3]})" for task in tasks])
#         message.reply_text(reply_message)
#     else:
#         message.reply_text("У вас нет задач.")
#
# @app.on_message(filters.command("complete"))
# def handle_complete_task(client, message):
#     try:
#         task_id = int(message.text.split()[1])
#         complete_task(task_id)
#         message.reply_text(f"Задача {task_id} отмечена как выполненная.")
#     except ValueError:
#         message.reply_text("Неправильный формат. Используйте: /complete ID_задачи")



if __name__ == "__main__":
    app.run()






# import psycopg2
# from pyrogram import Client, filters
# import settings
# from settings import DATABASE_URL
# from db import register_user, add_task, get_tasks, complete_task
# import transitions
# from transitions import State, Machine
#
#
# app = Client(
#     "my_task_bot",
#     api_id=settings.API_ID,
#     api_hash=settings.API_HASH,
#     bot_token=settings.BOT_TOKEN
# )
#
#
# @app.on_message(filters.command("start"))
# async def start(client, message):
#     if fsm.state == 'start':
#         fsm.register()
#         await message.reply_text("Добро пожаловать! Давайте зарегистрируем вас.")
#         # Переход в состояние awaiting_registration
#
# @app.on_message(filters.command("register"))
#
# # @app.on_message(filters.command("start"))
# # def start(сlient, message):
# #     message.reply_text("Привет! Добро пожаловать в бота для управления задачами. Для регистрации введите /register.")
#
# USER_STATES_REG = {}
# USER_DATA = {}
#
# STATE_USERNAME = 1
# STATE_NAME = 2
# STATE_PASSWORD = 3
#
#     @app.on_message(filters.command("register"))
#     def start_register(client, message):
#         user_id = message.from_user.id
#         message.reply_text("Пожалуйста, введите ваше имя пользователя:")
#         USER_STATES_REG[user_id] = STATE_USERNAME
#         USER_DATA[user_id] = {"telegram_id": user_id}
#
#     @app.on_message(filters.text | filters.command("register"))  #нужен допфильтр + понять как докеризировать
#     def input_handler(client, message):
#         user_id = message.from_user.id
#         if user_id not in USER_STATES_REG:
#             return
#
#         state = USER_STATES_REG[user_id]
#
#         if state == STATE_USERNAME:
#             username = message.text
#             USER_DATA[user_id]["username"] = username
#             message.reply_text("Пожалуйста, введите ваше полное имя:")
#             USER_STATES_REG[user_id] = STATE_NAME
#
#         elif state == STATE_NAME:
#             name = message.text
#             USER_DATA[user_id]["name"] = name
#             message.reply_text("Пожалуйста, введите ваш пароль (будет использован безопасный способ его сохранения):")
#             USER_STATES_REG[user_id] = STATE_PASSWORD
#
#         elif state == STATE_PASSWORD:
#             password = message.text
#             telegram_id = USER_DATA[user_id]["telegram_id"]
#             username = USER_DATA[user_id]["username"]
#             name = USER_DATA[user_id]["name"]
#
#             try:
#                 register_user(telegram_id, username, password, name)
#                 message.reply_text("Регистрация прошла успешно!")
#             except Exception as e:
#                 message.reply_text(f"Ошибка при регистрации: {str(e)}")
#             finally:
#                 del USER_STATES_REG[user_id]
#                 del USER_DATA[user_id]
#
# lump = Registration()
# machine = Machine(lump, states=['STATE_USERNAME', 'STATE_NAME', 'STATE_PASSWORD'])
# def get_user_id_by_telegram_id(telegram_id):
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
#         user_id = cursor.fetchone()[0]
#         return user_id
#     except TypeError:
#         return None
#     finally:
#         cursor.close()
#         conn.close()
#
# @app.on_message(filters.command("addtask"))
# def handle_add_task(client, message):
#     telegram_id = message.from_user.id
#     user_id = get_user_id_by_telegram_id(telegram_id)
#     if not user_id:
#         message.reply_text("Пожалуйста, сначала зарегистрируйтесь с помощью команды /register.")
#         return
#
#     try:
#         title, description = message.text.split(maxsplit=2)[1:]
#         add_task(user_id, title, description)
#         message.reply_text("Задача успешно добавлена.")
#     except ValueError:
#         message.reply_text("Неправильный формат. Используйте: /addtask Название Описание")
#
# @app.on_message(filters.command("tasks"))
# def handle_list_tasks(client, message):
#     user_id = message.from_user.id
#     tasks = get_tasks(user_id)
#     if tasks:
#         reply_message = "\n".join([f"{task[0]}: {task[1]} - {task[2]} (Статус: {task[3]})" for task in tasks])
#         message.reply_text(reply_message)
#     else:
#         message.reply_text("У вас нет задач.")
#
# @app.on_message(filters.command("complete"))
# def handle_complete_task(client, message):
#     try:
#         task_id = int(message.text.split()[1])
#         complete_task(task_id)
#         message.reply_text(f"Задача {task_id} отмечена как выполненная.")
#     except ValueError:
#         message.reply_text("Неправильный формат. Используйте: /complete ID_задачи")
# if __name__ == "__main__":
#     app.run()
#
#
#
#
