import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

os.makedirs("data", exist_ok=True)
DATABASE_URL = "sqlite:///./data/pharma_qc.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BatchRecord(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String, unique=True, index=True)
    strength = Column(String, default="5MG")
    batch_size = Column(Float, default=240000)
    created_at = Column(DateTime, default=datetime.utcnow)

    # CPPs
    api_water = Column(Float)
    api_content = Column(Float)
    lactose_water = Column(Float)
    smcc_water = Column(Float)
    starch_water = Column(Float)

    # CQAs
    tbl_av_hardness = Column(Float)
    tbl_rsd_weight = Column(Float)
    tbl_tensile = Column(Float)
    dissolution_av = Column(Float)
    impurities_total = Column(Float)

    # Calificación analítica
    is_deviation = Column(Integer, default=0)
    t2_score = Column(Float, nullable=True)
    spe_score = Column(Float, nullable=True)
    risk_prob = Column(Float, nullable=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
