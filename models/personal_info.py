from sqlalchemy import Column, Integer, String, Date
from database import Base

class PersonalInfo(Base):
    __tablename__ = "personal_info"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    gender = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    education = Column(String, nullable=False)
    occupation = Column(String, nullable=False)
