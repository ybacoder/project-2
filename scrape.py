import requests
import time
import datetime as dt
import pandas as pd
import io
import zipfile
from bs4 import BeautifulSoup
from urllib.request import urlopen


# URLs
LAMBDA_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13114&reportTitle=SCED%20System%20Lambda&showHTMLView=&mimicKey"
WIND_5MIN_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13071&reportTitle=Wind%20Power%20Production%20-%20Actual%205-Minute%20Averaged%20Values&showHTMLView=&mimicKey"
# HOURLY_ACTUAL_AND_FORECASTED_WIND_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13028&reportTitle=Wind%20Power%20Production%20-%20Hourly%20Averaged%20Actual%20and%20Forecasted%20Values&showHTMLView=&mimicKey"


# this year - for locating dates
this_year = dt.date.today().year


def file_dt(filename, year=None):
    """extract the date and time from the filename"""

    # use current year by default
    if year is None:
        year = this_year

    # find the part of the filename that starts with the specified year
    parts = filename.split('.')
    for i, part in enumerate(parts):
        if part.startswith(str(year)):
            date_str = part
            time_str = parts[i + 1]
            break
    else:
        # if no match, try again using last year (e.g. at start of January there could be a delay in publishing)
        return file_dt(filename, year - 1)
    
    # construct datetime from the date and time strings in the filename
    return dt.datetime(
        date_str[:4],
        date_str[4:6],
        date_str[6:],
        time_str[:2],
        time_str[2:4],
        time_str[4:6]
    )


def data_frame(zip_url):  # resource: https://techoverflow.net/2018/01/16/downloading-reading-a-zip-file-in-memory-using-python/
    """download an unpack the ZIP file in memory; return a DataFrame of the CSV contents"""

    # download ZIP file
    r = urlopen(zip_url)
    assert(r.status_code == 200)

    # convert to ZipFile object
    bytes_zf = BytesIO(r.read())
    zf = zipfile.ZipFile(bytes_zf)

    # inspect
    zip_filenames = zf.namelist()
    assert(len(zip_filenames) == 1)

    # extract and return as df
    return pd.read_csv(zf.open(zip_filenames[0]))

def data_frames(ercot_url, since=None):
    """scrape any new CSVs from the page and return as a list - since a certain time (datetime object), if specified"""

    # use start of 2020 as default limiting date
    if since is None:
        since = dt.datetime(2020, 1, 1)

    # get HTML
    r = requests.get(ercot_url)
    
    # check response status
    if r.status_code != 200:
        print(f"Got status code {r.status_code} from {url}")
    
    # initialize with empty list
    links = []  # to be tuples of (datetime, URL)

    # iterate over table rows to get links to desired ZIP files
    for tr in BeautifulSoup(r.text).find_all('tr'):

        filename = tr.td.text  # text of first column is the filename

        if filename.endswith("csv.zip"):  # each file also comes in an XML option, but we don't have experience working with XML.
            
            # get date & time of file
            tr_dt = file_dt(filename)
            
            # compare to "since" limit
            if tr_dt > since:
                # append file link
                links.append((tr_dt, tr.find('a')['href']))
            else:
                break
        
    # iterate over links to get the CSVs
    for link in links:

        # get CSV from ZIP (ensure there is only 1) - in memory
        zip_csvs = list(csv_files(link))
        assert len(zip_csvs) == 1
        csv_file = zip_csvs[0]

        # get data from CSV
        df = pd.read_csv(csv_file)