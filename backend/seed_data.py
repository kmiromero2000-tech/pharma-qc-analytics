import numpy as np
import pandas as pd
from database import SessionLocal, Base, engine, BatchRecord

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(BatchRecord).count() > 0:
        db.close()
        return

    np.random.seed(42)
    n_batches = 1005

    records = []
    for i in range(1, n_batches + 1):
        api_water = float(np.clip(np.random.normal(1.5, 0.2), 1.0, 2.5))
        api_content = float(np.clip(np.random.normal(98.5, 1.8), 90.0, 105.0))
        lactose_water = float(np.clip(np.random.normal(4.3, 0.3), 3.5, 5.2))
        smcc_water = float(np.clip(np.random.normal(3.3, 0.2), 2.5, 4.0))
        starch_water = float(np.clip(np.random.normal(6.1, 0.15), 5.5, 7.0))

        tbl_av_hardness = float(np.clip(np.random.normal(65.0, 8.0), 35.0, 95.0))
        tbl_rsd_weight = float(np.clip(np.random.normal(0.75, 0.2), 0.3, 2.2))
        tbl_tensile = float(np.clip(np.random.normal(1.5, 0.25), 0.8, 2.5))
        dissolution_av = float(np.clip(np.random.normal(92.0, 4.5), 70.0, 100.0))
        impurities_total = float(np.clip(np.random.normal(0.32, 0.08), 0.1, 0.85))

        is_dev = 1 if (
            dissolution_av < 85.0 or 
            tbl_av_hardness < 48.0 or 
            tbl_rsd_weight > 1.4 or 
            impurities_total > 0.55
        ) else 0

        records.append(
            BatchRecord(
                batch_code=f"LOT-{2018 + (i // 300)}-{i:04d}",
                strength="5MG",
                batch_size=240000.0,
                api_water=api_water,
                api_content=api_content,
                lactose_water=lactose_water,
                smcc_water=smcc_water,
                starch_water=starch_water,
                tbl_av_hardness=tbl_av_hardness,
                tbl_rsd_weight=tbl_rsd_weight,
                tbl_tensile=tbl_tensile,
                dissolution_av=dissolution_av,
                impurities_total=impurities_total,
                is_deviation=is_dev
            )
        )

    db.bulk_save_objects(records)
    db.commit()
    db.close()
    print(f"Cargados exitosamente {n_batches} lotes.")

if __name__ == "__main__":
    seed_database()
