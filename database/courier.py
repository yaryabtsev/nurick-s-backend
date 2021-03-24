from sqlalchemy import Column, Integer, VARCHAR, Float

from database.base import BaseModel


class Courier(BaseModel):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, unique=True, nullable=False)
    courier_type = Column(VARCHAR(255), nullable=False)
    regions = Column(VARCHAR(255), nullable=False)
    working_hours = Column(VARCHAR(255), nullable=False)
    earnings = Column(Integer, nullable=False, default=0)
    rating = Column(Float, nullable=False, default=0)

    sum_time = Column(VARCHAR(255), nullable=False)
    last_orders_id = Column(VARCHAR(255), nullable=False)
    count_orders = Column(VARCHAR(255), nullable=False)

    def __repr__(self):
        return f'{self.courier_type}_courier#{self.courier_id}'
