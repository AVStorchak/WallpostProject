import backend
import pandas as pd
from flask import Flask, render_template, request, Response

app = Flask(__name__)


class DataContainer():
    pass


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        user = request.form.get('user')
        date = request.form.get('date')
        entry.requested_fields = request.form.getlist('fields')

        if user == '':
            return render_template("id_error.html")
        try:
            query_id = backend.get_query_id(user)
            query_date = backend.get_query_timestamp(date)
        except ValueError:
            return render_template("date_error.html")
        except TypeError:
            return render_template("id_error.html")

        try:
            all_posts = backend.load_posts(query_id, query_date)
        except:
            return render_template("data_load_error.html")
        entry.filtered_posts = backend.filter_posts(all_posts, query_date)
        entry.df = pd.DataFrame(entry.filtered_posts)
        return render_template("save_data.html")


@app.route("/getcsv")
def get_csv():
    posts = entry.filtered_posts
    fields = entry.requested_fields
    csv = backend.compose_csv(posts, fields)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=wall_stats.csv"})


@app.route("/plotyear")
def plot_year():
    df = entry.df
    plot = backend.plot_year_stats(df)
    return Response(plot, mimetype='image/png')


@app.route("/plotmonth")
def plot_month():
    df = entry.df
    plot = backend.plot_month_stats(df)
    return Response(plot, mimetype='image/png')


@app.route("/plotweekday")
def plot_weekday():
    df = entry.df
    plot = backend.plot_weekday_stats(df)
    return Response(plot, mimetype='image/png')


@app.route("/plothour")
def plot_hour():
    df = entry.df
    plot = backend.plot_hour_stats(df)
    return Response(plot, mimetype='image/png')


if __name__ == "__main__":
    entry = DataContainer()
    app.run()
