from database import Base
from sqlalchemy import Column, Integer, String

# class Financial(Base):
#     id = Column(Integer, primary_key=True, index=True)
#     Segment = Column(String(100)) 
#     Country = Column(String(100))
#     Discount_Band = Column(String(100))
#     Units_Sold = Column(String(100))
#     Manufacturing_Price = Column(String(100))
#     Sale_Price = Column(String(100))
#     Gross_Sales = Column(String(100))
#     Discounts = Column(String(100))
#     Sales = Column(String(100))
#     COGS = Column(String(100))
#     Profit = Column(String(100))
#     Date = Column(String(100))
#     Month_Number = Column(String(100))
#     Month_Name = Column(String(100))
#     Year = Column(String(100))

class Patients(Base):
    __tablename__ = "PatientsData"
    Patient_ID = Column(Integer, primary_key=True)
    Age = Column(Integer)
    Gender = Column(String(50))
    Diagnosis = Column(String(200))
    Admitted = Column(String(200))