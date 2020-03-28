from flask import Flask, render_template, jsonify, _app_ctx_stack, url_for
import scraping
import pandas as pd
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


### needs to be tested
@app.route("/data")
def data_access():
    """return a JSON of all stored data"""  # doesn't make a lot of sense. adding filtering here (or sub-endpoints like "today" or "latest") is a subject of future work.

    query = session.query(Data)  # query all rows and columns
    df = pd.read_sql(query.statement, con=engine)

    return jsonify(df.to_dict)

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

    # get "since" date to 
    since = app.session.query(models.Wind.SCEDTimeStamp).last()[0]

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