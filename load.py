import scraping
import clean_data
import csv
import datetime
import pandas as pd
import models
from database import SessionLocal, engine

db = SessionLocal()

models.Base.metadata.create_all(bind=engine)

scrape_date = datetime.datetime.today().strftime("%m.%d.%Y")

def csv_db():

    with open(f"scrape_{scrape_date}.csv", "r") as f:

        csv_reader = csv.DictReader(f)

        for row in csv_reader:
            wind_db = models.Wind(
                lambda_filename = row["filename_x"],
                lambda_file_url = row["file_url_x"],
                wind_filename = row["filename_y"],
                wind_file_url = row["file_url_y"],
                SCEDTimeStamp = row["SCEDTimeStamp"],
                SystemLambda =  row["SystemLambda"],
                RepeatedHourFlag = row["RepeatedHourFlag"],
                System_Wide = row["SYSTEM_WIDE"],
                LZ_South_Houston = row["LZ_SOUTH_HOUSTON"],
                LZ_West = row["LZ_WEST"],
                LZ_North = row["LZ_NORTH"],
                DSTFlag = row["DSTFlag"]
            )
            db.add(wind_db)
        db.commit()
    db.close()

    return "Scraping Complete"