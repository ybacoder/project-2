from flask import Flask, render_template

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
    return render_template("scrape.html", )


if __name__ == "__main__":
    app.run(debug=True)