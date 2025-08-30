import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wellatlas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sites = relationship("Site", backref="customer", cascade="all, delete-orphan")

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    jobs = relationship("Job", backref="site", cascade="all, delete-orphan")

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))

# Seed demo data
def seed_data():
    if Customer.query.first():
        return
    import random
    presidents = ["Washington", "Jefferson", "Lincoln", "Roosevelt", "Kennedy"]
    categories = ["Domestic", "Ag", "Drilling", "Electrical"]
    coords = [
        (39.927, -122.175), # Orland
        (39.406, -122.194), # Willows
        (39.728, -121.837), # Chico
        (39.928, -122.190), # Corning
        (39.725, -121.802)  # Durham
    ]
    for p in presidents:
        cust = Customer(name=p)
        db.session.add(cust)
        for i in range(5):
            lat, lng = random.choice(coords)
            site = Site(name=f"{p} Site {i+1}", latitude=lat, longitude=lng, customer=cust)
            db.session.add(site)
            for c in categories:
                job = Job(name=f"{c} Job", category=c, site=site)
                db.session.add(job)
    db.session.commit()

@app.before_request
def init_db():
    db.create_all()
    seed_data()

# Routes
@app.route("/")
def index():
    sites = Site.query.all()
    return render_template("index.html", sites=sites)

@app.route("/customers")
def list_customers():
    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)

@app.route("/sites/<int:site_id>")
def view_site(site_id):
    site = Site.query.get_or_404(site_id)
    return render_template("sites.html", site=site)

@app.route("/jobs/<int:job_id>")
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template("jobs.html", job=job)

# Nearby sites API
@app.route("/nearby", methods=["POST"])
def nearby():
    data = request.get_json()
    lat, lng = data.get("lat"), data.get("lng")
    results = []
    for site in Site.query.all():
        d = haversine(lat, lng, site.latitude, site.longitude)
        if d <= 50:  # 50 km radius
            results.append({
                "id": site.id,
                "name": site.name,
                "lat": site.latitude,
                "lng": site.longitude,
                "customer": site.customer.name
            })
    return jsonify(results)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
