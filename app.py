from flask import Flask, render_template, jsonify, _app_ctx_stack, url_for
import scraping
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine, func
from typing import List
from flask_cors import CORS
from database import SessionLocal, engine
import models
import load
import clean_data

models.Base.metadata.create_all(bind=engine)

### initialize db connection & ORM

app = Flask(__name__)
CORS(app)
app.session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)

### Example from 17 Pet Pals example
# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     os.environ.get("JAWSDB_URL", "sqlite:///pets.sqlite") <-- replace the second string with our local db connection string
# )

@app.route("/")
def home():
    return render_template("index.html", )


@app.route("/data")
def data_access():
    """return a JSON of all stored data"""  # doesn't make a lot of sense. adding filtering here (or sub-endpoints like "today" or "latest") is a subject of future work.

    # query = session.query(Data)  # query all rows and columns
    # df = pd.read_sql(query.statement, con=engine)

    return render_template("data.html")


# non-time data vs. time data
@app.route("/timeseries")
def plot1():
    """Return all timeseries data"""

    results = app.session.query(models.Wind)\
        .filter(models.Wind.System_Wide != 0)\
        .all()

    trace1 = {
        "x": [], # Erin to fill in
        "y": [], # Erin to fill in
        "type": "scatter"
    }

    trace2 = {
        "x": [], # Erin to fill in
        "y": [], # Erin to fill in
        "type": "scatter"
    }

    layout = {
      "title": "Wind Generation and System Lambda",
      "height": 700,
      }
    
    return render_template("plot1.html", trace=[trace1, trace2], layout=layout)

# non-time data vs. non-time data
@app.route("/correlation")
def plot2():
    """Return all non-zero non-timeseries data"""

    results = app.session.query(models.Wind)\
        .filter(models.Wind.System_Wide != 0)\
        .all()

    trace = {
        "x": [result.System_Wide for result in results],
        "y": [result.SystemLambda for result in results],
        "mode": "markers",
        "type": "scatter"
    }

    layout = {
      "title": "Wind Generation vs. System Lambda",
      "xaxis": {
          "title": "Wind Generation"
      },
      "yaxis": {
          "title": "System Lambda"
      },
      "height": 700,
      }
    
    return render_template("plot2.html", trace=trace, layout=layout)


@app.route("/scrape")
def scrape():

    # get "since" date to avoid longer-than-necessary scrapes
    since = app.session.query(models.Wind.SCEDTimeStamp)[-1][0]
    print(since, since[0], sep='\n')
    input()

    # scrape
    clean_data.data_scrape(since)

    # load into db
    load.csv_db()

    return "Scraping Complete"


@app.teardown_appcontext
def remove_session(*args, **kwargs):
    app.session.remove()


if __name__ == "__main__":
    app.run(debug=True)