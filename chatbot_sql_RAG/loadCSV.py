import pandas as pd
from database import get_db, Base, engine
from model import Patients
from sqlalchemy.exc import SQLAlchemyError

class LoadCSV:
    def __init__(self, path, expectedHeader):
        self.dataframe = pd.read_csv(path)
        self.expectedHeader = expectedHeader
    
    def convertToModel(self):
        # TODO: make it generic for any kind of CSV.
        missing = [c for c in self.expectedHeader if c not in self.dataframe.columns]
        if missing:
            raise ValueError(f"CSV missing required columns: {missing}")
        df = self.dataframe[self.expectedHeader].copy()
        df = df.where(pd.notnull(df), None)
        for col in ("Patient_ID", "Age"):
            df[col] = df[col].astype("Int64")
            
        records = df.to_dict(orient="records")
        print("All Good from convertToModel")
        return [Patients(**rec) for rec in records]

        
    def loadToSQLDB(self):
        Base.metadata.create_all(bind=engine)
        objs = self.convertToModel()

        # Acquire a session from the generator
        db_gen = get_db()
        db = next(db_gen)
        try:
            # Fast bulk insert
            db.bulk_save_objects(objs)
            db.commit()
            print("All Good from loadToSQLDB ", len(objs))
            return len(objs)
        except SQLAlchemyError:
            db.rollback()
            raise
        finally:
            # Exhaust generator so its finally runs (calls close)
            try:
                next(db_gen)
            except StopIteration:
                pass