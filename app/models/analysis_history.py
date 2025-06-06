# app/models/analysis_history.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # JWT token'dan alınacak
    symbol = Column(String)
    indicators = Column(String)  # "sma,ema,rsi"
    result = Column(String)  # JSON formatta string olarak saklanacak
    created_at = Column(DateTime(timezone=True), server_default=func.now())
