"""
The flask application package.
"""

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import pandas as pd

SECRET_KEY = "Sarina+Kiana"
DATABASE = 'sqlite:///../ILD/database/local_DB.db'
SQLALCHEMY_ECHO = True
UPLOAD_FOLDER = 'ILD\\static\\uploads'
UPLOAD_FOLDER_ZONES = 'ILD\\static\\uploads\\zones'
UPLOAD_FOLDER_IMAGES = 'ILD\\static\\images'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_ZONES'] = UPLOAD_FOLDER_ZONES
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES

db = SQLAlchemy(app,session_options={"autoflush": False})

Base = declarative_base()

# Engine & session
engine = create_engine('sqlite:///:memory:', echo=True)
db.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

import ILD.views