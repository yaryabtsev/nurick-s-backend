import datetime
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, TIMESTAMP, VARCHAR, create_engine, Float
from sqlalchemy.orm import scoped_session, sessionmaker

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'data.db'), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Courier(BaseModel):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, unique=True, nullable=False)
    courier_type = Column(VARCHAR(255), nullable=False)
    regions = Column(VARCHAR(255), nullable=False)
    working_hours = Column(VARCHAR(255), nullable=False)

    def __repr__(self):
        return f'{self.courier_type}_courier#{self.courier_id}'


class Order(BaseModel):
    __tablename__ = 'orders'

    order_id = Column(Integer, unique=True, nullable=False)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = Column(VARCHAR(255), nullable=False)
    assign_time = Column(TIMESTAMP)
    courier_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f'{self.courier_type}_courier#{self.courier_id}'


def init_db():
    Base.metadata.create_all(bind=engine)
