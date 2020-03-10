import requests, time, datetime as dt
from bs4 import BeautifulSoup


# URLs
LAMBDA_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13114&reportTitle=SCED%20System%20Lambda&showHTMLView=&mimicKey"
ACTUAL_WIND_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13071&reportTitle=Wind%20Power%20Production%20-%20Actual%205-Minute%20Averaged%20Values&showHTMLView=&mimicKey"
# HOURLY_ACTUAL_AND_FORECASTED_WIND_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13028&reportTitle=Wind%20Power%20Production%20-%20Hourly%20Averaged%20Actual%20and%20Forecasted%20Values&showHTMLView=&mimicKey"


def csv_link(tr):
    """return the link to the ZIP file if it is for the CSV file; otherwise, None"""

    if tr.td.text.endswith("csv.zip"):
        return tr.find('a')['href']


def scrape_CSVs(url, since=None):
    """scrape any new CSVs from the page and return as a list"""

    r = requests.get(url)
    
    if r.status_code != 200:
        print(f"Got status code {r.status_code} from {url}")

    for tr in BeautifulSoup(r.text).find_all('tr'):
        pass