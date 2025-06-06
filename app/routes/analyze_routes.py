# routes/analyze_routes.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import io
import csv
from reportlab.pdfgen import canvas

router = APIRouter()

# Örnek analiz verisi (test amaçlı)
mock_result = {
    "symbol": "AAPL",
    "latest": {
        "close": 203.89,
        "sma": 204.2,
        "rsi": 35.53,
        "bollinger_upper": 210.0,
        "bollinger_lower": 190.0
    }
}


def get_analysis_result(symbol: str):
    if symbol.upper() == "AAPL":
        return mock_result
    return None


@router.get("/download/csv/{symbol}")
def download_csv(symbol: str):
    result = get_analysis_result(symbol)
    if not result:
        raise HTTPException(status_code=404, detail="No analysis result found.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    for key, value in result["latest"].items():
        writer.writerow([key, value])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={symbol}_analysis.csv"}
    )


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
from app.plot.plot_utils import generate_sample_plot


@router.get("/download/pdf/{symbol}")
def download_pdf(symbol: str):
    generate_sample_plot(symbol)  # PNG üret

    result = get_analysis_result(symbol)
    if not result:
        raise HTTPException(status_code=404, detail="No analysis result found.")

    file_path = f"{symbol}_analysis.pdf"
    plot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plots", f"{symbol}.png"))

    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    # Başlık
    c.drawString(100, 750, f"Analysis Report for {symbol}")

    # Yazılar
    y = 720
    for key, value in result["latest"].items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 20

    # Grafik en alta
    if os.path.exists(plot_path):
        c.drawImage(ImageReader(plot_path), 100, 100, width=400, preserveAspectRatio=True)

    c.save()
    return FileResponse(path=file_path, filename=file_path, media_type="application/pdf")
