"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from ILD import app

@app.route('/')
@app.route('/dashborad')
def dashborad():
    """Renders the dashborad page."""
    return render_template(
        'index.html',
        title='dashborad'
    )

@app.route('/report')
def report():
    """Renders the report page."""
    
    return render_template(
        'report.html',
        title='report'
    )

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
