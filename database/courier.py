from sqlalchemy import Column, Integer, VARCHAR

from database.base import BaseModel


class Courier(BaseModel):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, unique=True, nullable=False)
    courier_type = Column(VARCHAR(255), nullable=False)
    regions = Column(VARCHAR(255), nullable=False)
    working_hours = Column(VARCHAR(255), nullable=False)

    def __repr__(self):
        return f'{self.courier_type}_courier#{self.courier_id}'
