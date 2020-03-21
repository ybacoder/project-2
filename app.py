from flask import Flask, render_template
import scrape as _scrape
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

### initialize db connection & ORM

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", )


@app.route("/data")
def data_access():
    return render_template("data.html", )

# non-time data vs. time data
@app.route("/timeseries")
def plot1():
    return render_template("plot1.html", )


# non-time data vs. non-time data
@app.route("/correlation/<query>")
def plot2(query):

    ### per Erin's testing specifications
    
    return render_template("plot2.html", )


@app.route("/scrape")
def scrape():

    ### query db to find date of most recent scrape

    # scrape
    lambda_scrape = scrape.get_data(scrape.LAMBDA_URL, since=last_date)
    wind_scrape = scrape.get_data(scrape.WIND_5MIN_URL, since=last_date)

    ### get necessary data and create new df to put in db
    ### necessary data is time of scrape + df contents
    ### wind data only need 1st row
    ### put in db

    return render_template("scrape.html", )


if __name__ == "__main__":
    app.run(debug=True)