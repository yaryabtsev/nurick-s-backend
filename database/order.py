from sqlalchemy import Column, Integer, Float, VARCHAR, TIMESTAMP, null

from database.base import BaseModel


class Order(BaseModel):
    __tablename__ = 'orders'

    order_id = Column(Integer, unique=True, nullable=False)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = Column(VARCHAR(255), nullable=False)
    assign_time = Column(TIMESTAMP, nullable=False)
    courier_id = Column(Integer, nullable=False)
    complete_time = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'order#{self.courier_id}: {self.weight}кг {self.delivery_hours} '
