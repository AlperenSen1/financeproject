import os
import sys
import csv
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.company import Company

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

CSV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/companylist.csv"))

def insert_companies():
    db: Session = SessionLocal()
    with open(CSV_FILE_PATH, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbol = row["Symbol"].strip()
            name = row["Name"].strip()
            if symbol and name:
                exists = db.query(Company).filter_by(symbol=symbol).first()
                if not exists:
                    db.add(Company(symbol=symbol, name=name))
        db.commit()
    db.close()
    print("✅ Şirketler başarıyla eklendi.")

if __name__ == "__main__":
    insert_companies()
