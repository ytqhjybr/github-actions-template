from app.db.database import engine
from app.models import models  # импорт моделей

def init_db():
    models.Base.metadata.create_all(bind=engine)