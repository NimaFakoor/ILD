from datetime import datetime, date
from email.mime import image
from ILD import db,app

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(100), nullable=True)
    longitude = db.Column(db.String(100), nullable=True)
    origin = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logdate = db.Column(db.DateTime, nullable=False, default=datetime.now())

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# ChangeLog *sequence-based* #major.minor[.build[.revision]] :> versioning

class Version(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    major = db.Column(db.Integer, nullable=True)
    minor = db.Column(db.Integer, nullable=True)
    build = db.Column(db.Integer, nullable=True)
    revision = db.Column(db.Integer, nullable=False)
    identifiers = db.Column(db.String(50), nullable=True)  # version
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# create the database and the db table
app.app_context().push()
db.create_all()

# commit the changes
db.session.commit()
