# import necessary libraries
import os
import numpy as np
import pandas as pd
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
# Python SQL tools
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Flask Setup

app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///DataSets/belly_button_biodiversity.sqlite"

engine= create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True )

Samples = Base.classes.samples
Otu = Base.classes.otu
samples_Metadata = Base.classes.samples_metadata

session = Session(engine)


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/names')
def names():
    stmt = session.query(Samples).statement
    df=pd.read_sql_query(stmt, session.bind)
    df.set_index('otu_id', inplace=True)
    return jsonify(list(df.columns))

@app.route('/otu')
def otu():
    # stmt2 = session.query(Samples).statement
    # df=pd.read_sql_query(stmt2, session.bind)
    # df.set_index('otu_id', inplace=True)
    results = session.query(Otu.lowest_taxonomic_unit_found).all()
    return jsonify(results)
    
    


@app.route('/metadata/<sample>')
def metadata_sample(sample):
    sample=str(sample)
    sample=sample.split("_")[1]
    result_sample = session.query(samples_meta_db.AGE,samples_meta_db.BBTYPE,samples_meta_db.ETHNICITY,samples_meta_db.GENDER,samples_meta_db.LOCATION,samples_meta_db.SAMPLEID).filter(samples_meta_db.SAMPLEID==sample).first()
    
    sample_dict={}
    names = ["Age", "BBTYPE", "ETHNICITY","GENDER","LOCATION","SAMPLEID"]
    for i in range(len(names)):
        sample_dict[names[i]]=result_sample[i]
    return jsonify(sample_dict)


@app.route('/wfreq/<sample>')
def wfreq(sample):
    sample=str(sample)
    sample=sample.split("_")[1]
    result_wfreq= session.query(samples_meta_db.WFREQ).filter(samples_meta_db.SAMPLEID==sample).first()

    return jsonify(result_wfreq[0])

@app.route('/samples/<sample>')
def samp_samples(sample):
    sample=str(sample)
    #to dynamically select column, use getattr
    result_samples_desc = session.query(samples_db.otu_id,getattr(samples_db, sample)).order_by(getattr(samples_db, sample).desc()).all()
    
    otu_list=[]
    sample_list=[]
    for i in result_samples_desc:
        otu_list.append(i[0])
        sample_list.append(i[1])
        sample_otu_dict={}
    sample_otu_dict["otu_ids"]=otu_list
    sample_otu_dict["sample_values"]=sample_list
    sample_otu_list=[]
    sample_otu_list.append(sample_otu_dict)
    return jsonify(sample_otu_list)


if __name__ == '__main__':
    app.run(debug=True,port=3316)