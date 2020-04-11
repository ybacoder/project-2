from flask import (
    Flask,
    render_template,
    jsonify,
    _app_ctx_stack,
    url_for,
    request,
    redirect,
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
from worker import conn
from rq import Queue

models.Base.metadata.create_all(bind=engine)

# initialize db connection & ORM
app = Flask(__name__)
CORS(app)
app.session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)

# for background tasks
queue = Queue(connection=conn)

# to combine querying, scraping, and loading into a single job
def scrape_and_load():
    since = app.session.query(models.Wind.SCEDTimeStamp)[-1][0]
    clean_data.data_scrape(since)
    load.csv_db()

# for redirect after scraping
referring_func_name = "home"
page_names = {
    "home": "Home Page",
    "data": "Data Page",
    "plot1": "Time Series Page",
    "plot2": "Correlation Page",
}

# for `get_data` route (not all columns are necessary for users to see)
DATA_COLUMNS = [
    "SystemLambda",
    "RepeatedHourFlag",
    "System_Wide",
    "LZ_South_Houston",
    "LZ_West",
    "LZ_North",
    "DSTFlag"
]


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
        cmd = app.session.query(
            models.Wind
        )

        if request_start:
            cmd = cmd.filter(
                models.Wind.SCEDTimeStamp
                >= dt.datetime.strptime(request_start, "%Y-%m-%d")
            )

        if request_end:
            cmd = cmd.filter(
                models.Wind.SCEDTimeStamp
                < (dt.datetime.strptime(request_end, "%Y-%m-%d") + dt.timedelta(days=1))
            )

        results = cmd.all()
        data = [
            {result.SCEDTimeStamp.isoformat(): result.to_dict(False, *DATA_COLUMNS)}
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

    results = (
        app.session.query(
            models.Wind.SCEDTimeStamp, models.Wind.System_Wide, models.Wind.SystemLambda
        )
        .filter(models.Wind.System_Wide != 0)
        .all()
    )

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
        "titlefont": {"size": 24},
        "xaxis": {"title": "Timestamp", "titlefont": {"size": 16},},
        "yaxis": {
            "title": "System Lambda ($/MWh)",
            "titlefont": {"color": "#1f77b4", "size": 16},
            "tickfont": {"color": "#1f77b4"},
            "range": [-100, 1000],
            "tick0": 0,
            "dtick": 100,
        },
        "yaxis2": {
            "title": "Wind Generation (MW)",
            "titlefont": {"color": "#ff7f0e", "size": 16},
            "tickfont": {"color": "#ff7f0e"},
            "range": [-2000, 20000],
            "tick0": 0,
            "dtick": 2000,
            "overlaying": "y",
            "side": "right",
        },
        "height": 600,
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
        app.session.query(models.Wind.System_Wide, models.Wind.SystemLambda, models.Wind.SCEDTimeStamp)
        .filter(models.Wind.System_Wide != 0)
        .statement,
        con=engine,
    ).assign(SCEDTimeStamp=lambda df: df.SCEDTimeStamp.apply(
        lambda x: x.hour
    ))

    fig_dict = px.scatter(
        df,
        x="System_Wide",
        y="SystemLambda",
        labels={
            "System_Wide": "Wind Generation (MW)",
            "SystemLambda": "System Lambda ($/MWh)",
            "SCEDTimeStamp": "Hour"
        },
        log_y=True,
        trendline="ols",
        template="simple_white",
        title="System Lambda vs. Wind Generation",
        color="SCEDTimeStamp",
        color_continuous_scale=["blue", "yellow", "blue"],
        opacity=.5,
        height=700
    ).to_dict()

    data = json.dumps(fig_dict["data"], cls=plotly.utils.PlotlyJSONEncoder)
    layout = json.dumps(fig_dict["layout"], cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("plot2.html", data=data, layout=layout)


@app.route("/scrape")
def scrape():

    global referring_func_name

    queue.enqueue(scrape_and_load, job_timeout=1200)  # 20 minutes

    return render_template(
        "scrape.html",
        referring_func_name=referring_func_name,
        page_name=page_names[referring_func_name],
    )


@app.teardown_appcontext
def remove_session(*args, **kwargs):
    app.session.remove()


if __name__ == "__main__":
    app.run(debug=True)
