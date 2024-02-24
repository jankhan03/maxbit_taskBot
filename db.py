from models import User, Task, Session
import bcrypt

def register_user(telegram_id, username, password, name):
    session = Session()
    try:
        # Хеширование пароля
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Создание нового пользователя
        new_user = User(telegram_id=telegram_id, username=username, password_hash=password_hash, name=name)
        session.add(new_user)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка при добавлении пользователя: {e}")
    finally:
        session.close()

def add_task(user_id, title, description, status):
    session = Session()
    try:
        # Добавление новой задачи
        new_task = Task(user_id=user_id, title=title, description=description, status=status)
        session.add(new_task)
        session.commit()
        print(f"Задача {title} успешно создана.")
    except Exception as e:
        session.rollback()
        print(f"Ошибка при добавлении задачи: {e}")
    finally:
        session.close()

def get_tasks(user_id):
    session = Session()
    try:
        tasks = session.query(Task).filter(Task.user_id == user_id).all()
        return [(task.id, task.title, task.description, task.status) for task in tasks]
    finally:
        session.close()

def complete_task(task_id):
    session = Session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = 'completed'
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка при обновлении задачи: {e}")
    finally:
        session.close()

#
# import bcrypt
# import psycopg2
# from settings import DATABASE_URL
#
#
# def register_user(telegram_id, username, password, name):
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#
#     # Хеширование пароля
#     password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#
#     try:
#         cursor.execute("INSERT INTO users (telegram_id, username, password_hash, name) VALUES (%s, %s, %s, %s)",
#                        (telegram_id, username, password_hash, name))
#         conn.commit()
#     except psycopg2.Error as e:
#         print(f"Ошибка при добавлении пользователя: {e}")
#     finally:
#         cursor.close()
#         conn.close()
#
#
# def add_task(telegram_id, title, description, status):
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("INSERT INTO tasks (user_id, title, description, status) VALUES (%s, %s, %s, %s)",
#                        (telegram_id, title, description, status))
#         conn.commit()
#     except psycopg2.Error as e:
#         print(f"Ошибка при добавлении задачи: {e}")
#         conn.rollback()
#     finally:
#         cursor.close()
#         conn.close()
#
#
# def get_tasks(user_id):
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("SELECT id, title, description, status FROM tasks WHERE user_id = %s", (user_id,))
#         tasks = cursor.fetchall()
#
#         return tasks
#     finally:
#         cursor.close()
#         conn.close()
#
# def complete_task(task_id):
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     try:
#         cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = %s", (task_id,))
#         conn.commit()
#     finally:
#         cursor.close()
#         conn.close()
