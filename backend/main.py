from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
from database import get_db, Base, engine, BatchRecord
from seed_data import seed_database
from analytics import calculate_mspc_metrics, compare_models, FEATURES

app = FastAPI(title="Pharma QC Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    seed_database()

@app.get("/api/summary")
def get_summary(db: Session = Depends(get_db)):
    total = db.query(BatchRecord).count()
    deviations = db.query(BatchRecord).filter(BatchRecord.is_deviation == 1).count()
    compliant = total - deviations
    rate = round((deviations / total) * 100, 2) if total else 0.0

    return {
        "total_batches": total,
        "deviations": deviations,
        "compliant": compliant,
        "deviation_rate": rate,
    }

@app.get("/api/analytics/models")
def get_model_evaluation(db: Session = Depends(get_db)):
    rows = db.query(BatchRecord).all()
    df = pd.DataFrame([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])
    
    comparison, probs = compare_models(df)
    return comparison

@app.get("/api/analytics/mspc")
def get_mspc(limit: int = 150, db: Session = Depends(get_db)):
    rows = db.query(BatchRecord).limit(limit).all()
    df = pd.DataFrame([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    t2, t2_ucl, spe, spe_ucl = calculate_mspc_metrics(df)

    data = []
    for idx, row in df.iterrows():
        is_oot = bool((t2[idx] > t2_ucl) or (spe[idx] > spe_ucl))
        data.append({
            "batch_code": row["batch_code"],
            "t2": round(float(t2[idx]), 3),
            "spe": round(float(spe[idx]), 3),
            "is_oot": is_oot,
            "is_deviation": int(row["is_deviation"]),
            "dissolution_av": row["dissolution_av"],
            "tbl_av_hardness": row["tbl_av_hardness"],
            "tbl_rsd_weight": row["tbl_rsd_weight"]
        })

    return {
        "t2_ucl": round(float(t2_ucl), 3),
        "spe_ucl": round(float(spe_ucl), 3),
        "chart_data": data
    }
