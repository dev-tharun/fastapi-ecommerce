from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base


class ProductImage(Base):
    __tablename__ = "productimage"
    productimage_id=Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.product_id"),)
    productimage_url=Column(String(255))
    status = Column(TINYINT)
    created_at = Column(DateTime, default=func.current_timestamp())

    product=relationship("Product",back_populates="productimage")
