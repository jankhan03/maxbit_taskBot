from models import User, Task, Session
import bcrypt
from sqlalchemy import cast, Integer
from logger import logger

'''В этом файле мы работаем с базами данных и sql запросами, обернутыми в алхимию для удобства и безопасности'''

def register_user(telegram_id, username, password, name):
    session = Session()
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(telegram_id=int(telegram_id), username=username, password_hash=password_hash, name=name)
        session.add(new_user)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.info(f"Ошибка при добавлении пользователя: {e}")
    finally:
        session.close()

def delete_task(task_id):
    session = Session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            session.delete(task)
            session.commit()
            logger.info(f"Задача {task.title} успешно удалена.")
    except Exception as e:
        session.rollback()
        logger.info(f"Ошибка при удалении задачи: {e}")
    finally:
        session.close()

def user_exists(telegram_id):
    session = Session()
    try:
        user = session.query(User).filter(cast(User.telegram_id, Integer) == telegram_id).first()
        return user is not None
    finally:
        session.close()

def add_task(user_id, title, description, status):
    session = Session()
    try:
        # Добавление новой задачи
        new_task = Task(user_id=user_id, title=title, description=description, status=status)
        session.add(new_task)
        session.commit()
        logger.info(f"Задача {title} успешно создана.")
    except Exception as e:
        session.rollback()
        logger.info(f"Ошибка при добавлении задачи: {e}")
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
        logger.info(f"Ошибка при обновлении задачи: {e}")
    finally:
        session.close()

# def get_user_id_by_telegram_id(telegram_id):
#     session = Session()
#     try:
#         user = session.query(User).filter(cast(User.telegram_id, Integer) == telegram_id).first()
#         return user.id if user else None
#     finally:
#         session.close()