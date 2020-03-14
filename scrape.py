import requests
import datetime as dt
from pandas import read_csv
from io import BytesIO
from zipfile import ZipFile
from bs4 import BeautifulSoup
from urllib.request import urlopen


# for determining when "now" is according to ERCOT
TIME_ZONE = 'CST'
TZ_OFFSETS = {
    'CST': 0,
    'PT': -2,
    'EST': 1
}


# URLs
LAMBDA_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13114&reportTitle=SCED%20System%20Lambda&showHTMLView=&mimicKey"
WIND_5MIN_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13071&reportTitle=Wind%20Power%20Production%20-%20Actual%205-Minute%20Averaged%20Values&showHTMLView=&mimicKey"
_ERCOT_BASE_URL = "http://mis.ercot.com"  # required as scraped links don't include this part
# HOURLY_ACTUAL_AND_FORECASTED_WIND_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13028&reportTitle=Wind%20Power%20Production%20-%20Hourly%20Averaged%20Actual%20and%20Forecasted%20Values&showHTMLView=&mimicKey"


def _file_dt(filename, now, year=None):
    """extract the date and time from the filename"""

    # use current year by default
    if year is None:
        year = now.year

    # find the part of the filename that starts with the specified year
    parts = filename.split('.')
    for i, part in enumerate(parts):
        if part.startswith(str(year)):
            date_str = part
            time_str = parts[i + 1]
            break
    else:
        # if no match, try again using last year (e.g. at start of January there could be a delay in publishing) - just for future-proofing, in case we decide to keep this going until next year or later
        return _file_dt(filename, year - 1)
    
    # construct datetime from the date and time strings in the filename
    return dt.datetime(
        year,
        int(date_str[4:6]),
        int(date_str[6:]),
        int(time_str[:2]),
        int(time_str[2:4]),
        int(time_str[4:6])
    )


def data_frame(zip_url):  # resource: https://techoverflow.net/2018/01/16/downloading-reading-a-zip-file-in-memory-using-python/
    """download an unpack the ZIP file in memory; return a DataFrame of the CSV contents"""

    # download ZIP file
    r = urlopen(zip_url)
    assert r.status == 200

    # convert to ZipFile object
    bytes_zf = BytesIO(r.read())
    zf = ZipFile(bytes_zf)

    # inspect
    zip_filenames = zf.namelist()
    assert len(zip_filenames) == 1

    # extract and return as df
    return read_csv(zf.open(zip_filenames[0]))


def data_frames(page_url, base_url=_ERCOT_BASE_URL, since=None, before=None):
    """scrape CSVs from the page and return as a list of associated data

To include additional info in case of errors, each row of the returned list is [datetime of scraping, filename, URL of ZIP file, DataFrame of CSV contents].

Use the `base_url` argument to specify the base URL.

Use the `since` argument (datetime object) to specify how far back to go (exclusive) - e.g. to stop before overlapping with previous data.

If necessary, use the `before` argument (datetime object) to limit the recency of files scraped."""

    now = dt.datetime.now() - dt.timedelta(0, TZ_OFFSETS[TIME_ZONE])

    # use start of 2020 as default "since" date
    if since is None:
        since = now - dt.timedelta(365)
    
    if before is None:
        before = now

    # use today as 

    # initialize with empty list
    data = []  # to be lists of [filename, URL, DataFrame]

    print(f"SCRAPING {page_url}...")
    print("LOCATING DESIRED DOWNLOAD LINKS...")

    try:   
        # get HTML
        r = requests.get(page_url)
        
        # check response status
        assert r.status_code == 200

        # iterate over table rows to get links to desired ZIP files
        for tr in BeautifulSoup(r.text, "lxml").find_all('tr'):

            filename = tr.td.text  # text of first column is the filename

            if filename.endswith("csv.zip"):  # each file also comes in an XML option, but we don't have experience working with XML.
                
                # get date & time of file
                tr_dt = _file_dt(filename, now)
                
                # compare to `since`/`before` limits
                if tr_dt < before:
                    if tr_dt > since:
                        # append filename and link
                        data.append([now, filename, base_url + tr.find('a')['href']])
                    else:
                        break
        
        print(f"\tIDENTIFIED {len(data)} FILES TO DOWNLOAD.")
        print("DOWNLOADING FILES AND EXTRACTING DATA...")

        # iterate over links to get the CSVs
        for row in data:
            # get CSV from ZIP (ensure there is only 1) - in memory
            row.append(data_frame(row[1]))
            print("\tSUCCESS:", row[0])
            
        print("SCRAPING SUCCESSFUL.")
        
    except:
        from traceback import print_exc
        print("A SCRAPING ERROR OCCURRED. TRACEBACK:")
        print_exc()

    return data