import scraping
import load
import csv
import datetime
import pandas as pd

import models
from database import SessionLocal, engine

db = SessionLocal()

models.Base.metadata.create_all(bind=engine)

def data_scrape(since):
    lambda_scrape = scraping.get_data(scraping.LAMBDA_URL, since=since)
    wind_scrape = scraping.get_data(scraping.WIND_5MIN_URL, since=since)

    #Lambda Data Munging
    lambda_scrape_df = pd.DataFrame(lambda_scrape, columns= ["datetime", "filename", "file_url", "file_data"])
    lambda_data = list(lambda_scrape_df["file_data"])
    split_lambda = [str(line).split(" ") for line in lambda_data]
    final_lambda_data = []
    for e in split_lambda:
        filter_object = filter(lambda x: x != "", e)
        final_lambda_data.append(list(filter_object))

    lambda_data_df = pd.DataFrame(final_lambda_data)
    lambda_data_df = lambda_data_df.drop(columns = [0,1,2])
    lambda_data_df[3] = lambda_data_df[3] + " " + lambda_data_df[4]
    lambda_data_df = lambda_data_df.drop(columns = [4])
    lambda_data_df = lambda_data_df.rename(columns = {3: "SCEDTimeStamp", 5: "RepeatedHourFlag", 6: "SystemLambda"})
    lambda_scrape_df = lambda_scrape_df.drop(columns = ["file_data"])
    final_lambda_df = pd.concat([lambda_scrape_df, lambda_data_df], axis=1, sort=False)
    final_lambda_df['SCEDTimeStamp'] = pd.to_datetime(final_lambda_df['SCEDTimeStamp']).apply(lambda t: t.replace(second=0))
    

    # Wind Data Munging
    wind_scrape_df = pd.DataFrame(wind_scrape, columns= ["datetime", "filename", "file_url", "file_data"])
    wind_data = list(wind_scrape_df["file_data"])
    split_wind = [str(line).split(" ") for line in wind_data]
    final_wind_data = []
    for e in split_wind:
        filter_object = filter(lambda x: x != "", e)
        final_wind_data.append(list(filter_object))
    
        def Extract(final_wind_data): 
            return [item[83:90] for item in final_wind_data]

    wind_data_extract= Extract(final_wind_data)
    wind_data_df = pd.DataFrame(wind_data_extract)
    wind_data_df[0] = wind_data_df[0] + " " + wind_data_df[1]
    wind_data_df = wind_data_df.drop(columns = [1])
    wind_data_df = wind_data_df.rename(columns = {0: "SCEDTimeStamp", 2: "SYSTEM_WIDE", 3: "LZ_SOUTH_HOUSTON", 4: "LZ_WEST", 5: "LZ_NORTH", 6: "DSTFlag"})
    wind_scrape_df = wind_scrape_df.drop(columns = ["file_data"])
    final_wind_df = pd.concat([wind_scrape_df, wind_data_df], axis=1, sort=False)
    final_wind_df['SCEDTimeStamp'] = pd.to_datetime(final_wind_df['SCEDTimeStamp']).apply(lambda t: t.replace(second=0))

    
    #Create Final Dataframe
    final_df_df = pd.merge(final_lambda_df, final_wind_df, on=["SCEDTimeStamp"], how="outer").sort_values("SCEDTimeStamp")

    scrape_date = datetime.datetime.today().strftime("%m.%d.%Y")

    final_df_df.to_csv(f"scrape_{scrape_date}.csv", index=False)


    return final_df_df.to_csv(f"scrape_{scrape_date}.csv", index=False)