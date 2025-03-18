from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class SubCategory(Base):

    __tablename__ = "sub_category" 
    sub_category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_product_id = Column(Integer, ForeignKey("category_product.category_product_id")) 
    sub_category_name =Column(String(255))
    sub_category_description=Column(Text(255))
    status = Column(TINYINT)
    created_at = Column(DateTime, default=func.current_timestamp())

    category_product = relationship("CategoryProduct", back_populates="sub_category")
    product = relationship("Product", back_populates="sub_category")



