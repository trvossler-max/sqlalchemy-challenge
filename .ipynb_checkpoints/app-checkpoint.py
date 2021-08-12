import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Home Page and Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the SQL-Alchemy API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date [Format: yyyy-mm-dd] <br/>"
        f"/api/v1.0/start_date/end_date [Format: yyyy-mm-dd]"
    )

#api to return a JSON representation of the precipitation dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of dates and precipitation values"""
    # Query all dates
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date > '2016-08-23').\
    order_by(measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

#api to return a list of stations.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query to return a JSON list of stations from the dataset.
    st_results = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list of stations

    all_stations = []
    for station, name, latitude, longitude, elevation in st_results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["lat"] = latitude
        station_dict["lon"] = longitude
        station_dict["elev"] = elevation

    return jsonify(all_stations)

#api to return return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    # Query to return a JSON list of temps from the most active stations for the past 12 months.
    temp_results = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date > '2016-08-23').\
    filter(measurement.station == 'USC00519281').\
    order_by(measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(temp_results))

    return jsonify(all_temps)

# api to return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range.
@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperatures"""
    # Query to return a JSON list of min, max, and average temps.
    sel = [measurement.tobs, 
       func.min(measurement.tobs), 
       func.avg(measurement.tobs), 
       func.max(measurement.tobs)]
    
    temp_stats = session.query(*sel).\
        filter(measurement.date >= start_date).all()

    session.close()

# Convert list of tuples into normal list
    temps = list(np.ravel(temp_stats))

    return jsonify(temps)

# api to Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

@app.route("/api/v1.0/<start_date>/<end_date>")
def date_range(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperatures"""
    # Query to return a JSON list of min, max, and average temps.
    sel = [measurement.tobs, 
       func.min(measurement.tobs), 
       func.avg(measurement.tobs), 
       func.max(measurement.tobs)]
    
    temps_stats = session.query(*sel).\
        filter(measurement.date >= start_date).\
        filter(measurement.date <= end_date).all()

    session.close()

# Convert list of tuples into normal list
    dtemps = list(np.ravel(temps_stats))

    return jsonify(dtemps)


if __name__ == "__main__":
    app.run(debug=True)