from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL

'''В этом файле мы создадим модели наших таблиц'''

Base = declarative_base()

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BIGINT, unique=True)
    username = Column(String)
    password_hash = Column(String)
    name = Column(String)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String)
    user_id = Column(Integer)

Base.metadata.create_all(engine)
