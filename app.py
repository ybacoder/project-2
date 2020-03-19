from flask import Flask, render_template
import scrape
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


@app.route("/plot")
def plot():
    return render_template("plot.html", )


@app.route("/scrape")
def scrape():

    ### query db to find date of most recent scrape

    # scrape
    lambda_scrape = scrape.get_data(scrape.LAMBDA_URL, since=last_date)
    wind_scrape = scrape.get_data(scrape.WIND_5MIN_URL, since=last_date)

    ### get necessary data and create new df to put in db
    ### necessary data is time of scrape + df contents
    ### wind data only need 1st row

    return render_template("scrape.html", )


if __name__ == "__main__":
    app.run(debug=True)