from pyrogram import Client, filters
from pyrogram.types import  Message
from logger import logger
from db import register_user, add_task, get_tasks, user_exists#, edit_task_status
from states import UserState
from inline_buttons import task_buttons, send_status_selection, registration, tasks, back_to_menu_keyboard

def register_handlers(client: Client, user_state: UserState) -> None:
    @client.on_message(filters.command("register"))
    def start_register(_, message: Message) -> None:
        """
        Запускает процесс регистрации пользователя.

        Аргументы:
            client: Клиент бота.
            message: Сообщение от пользователя.

        Возвращает:
            None
        """
        user_id = message.from_user.id
        if user_exists(user_id):
            message.reply_text("Вы уже зарегистрированы в системе.", reply_markup=back_to_menu_keyboard())
            logger.info(f"User {user_id} attempted to register again.")
        else:
            user_state.set_state(user_id, "STATE_USERNAME")
            user_state.set_data(user_id, "telegram_id", user_id)
            logger.info(f"User {user_id} started registration process.")
            message.reply_text("Пожалуйста, введите ваше имя пользователя:", reply_markup=back_to_menu_keyboard())

    @client.on_message(filters.command("start"))
    def start(_, message: Message) -> None:
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
            message.reply_text("Вы уже зарегестрированы в системе!\nВыберите действие:", reply_markup=tasks())
        else:
            message.reply_text("Для начала работы с ботом зарегистрируйтесь, пожалуйста.", reply_markup=registration())

    @client.on_message(filters.command("add_task"))
    def add_task_start(_, message: Message) -> None:
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
        message.reply_text("Введите название задачи:", reply_markup=back_to_menu_keyboard())

    @client.on_message(filters.text & filters.regex("^Вернуться в меню$"))
    def back_to_menu(_, message: Message) -> None:
        """
        Отвечает за возвращение в главное меню, обнуляя состояние пользоватлея.

        Аргументы:
            client: Клиент бота.
            message: Сообщение от пользователя.

        Возвращает:
            None
        """
        user_id = message.from_user.id
        user_state.delete_state(user_id)
        user_state.delete_data(user_id)
        start(client, message)

    @client.on_message(filters.command("my_tasks"))
    def show_tasks(_, message: Message) -> None:
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
                message.reply_text("У вас нет задач. Перейдите в главное меню и добавьте задачу.", reply_markup=back_to_menu_keyboard())
        except Exception as e:
            logger.error(f"Error retrieving tasks for user {user_id}: {e}")
            message.reply_text("Произошла ошибка при получении списка ваших задач. Пожалуйста, попробуйте позже.", reply_markup=back_to_menu_keyboard())


    @client.on_message(filters.all)
    def input_handler(_, message: Message) -> None:
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
            message.reply_text("Регистрация прошла успешно!\nДля создания задач перейдите в главное меню.")
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


        # elif current_state == "STATE_EDIT_TASK":
        #     if text.startswith("status_"):
        #         new_status = text.split("_")[1]
        #         task_id = user_state.get_data(user_id, "task_id")
        #         if edit_task_status(task_id, new_status):
        #             message.reply_text(f"Статус задачи успешно изменен на {new_status}.", reply_markup=back_to_menu_keyboard())
        #         else:
        #             message.reply_text("Произошла ошибка при изменении статуса задачи.", reply_markup=back_to_menu_keyboard())
        #         user_state.delete_state(user_id)
        #         user_state.delete_data(user_id, "task_id")
        #     else:
        #         message.reply_text("Пожалуйста, выберите статус задачи из предложенного меню.")

        elif current_state == "STATE_STATUS":
            status = message.text
            title = user_state.get_data(user_id, "title")
            description = user_state.get_data(user_id, "description")
            logger.info(f"User {user_id} entered status: {status}")
            add_task(user_id, title, description, status)
            logger.info(f"User {user_id} added task with title: {title}, description: {description}, status: {status}")
            message.reply_text("Задача успешно добавлена.", reply_markup=back_to_menu_keyboard())
            user_state.delete_state(user_id)
            user_state.delete_data(user_id)
