from db import db
from datetime import datetime
from zoneinfo import ZoneInfo


class Customer(db.Model):

    __tablename__ = 'customer'

    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique =True, nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    bookings = db.relationship('Booking', backref='customer', lazy = True)


class FitnessClass(db.Model):

    __tablename__ = 'fitness_class'

    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(100), nullable= False)
    datetime = db.Column(db.DateTime, nullable= False)
    instructor_name  = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable = False)
    available_slots = db.Column(db.Integer, nullable=False)
    is_cancelled = db.Column(db.Boolean, default = False)
    bookings = db.relationship('Booking', backref='fitness_class', lazy=True)

class Booking(db.Model):

    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key = True)
    class_id = db.Column(db.Integer, db.ForeignKey('fitness_class.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable = False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)

