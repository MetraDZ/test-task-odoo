from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///example.db' # TODO Insert url here <username>:<password>@<host>:<port>/<db_name>

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class BaseWithJson(Base):
    __abstract__ = True

    def to_dict(self):
        return {field.name:getattr(self, field.name) for field in self.__table__.c if field.name != 'hashed_password'}
    
    @classmethod
    def fields(cls, ignored: List[str]):
        fields = [field.name for field in cls.__table__.c]
        if ignored:
            fields = [field for field in fields if field not in ignored]
        return fields
    

class User(BaseWithJson):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(60), nullable=False)
    hashed_password = Column(String(60), nullable=False)


class Contact(BaseWithJson):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    oodo_id = Column(Integer, nullable=False)
    name = Column(String(60), server_default='NoNameUser')
    email = Column(String(60))

Base.metadata.create_all(engine)