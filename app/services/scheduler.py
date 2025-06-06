import yfinance as yf
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services import stock_analysis
from app.logging_config import logger
from app.services.stock_analysis import calculate_all_indicators


def run_scheduled_analysis():
    print(" run_scheduled_analysis() tetiklendi")
    logger.info("Running scheduled analysis...")

    symbols = ["AAPL", "MSFT", "GOOGL"]
    all_indicators = ["sma", "ema", "rsi", "macd", "z_score", "bollinger"]

    for symbol in symbols:
        try:
            print(f" Analiz başlatılıyor: {symbol}")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo", interval="1d")
            if hist.empty:
                warning_msg = f"No data for {symbol}"
                print(f" {warning_msg}")
                logger.warning(warning_msg)
                continue

            hist.reset_index(inplace=True)
            hist = stock_analysis.calculate_all_indicators(hist, selected_indicators=all_indicators)
            latest = stock_analysis.extract_latest_values(hist)
            signals = stock_analysis.generate_signals(latest)
            decision = stock_analysis.calculate_weighted_decision(signals)

            log_msg = f"[{symbol}] Final Decision: {decision}"
            print(f" {log_msg}")
            logger.info(log_msg)

        except Exception as e:
            err_msg = f"[{symbol}] Error during scheduled analysis: {e}"
            print(f" {err_msg}")
            logger.error(err_msg)


def start_scheduler():
    print(" start_scheduler() çağrıldı")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_scheduled_analysis, 'interval', seconds=10)
    scheduler.start()
    logger.info(" Scheduler started.")
