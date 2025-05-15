from sqlalchemy import Column, Integer, String
from .database import Base

class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    recovery = Column(String)
    secret = Column(String)