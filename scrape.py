import requests, time
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

# setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db/emoji.sqlite"
db = SQLAlchemy(app)

# URLs
LAMBDA_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13114&reportTitle=SCED%20System%20Lambda&showHTMLView=&mimicKey"
ACTUAL_WIND_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13071&reportTitle=Wind%20Power%20Production%20-%20Actual%205-Minute%20Averaged%20Values&showHTMLView=&mimicKey"
# HOURLY_ACTUAL_AND_FORECASTED_WIND_URL = "http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13028&reportTitle=Wind%20Power%20Production%20-%20Hourly%20Averaged%20Actual%20and%20Forecasted%20Values&showHTMLView=&mimicKey"


def scrape_CSVs(url):
    """scrape all CSVs from the page and save any that are not already in the database"""

    pass