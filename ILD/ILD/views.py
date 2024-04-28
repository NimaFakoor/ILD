"""
Routes and views for the flask application.
"""

from flask import render_template

import os
import logging
from datetime import datetime
from sqlalchemy.inspection import inspect
from collections import defaultdict
from venv import create
import pandas as pd
import datetime as dt
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    jsonify,
    abort,
)
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_sqlalchemy import SQLAlchemy

from ILD import app, db
from ILD.database import *

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Renders the dashboard page."""
    return render_template(
        'index.html',
        title='dashboard'
    )

@app.route('/report')
def report():
    """Renders the report page."""
    
    return render_template(
        'report.html',
        title='report'
    )

@app.route("/add/report", methods=["POST"])
def add_report():
    """Adds new report to the database."""
    
    report_entry = Report(latitude=request.form["latitude"],longitude=request.form["longitude"],origin=request.form["origin"],phone=request.form["phone"],description=request.form["description"])
    db.session.add(report_entry)
    db.session.commit()
    error = "گزارش ایجاد شد"
    flash(error)
    return redirect(url_for("dashboard"))

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )