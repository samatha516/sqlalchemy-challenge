import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)

latestDate = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
latestDate = list(np.ravel(latestDate))[0] # this is 2017-08-23

latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d') # 2017-08-23 00:00:00
latestYear = int(dt.datetime.strftime(latestDate, '%Y')) # 2017
latestMonth = int(dt.datetime.strftime(latestDate, '%m')) # 8
latestDay = int(dt.datetime.strftime(latestDate, '%d')) # 23

yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365) # 2016-08-23
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d') # 2016-08-23

@app.route("/")
def home():
    return (f"<h1>Hawaii Climate API</h1>"
            f"<br/>"
            f"<b><u>Available Routes:</u></b></br>"
            f"<ul>"
            f"<li>/api/v1.0/precipitaton &rarr; Latest year of preceipitation data</li><br/>"
            f"<li>/api/v1.0/stations &rarr; Weather observation stations</li><br/>"            
            f"<li>/api/v1.0/tobs &rarr; Latest year of temperature data</li><br/>"
            f"</ul>"
            f"<u><b>datesearch (yyyy-mm-dd):</b></u><br/>"
            f"<ul>"
            f"<li>/api/v1.0/datesearch/yyyy-mm-dd &rarr; Low, High, and Average temperatures starting from search date onwards</li><br/>"
            f"<li>/api/v1.0/datesearch/yyyy-mm-dd/yyyy-mm-dd &rarr; Low, High, and Average temperatures for search date range including the end date</li><br/>"
            f"</ul>"
            f"*******************************************<br/>"
            f"<i>Note: Data available from 2010-01-01 to 2017-08-23 </i><br/>"
            f"*******************************************")

@app.route("/api/v1.0/precipitaton")
def precipitation():
    # date range 2016-08-24 through 2017-08-23
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    precipData = []
    #list of dictionaries
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipDict)

    return jsonify(precipData) # results in json format

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)