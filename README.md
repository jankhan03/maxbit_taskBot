Пояснительная Записка для Telegram-бота "Task Manager Bot"

Целью проекта является разработка Telegram-бота для управления задачами пользователей. Бот позволяет пользователям регистрироваться, добавлять, редактировать, просматривать и удалять свои задачи. Он предоставляет удобный интерфейс для управления ежедневными делами и проектами и может стать незаменимым помощником.

/// к сожалению в последнем из коммитов при некоторых изменениях была утрачена работоспособность функции изменения статуса задачи, в следующей версии этот момент я добавлю. В коде оставлены функции с комментариями

///upd 13.20 26.02 - добавлен хотфикс редактирования задачи

Инструкции по Развертыванию и Запуску  
Для запуска контейнера с приложением необходимо:  
Клонировать репозиторий с кодом бота.  
Добавить в файл settings.py переменные окружения API_ID, API_HASH, и BOT_TOKEN, а так же DATABASE_URL. 
Переменные API_ID, API_HASH можно получить на странице https://my.telegram.org/apps, а BOT_TOKEN в BotFather.
Добавить в файл docker-compose.yml переменные окружения API_ID, API_HASH, и BOT_TOKEN, а так же POSTGRES_DB, POSTGRES_USER и POSTGRES_PASSWORD.  
Запустить скрипт бота с помощью команды python bot.py.  
Ввести в терминал команду docker-compose up -d.  
Ввести в терминал команду docker-compose up.  
Дополнительные Пояснения  
Для обеспечения безопасности пароли пользователей хешируются перед сохранением в базе данных. Бот использует механизмы состояний для отслеживания текущего действия пользователя, что позволяет создавать многоступенчатые диалоги (например, регистрация или добавление задачи).  
Для улучшения взаимодействия пользователя с ботом, бот использует inline-кнопки для простоты выполнения действий с задачами, таких как редактирование и удаление. Состояния и данные пользователей сохраняются в памяти бота, что позволяет обеспечивать персонализированный диалог и помнить контекст диалога в процессе взаимодействия.  

Использованные Технологии и Инструменты
Python: Выбран для основы бота.  
Pyrogram: Фреймворк для создания Telegram-ботов в Python.  
SQLAlchemy: ORM для работы с базами данных, обеспечивает безопасность и удобство работы с SQL-запросами.  
Postgres: База данных, используемая для хранения данных пользователя и задач.  
bcrypt: Библиотека для безопасного хеширования паролей.  
Архитектурное Описание  
Бот строится на основе клиент-серверной архитектуры, где серверная часть обрабатывает команды пользователя, отправленные через клиент Telegram. Взаимодействие с базой данных происходит через абстракцию ORM для обеспечения безопасности и гибкости.  

Описание Классов и Функций  
Client: Класс из Pyrogram, представляет сессию бота в Telegram.  
UserState: Класс для управления состоянием пользователя во время сессии.  
Session: Класс из SQLAlchemy, управляет соединениями с базой данных и транзакциями.  
User, Task: Классы-модели SQLAlchemy для представления таблиц в базе данных.  
Функции обработчики команд (register, start, add_task_start, и т.д.) вызываются в ответ на конкретные команды пользователя и управляют логикой бота.  

Реализованная Функциональность  
Регистрация: Пользователи могут зарегистрироваться с помощью команды /register.  
Управление задачами: Пользователи могут добавлять (/add_task), просматривать (/my_tasks), редактировать и удалять задачи.  
Изменение статуса: Пользователи могут изменять статус задачи с помощью интерактивных кнопок.  
SQL-Запросы и Структура БД  
SQL-запросы выполняются через ORM SQLAlchemy. База данных состоит из двух таблиц: User (хранит информацию о пользователях) и Task (хранит информацию о задачах пользователя).  

Примеры использования бота:  
Пользователь отправляет команду /register и вводит необходимые данные для регистрации.  
После регистрации с помощью кнопки пользователь возвращается в главное меню.  
Пользователю предлагается добавить задачу или посмотреть список своих задач.  
Пользователь может добавить задачу с помощью соответсвующей кнопки и ввести название и описание.  
С помощью кнопки "Мои задачи" пользователь получает список своих задач с кнопками для редактирования и удаления.  
SQL-запросы и структура базы данных:  
База данных состоит из двух основных таблиц:  
users: Хранит информацию о пользователях, включая их telegram_id, username, зашифрованный password_hash и name.  
tasks: Содержит задачи пользователей, включая title, description и status.  

Примеры SQL-запросов через ORM:  
Добавление новой задачи: session.add(new_task)  
Изменение статуса задачи: session.query(Task).filter(Task.id == task_id).update({"status": new_status})  
Удаление задачи: session.delete(task)  

Для дальнейшего расширения функционала бота можно добавить систему напоминаний о задачах, интеграцию с календарями и возможность групповой работы над задачами.  
В последующих версиях так же необходимо будет добавить проверку корректности пароля, логина и полного имени.
