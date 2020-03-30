from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime


class DictMixIn:
    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(
                getattr(self, column.name), (datetime.datetime, datetime.date)
            )
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


class Wind(Base, DictMixIn):
    __tablename__ = "wind_data"

    id = Column(Integer, primary_key=True, index=True)
    lambda_filename = Column(String(250), nullable=True)
    lambda_file_url = Column(String(250), nullable=True)
    wind_filename = Column(String(250), nullable=True)
    wind_file_url = Column(String(250), nullable=True)
    SCEDTimeStamp = Column(DateTime, nullable=True)
    SystemLambda = Column(Float, nullable=True)
    RepeatedHourFlag = Column(String(250), nullable=True)
    System_Wide = Column(Float, nullable=True)
    LZ_South_Houston = Column(Float, nullable=True)
    LZ_West = Column(Float, nullable=True)
    LZ_North = Column(Float, nullable=True)
    DSTFlag = Column(String(250), nullable=True)