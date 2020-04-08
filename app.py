from flask import (
    Flask,
    render_template,
    jsonify,
    _app_ctx_stack,
    url_for,
    request,
    redirect
)
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
import json
import plotly
import numpy
import plotly.express as px

models.Base.metadata.create_all(bind=engine)

# initialize db connection & ORM
app = Flask(__name__)
CORS(app)
app.session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)

# for redirect after scraping
referring_func_name = None


@app.route("/")
def home():
    """home route"""

    global referring_func_name
    referring_func_name = "home"

    return render_template("index.html",)


@app.route("/get_data")
def data_access():
    """return a JSON of requested stored data"""

    global referring_func_name
    referring_func_name = "data_access"

    request_start = request.args.get("start")
    request_end = request.args.get("end")

    try:
        base_cmd = app.session.query(
            models.Wind.SCEDTimeStamp,
            models.Wind.RepeatedHourFlag,
            models.Wind.SystemLambda,
            models.Wind.System_Wide,
            models.Wind.LZ_North,
            models.Wind.LZ_South_Houston,
            models.Wind.LZ_West
        )

        if request_start:
            base_cmd = base_cmd.filter(
                models.Wind.SCEDTimeStamp
                >= dt.datetime.strptime(request_start, "%Y-%m-%d")
            )

        if request_end:
            base_cmd = base_cmd.filter(
                models.Wind.SCEDTimeStamp
                < (dt.datetime.strptime(request_end, "%Y-%m-%d") + dt.timedelta(days=1))
            )

        results = base_cmd.all()
        data = [
            {result.SCEDTimeStamp.isoformat(): result.to_dict(False)}
            for result in results
        ]

        return jsonify(data)

    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)})


@app.route("/data")
def data():

    global referring_func_name
    referring_func_name = "data"

    return render_template("data.html")


@app.route("/timeseries")
def plot1():
    """Return all timeseries data"""

    global referring_func_name
    referring_func_name = "plot1"

    results = app.session.query(
            models.Wind.SCEDTimeStamp,
            models.Wind.System_Wide,
            models.Wind.SystemLambda
        )\
        .filter(models.Wind.System_Wide != 0)\
        .all()

    trace1 = {
        "x": [result.SCEDTimeStamp for result in results],
        "y": [result.SystemLambda for result in results],
        "name": "System Lambda ($/MWh)",
        "type": "scatter",
    }

    trace2 = {
        "x": [result.SCEDTimeStamp for result in results],
        "y": [result.System_Wide for result in results],
        "name": "Wind Generation (GW)",
        "type": "scatter",
        "yaxis": "y2",
    }

    layout = {
        "title": "Wind Generation and System Lambda vs. Time",
        "titlefont": {
            "size": 24
        },
        "xaxis": {
            "title": "Timestamp",
            "titlefont": {
                "size": 16
            },
        },
        "yaxis": {
            "title": "System Lambda ($/MWh)",
            "titlefont": {
                "color": "#1f77b4",
                "size": 16
            },
            "tickfont": {"color": "#1f77b4"},
            "range": [-100, 1000],
            "tick0": 0,
            "dtick": 100,
        },
        "yaxis2": {
            "title": "Wind Generation (GW)",
            "titlefont": {
                "color": "#ff7f0e",
                "size": 16
            },
            "tickfont": {"color": "#ff7f0e"},
            "range": [-2000, 20000],
            "tick0": 0,
            "dtick": 2000,
            "overlaying": "y",
            "side": "right",
        },
        "height": 700,
    }

    data = [trace1, trace2]
    data_json = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("plot1.html", data_json=data_json, layout=layout)


@app.route("/correlation")
def plot2():
    """Return all non-zero non-timeseries data"""

    global referring_func_name
    referring_func_name = "plot2"

    df = pd.read_sql(
        
        app.session.query(
            models.Wind.System_Wide,
            models.Wind.SystemLambda
        )
        .filter(models.Wind.System_Wide != 0)
        .statement,

        con = engine

    )

    fig_dict = px.scatter(df, x="System_Wide", y="SystemLambda", log_y=True, trendline="ols").to_dict()
    data = json.dumps(fig_dict["data"], cls=plotly.utils.PlotlyJSONEncoder)
    layout = json.dumps(fig_dict["layout"], cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("plot2.html", data=data, layout=layout)


@app.route("/scrape")
def scrape():

    global referring_func_name

    # get "since" date to avoid longer-than-necessary scrapes
    since = app.session.query(models.Wind.SCEDTimeStamp)[-1][0]

    # scrape
    clean_data.data_scrape(since)

    # load into db
    load.csv_db()

    return (
        redirect(url_for(referring_func_name))
        if referring_func_name
        else "Database import complete!"
    )


@app.teardown_appcontext
def remove_session(*args, **kwargs):
    app.session.remove()


if __name__ == "__main__":
    app.run(debug=True)
