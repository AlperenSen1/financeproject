from app.services.ai_model import predict_ai_signal

if __name__ == "__main__":
    symbol = "AAPL"
    prediction, confidence = predict_ai_signal(symbol)
    print(f"{symbol} için AI Tahmini: {prediction} (Güven: {confidence})")
