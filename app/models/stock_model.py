from pydantic import BaseModel
from typing import Optional

class StockResponse(BaseModel):
    symbol: str
    shortName: Optional[str]
    currentPrice: Optional[float]
    currency: Optional[str]
    peRatio: Optional[float]          # Price to Earnings
    pbRatio: Optional[float]          # Price to Book
    returnOnEquity: Optional[float]   # ROE
from pydantic import BaseModel
from typing import List, Optional

class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    rsi: float
    moving_average_7: float
    moving_average_14: float
    close_prices: List[float]
