from sqlalchemy import  Column,Float, ForeignKey, Integer, DateTime,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class OrderDetails(Base):
    __tablename__="order_details"
    order_detail_id=Column(Integer,primary_key=True,autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.order_id'))
    product_id = Column(Integer, ForeignKey("product.product_id"))
    quantity = Column(Integer)
    order_price = Column(Float)
    status = Column(TINYINT)
    created_at = Column(DateTime, default=func.current_timestamp())


    product = relationship("Product", back_populates="order_details")
    order= relationship("Order",back_populates="order_details")