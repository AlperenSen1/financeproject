from app.database.database import Base, engine
from app.models.company import Company

print(" Creating tables...")
Base.metadata.create_all(bind=engine)
print(" Done.")
