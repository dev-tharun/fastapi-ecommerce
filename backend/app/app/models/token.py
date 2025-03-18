from sqlalchemy import  Column, Integer, String, DateTime, ForeignKey,func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Apitoken(Base):
    __tablename__ = 'api_token'
    id= Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey('user.user_id'))
    token = Column(String(255))
    status = Column(TINYINT)
    created_at = Column(DateTime,default=func.current_timestamp())

    user=relationship("User",back_populates="api_token")