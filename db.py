from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session as SessionClass
from sqlalchemy.util.compat import contextmanager

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

    @staticmethod
    def give_since_id():
        with session_scope() as session:  # type: SessionClass
            x = session.query(ProcessStat).filter_by(bot_name=ProcessStat.const_bot_name).first()
            if not x:
                ProcessStat.create_since_id(1)
                return 1
            return x.since_id


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
