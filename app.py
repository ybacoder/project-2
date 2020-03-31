from flask import Flask, render_template, jsonify, _app_ctx_stack, url_for, request
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
    """home route"""

    global referring_func
    referring_func = "home"
    
    return render_template("index.html", )


@app.route("/data")
def data_access():
    """return a JSON of requested stored data"""

    global referring_func
    referring_func = "data_access"

    request_start = request.args.get("start")
    request_end = request.args.get("end")

    try:
        base_cmd = app.session.query(models.Wind)

        if request_start:
            base_cmd = base_cmd.filter(
                models.Wind.SCEDTimeStamp >= dt.datetime.strptime(request_start, "%Y-%m-%d")
            )

        if request_end:
            base_cmd = base_cmd.filter(
                models.Wind.SCEDTimeStamp <= dt.datetime.strptime(request_end, "%Y-%m-%d")
            )

        results = base_cmd.all()
        data = [result.to_dict() for result in results]

        return jsonify(data)

    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})


# non-time data vs. time data
@app.route("/timeseries")
def plot1():
    """Return all timeseries data"""

    global referring_func
    referring_func = "plot1"

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

    global referring_func
    referring_func = "plot2"

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

    return render_template("plot2.html", trace=[trace], layout=layout)


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

    return url_for(referring_func)


@app.teardown_appcontext
def remove_session(*args, **kwargs):
    app.session.remove()


if __name__ == "__main__":
    app.run(debug=True)