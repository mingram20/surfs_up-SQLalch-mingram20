# Import depencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False}, echo=True)

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def homePage():
    # List all routes that are available
    return'''<html>
    <h1> List of all API Routes for Hawaii</h1>
    <ul>
    <br>
    <li>
    Returns a list of precipitations from hte prior year:
    <br>
    <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
    Return a JSON list of the stations from the database: 
    <br>
    <a href='/api/v1.0/stations'>/api/v1.0/stations</a>
    </li>
    <br>
    <li>
    Return a JSON list of Temperature Observations (tobs) for the previous year:
    <br>
    <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a>
    </li>
    <br>
    <li>
    Return a JSON list of tripMin, tripMax, tripAvg for the dates greater than or equal to the date provided:
    <br>Replace &ltstart&gt with a date in Year-Month-Day format.
    <br>
    <a href='/api/v1.0/2017-03-17'>/api/v1.0/2017-03-17</a>
    </li>
    <br>
    <li>
    Return a JSON list of tripMin, tripMax, tripAvg for the dates in range of start date and end date inclusive:
    <br>
    Replace &ltstart&gt and &ltend&gt with a date in Year-Month-Day format. 
    <br>
    <a href='/api/v1.0/2017-03-17/2017-04-09'>/api/v1.0/2017-03-17/2017-04-09</a>
    </li>
    </ul>
    </html>
    '''

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Description of this function 
    '''Returns a list of precipitations from last year'''
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    maxDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    maxDate = maxDate[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    priorYear = dt.datetime.strptime(maxDate, '%Y-%m-%d') - dt.timedelta(days=366)
    
    # Perform a query to retrieve the date and precipitation scores
    queryYear = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= priorYear).all()

    # Convert list of tuples into dictionary
    prcpDict = dict(queryYear)

    return jsonify(prcpDict)

@app.route('/api/v1.0/stations')
def stations(): 
    # # Description of this function
    '''Return a JSON list of stations from the dataset.'''
    # Query stations and group by unique stations
    stationQuery =  session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into a list
    stationList = list(np.ravel(stationQuery))

    return jsonify(stationList)

@app.route('/api/v1.0/tobs')
def tobs(): 
    # # Description of this function
    '''Return a JSON list of Temperature Observations (tobs) for the previous year.'''

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    maxDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    maxDate = maxDate[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    priorYear = dt.datetime.strptime(maxDate, '%Y-%m-%d') - dt.timedelta(days=366)
    # Query tobs
    tempQuery = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= priorYear).all()

    # Convert list of tuples into normal list
    tempList = list(tempQuery)

    return jsonify(tempList)

@app.route('/api/v1.0/<start>')
def start(start=None):
    # Description of this function
    '''Return a JSON list of tripMin, tripMax, tripAvg for the dates greater than or equal to the date provided'''

    fromStart = session.query(Measurement.date, func.min(Measurement.tobs), func.\
        avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.\
            date >= start).group_by(Measurement.date).all()

    # Convert query into a list
    fromStartList=list(fromStart)
    return jsonify(fromStartList)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start=None, end=None):
    # Description of this function
    '''Return a JSON list of tripMin, tripMax, tripAvg for the dates in range of start date and end date inclusive'''
    
    betweenDates = session.query(Measurement.date, func.min(Measurement.tobs), func.\
        avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.\
            date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
            
    # Convert query into a list
    betweenDatesList=list(betweenDates)
    return jsonify(betweenDatesList)

if __name__ == '__main__':
    app.run(debug=True)