from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.plot.plot_utils import plot_stock_chart
from app.services.data_service import get_stock_data_for_plot

router = APIRouter()

@router.get("/plot/{symbol}")
async def plot_symbol(symbol: str):
    data = get_stock_data_for_plot(symbol.upper())

    if data is None or data.empty:
        raise HTTPException(status_code=404, detail="No data available for this symbol.")

    buffer = plot_stock_chart(data, symbol.upper())
    return StreamingResponse(buffer, media_type="image/png")
