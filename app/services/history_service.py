# app/services/history_service.py

from sqlalchemy.orm import Session
from app.models.analysis_history import AnalysisHistory
import json

def save_analysis(db: Session, username: str, symbol: str, indicators: list, result: dict):
    history = AnalysisHistory(
        username=username,
        symbol=symbol,
        indicators=",".join(indicators),
        result=json.dumps(result)
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

import json
from sqlalchemy.orm import Session
from app.models.analysis_history import AnalysisHistory

def get_user_history(db: Session, username: str, limit: int = 10):
    records = db.query(AnalysisHistory)\
                .filter_by(username=username)\
                .order_by(AnalysisHistory.created_at.desc())\
                .limit(limit).all()

    return [
        {
            "id": r.id,
            "username": r.username,
            "symbol": r.symbol,
            "indicators": r.indicators,
            "created_at": r.created_at,
            "result": json.loads(r.result) if r.result else None
        }
        for r in records
    ]
