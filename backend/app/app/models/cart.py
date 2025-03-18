from sqlalchemy import Column,Float, ForeignKey, Integer,DateTime,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base


class Cart(Base):
    __tablename__ = "cart"
    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.product_id"),)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    quantity = Column(Integer)
    price=Column(Float)
    status = Column(TINYINT)
    created_at = Column(DateTime, default=func.current_timestamp())

 
    product= relationship("Product", back_populates="cart")
    user = relationship("User", back_populates="cart")