# import necessary libraries
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

from flask import Flask, render_template, jsonify,request
from flask_sqlalchemy import SQLAlchemy

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///belly_button_biodiversity.sqlite"

db = SQLAlchemy(app)

# Reflect database schema
# Create engine using the `demographics.sqlite` database file
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Print all of the classes mapped to the Base
Base.classes.keys()

# Assign each class to a variable 
OTU = Base.classes.otu
Samples = Base.classes.samples
samples_metadata = Base.classes.samples_metadata

# Create a session
session = Session(engine)

# Define app routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/names")
def sample_names():
	samples_list = Samples.__table__.columns.keys()
	return jsonify(samples_list)

@app.route("/otu")
def otu():
    otu_descriptions = session.query(OTU.lowest_taxonomic_unit_found).all()
    otu_descriptions_list = [x for (x), in otu_descriptions]
    return jsonify(otu_descriptions_list)

@app.route("/otu_descriptions")
def otu_disc():
    otu_descriptions = session.query(OTU.otu_id, OTU.lowest_taxonomic_unit_found).all()
    otu_dict = {}
    for row in otu_descriptions:
        otu_dict[row[0]] = row[1]
    return jsonify(otu_dict)

@app.route("/metadata/<sample>")
def sample_query(sample):
    sample_name = sample.replace("BB_", "")
    result = session.query(samples_metadata.AGE, samples_metadata.BBTYPE, samples_metadata.ETHNICITY, samples_metadata.GENDER, samples_metadata.LOCATION, samples_metadata.SAMPLEID).filter_by(SAMPLEID = sample_name).all()
    record = result[0]
    record_dict = {
        "AGE": record[0],
        "BBTYPE": record[1],
        "ETHNICITY": record[2],
        "GENDER": record[3],
        "LOCATION": record[4],
        "SAMPLEID": record[5]
    }
    return jsonify(record_dict)

@app.route('/wfreq/<sample>')
def wash_freq(sample):
    sample_name = sample.replace("BB_", "")
    result = session.query(samples_metadata.WFREQ).filter_by(SAMPLEID = sample_name).all()
    wash_freq = result[0][0]
    return jsonify(wash_freq)

@app.route('/samples/<sample>')
def otu_data(sample):
    sample_query = "Samples." + sample
    result = session.query(Samples.otu_id, sample_query).order_by((sample_query)).all()
    otu_ids = [result[x][0] for x in range(len(result))]   
    sample_values = [result[x][1] for x in range(len(result))]
    dict_list = [{"otu_ids": otu_ids}, {"sample_values": sample_values}]
    return jsonify(dict_list)

if __name__ == '__main__':
    app.run(debug=True)