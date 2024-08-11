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
#
import base64
from io import BytesIO
from matplotlib.figure import Figure
#
import numpy as np
from scipy.stats import lognorm
import networkx as nx
import geopandas as gpd
import matplotlib.pylab as plt
import wntr


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

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
    
    report_entry = Report(latitude=request.form["latitude"],longitude=request.form["longitude"],radius=request.form["radius"],location=request.form["locationName"],origin=request.form["origin"],phone=request.form["phone"],description=request.form["description"])
    db.session.add(report_entry)
    db.session.commit()
    error = "گزارش ایجاد شد"
    flash(error)
    return redirect(url_for("dashboard"))

@app.route("/delete/report/<sid>", methods=['POST', 'GET'])
def delete_report(sid):
    """delete report from the database."""
    if not session.get("logged_in"):
        abort(401)
    print(sid)
    try:
        Report.query.filter_by(id=sid).delete()
        db.session.commit()
        error = "حذف شد"
        flash(error)
    except Exception as e:
        result = {"status": 0, "message": repr(e)}
        flash(result)
    return redirect(url_for("administrator"))

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("لطفا وارد شوید")
            # return jsonify({"status": 0, "message": "لطفا وارد شوید"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == "POST":
        if request.form["username"] != "admin":
            error = "نام کاربری نامعتبر"
        elif request.form["password"] != "admin":
            error = "رمز عبور نامعتبر"
        else:
            session["logged_in"] = True
            flash("شما وارد سیستم شدید")
            return redirect(url_for("administrator"))

    return render_template("login.html", title='ورود', error=error)

@app.route("/logout")
def logout():
    """User logout/authentication/session management."""
    session.pop("logged_in", None)
    flash("شما از سیستم خارج شدید")
    return redirect(url_for("dashboard"))

@app.route("/administrator", methods=["GET", "POST"])
@login_required
def administrator():
    """administrator"""
    if not session.get("logged_in"):
        abort(401)

    reports = Report.query.order_by(Report.id.asc()).all()
    return render_template("administrator.html" ,reports=reports , title='مدیریت سامانه')

#
def custom_wntr(wnt):

    wn = wntr.network.WaterNetworkModel(wnt)
    fname=str(wn.title[0])+".png"

    ''''''''
    adrs="ILD/static/images/plot_network/average_expected_demand/"
    fa=adrs+fname
    # Compute and plot average expected demand 
    AED = wntr.metrics.average_expected_demand(wn)
    wntr.graphics.plot_network(wn, node_attribute=AED, node_range=(0,0.025), title='Average expected demand (m$^3$/s)',filename=fa)
    ''''''''
    adrs="ILD/static/images/plot_network/large_pipe_diameters/"
    fa=adrs+fname
    # Return pipes diameters > 12 inches
    large_pipe_diameters = wn.query_link_attribute('diameter', np.greater, 12*0.0254)
    # Plot pipes diameters > 12 inches
    wntr.graphics.plot_network(wn, link_attribute=large_pipe_diameters, node_size=0, link_width=2, title="Pipes with diameter > 12 inches",filename=fa)
    ''''''''
    adrs="ILD/static/images/plot_network/pressure_at_5hr/"
    fa=adrs+fname
    # Simulate hydraulics using EPANET
    sim = wntr.sim.EpanetSimulator(wn)
    results_EPANET = sim.run_sim()
    # Plot pressure at hour 5 on the network
    pressure_at_5hr = results_EPANET.node['pressure'].loc[5*3600, :]
    wntr.graphics.plot_network(wn, node_attribute=pressure_at_5hr, node_size=30, title='Pressure at 5 hours',filename=fa)
    ''''''''
    adrs="ILD/static/images/plot_network/expected_demand/"
    fa=adrs+fname    # Run a pressure dependent hydraulic simulation
    wn.options.hydraulic.demand_model = 'PDD'
    wn.options.hydraulic.required_pressure = 50 # m, The required pressure is set to create a scenario where not all demands are met
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    # Compute water service availability, defined as the ratio of delivered demand to the expected demand. 
    expected_demand = wntr.metrics.expected_demand(wn)
    demand = results.node['demand'].loc[:,wn.junction_name_list]
    wsa = wntr.metrics.water_service_availability(expected_demand.sum(axis=0), demand.sum(axis=0))
    wntr.graphics.plot_network(wn, node_attribute=wsa, title='Water service availability',filename=fa)
    ''''''''
    adrs="ILD/static/images/plot_network/average_age/"
    fa=adrs+fname
    # Compute water age using the last 48 hours of a water quality simulation
    # Water age is the time water spends in the distribution system prior to use.
    wn.options.quality.parameter = 'AGE'
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    age = results.node['quality']
    age_last_48h = age.loc[age.index[-1]-48*3600:age.index[-1]]
    average_age = age_last_48h.mean()/3600 # convert to hours for the plot
    wntr.graphics.plot_network(wn, node_attribute=average_age, title="Average water age (hr)",filename=fa)
    ''''''''
    adrs="ILD/static/images/plot_network/pop_impacted/"
    fa=adrs+fname
    # Compute the population that is impacted by water age greater than 24 hours
    pop = wntr.metrics.population(wn)
    threshold = 24 # hours
    pop_impacted = wntr.metrics.population_impacted(pop, average_age, np.greater, threshold)
    wntr.graphics.plot_network(wn, node_attribute=pop_impacted, title="Population impacted by water age > 24 hours",filename=fa)
    ''''''''
    adrs="ILD/static/images/plot_network/plot_fragility_curve/"
    fa=adrs+fname
    #Fragility curves define the probability of exceeding a damage state as a function of environmental condition.  Fragility curves are commonly used in earthquake analysis, but can be defined for other scenarios.
    FC = wntr.scenario.FragilityCurve()
    FC.add_state('Minor', 1, {'Default': lognorm(0.5,scale=0.3)})
    FC.add_state('Major', 2, {'Default': lognorm(0.5,scale=0.7)})
    wntr.graphics.plot_fragility_curve(FC, xlabel='Peak Ground Acceleration (g)')
    plt.savefig(fa)
    ''''''''
    adrs="ILD/static/images/plot_network/link_segments/"
    fa=adrs+fname
    # Create a N-2 strategic valve layer.  Note that the user can create strategic or random valve placements, or use real valve data.
    valve_layer = wntr.network.generate_valve_layer(wn, 'strategic', 2)
    # Identify nodes and links that are in each valve segment
    G = wn.to_graph()
    node_segments, link_segments, seg_sizes = wntr.metrics.topographic.valve_segments(G, valve_layer)
    # Plot segments
    N = seg_sizes.shape[0] # number of segments
    cmap = wntr.graphics.random_colormap(N) # random color map helps visualize segments
    wntr.graphics.plot_network(wn, link_attribute=link_segments, node_size=0, link_width=2, link_range=[0,N],  link_cmap=cmap, title='Valve segment ID',filename=fa)

#

@app.route("/add/zone", methods=["POST"])
def add_zone():
    """Adds new zone to the database."""
    if not session.get("logged_in"):
        abort(401)

    file = request.files['file']
    filename = os.path.join(app.config['UPLOAD_FOLDER_ZONES'], file.filename)
    file.save(filename)

    custom_wntr(filename)

    error1 = "فایل با موفقیت بارگذاری شد"
    flash(error1)
    zone_entry = Zones(
        zone=request.form["zone"], file_address=file.filename)
    db.session.add(zone_entry)
    db.session.commit()
    error2 = "منطقه افزوده شد"
    flash(error2)
    return redirect(url_for("administrator"))

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

@app.route('/zones')
def zones():
    """Renders the zones page."""


    zones = Zones.query.order_by(Zones.id.asc()).all()
    return render_template(
        'zones.html',
        zones=zones,
        title='مناطق'
    )

@app.route("/zones/<sid>", methods=['POST', 'GET'])
def zone_view(sid):
    """zone view """

    zn = Zones.query.filter(Zones.id == sid).first()
    wn = wntr.network.WaterNetworkModel(os.path.join(app.config['UPLOAD_FOLDER_ZONES'], zn.file_address))
    fname=str(wn.title[0])

    return render_template(
        'zone_view.html',
        file_name=fname,
        title='مناطق'
    )


@app.route('/networks')
def networks():
    """Renders the networks page."""


    zones = Zones.query.order_by(Zones.id.asc()).all()
    return render_template(
        'networks.html',
        zones=zones,
        title='شبکه آبرسانی'
    )

@app.route("/networks/<sid>", methods=['POST', 'GET'])
def network_view(sid):
    """network view """

    zn = Zones.query.filter(Zones.id == sid).first()
    wn = wntr.network.WaterNetworkModel(os.path.join(app.config['UPLOAD_FOLDER_ZONES'], zn.file_address))
    fname=str(wn.title[0])

    return render_template(
        'network_view.html',
        file_name=fname,
        title='شبکه آبرسانی'
    )

