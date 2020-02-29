from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session as SessionClass
from sqlalchemy.util.compat import contextmanager

from utils import get_time_in_iran_timezone

engine = create_engine('sqlite:///abrekalamt.db')
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base(bind=engine)


class ProcessStat(Base):
    __tablename__ = 'process_state'
    since_id = Column(Integer)
    bot_name = Column(String, primary_key=True)

    const_bot_name = 'abrekalamt'

    def __init__(self, since_id: int, bot_name: str):
        self.since_id = since_id
        self.bot_name = bot_name

    @staticmethod
    def create_since_id(since_id: int):
        with session_scope() as session:  # type: SessionClass
            x = session.query(ProcessStat).filter_by(bot_name=ProcessStat.const_bot_name).first()
            if not x:
                session.add(ProcessStat(since_id, ProcessStat.const_bot_name))
                return
            x.since_id = since_id

    @staticmethod
    def give_since_id():
        with session_scope() as session:  # type: SessionClass
            x = session.query(ProcessStat).filter_by(bot_name=ProcessStat.const_bot_name).first()
            if not x:
                ProcessStat.create_since_id(1)
                return 1
            return x.since_id


class ProcessedUserNames(Base):
    __tablename__ = 'processed_user_names'
    user_name = Column(String, primary_key=True)
    last_time = Column(DateTime)

    def __init__(self, user_name: str):
        self.user_name = user_name
        self.last_time = get_time_in_iran_timezone()

    @staticmethod
    def create_last_time(user_name: str):
        with session_scope() as session:  # type: SessionClass
            x = session.query(ProcessedUserNames).filter_by(user_name=user_name).first()
            if not x:
                session.add(ProcessedUserNames(user_name))
                return
            x.last_time = get_time_in_iran_timezone()

    @staticmethod
    def give_last_time(user_name):
        with session_scope() as session:  # type: SessionClass
            x = session.query(ProcessedUserNames).filter_by(user_name=user_name).first()
            if not x:
                ProcessedUserNames.create_last_time(user_name)
                return -1
            return x.last_time


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()  # type: SessionClass
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise


@contextmanager
def read_session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()  # type: SessionClass
    try:
        yield session
    except:
        raise


Base.metadata.create_all(bind=engine)
