from sqlalchemy import Column, String
from app.database.database import Base

class Company(Base):
    __tablename__ = "companies"

    symbol = Column(String, primary_key=True)
    name = Column(String, nullable=False)
