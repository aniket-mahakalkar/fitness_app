from datetime import datetime, timedelta
from models.models import FitnessClass
from db import db
import pytz


def seed_data():

    if FitnessClass.query.count() == 0:
        classes = [
            FitnessClass(
                name="Yoga",
                datetime=datetime.now(pytz.timezone("Asia/Kolkata")) +  timedelta(days=1) ,
                instructor_name="Amit",
                capacity=10,
                available_slots=10
            ),
            FitnessClass(
                name="Zumba",
                datetime=datetime.now(pytz.timezone("Asia/Kolkata")) + timedelta(days=1) ,
                instructor_name="Priya",
                capacity=10,
                available_slots=10
            ),
            FitnessClass(
                name="HIIT",
                datetime=datetime.now(pytz.timezone("Asia/Kolkata")) + timedelta(days=1) ,
                instructor_name="John",
                capacity=10,
                available_slots=10
            ),
        ]

        db.session.add_all(classes)
        db.session.commit()
        print("Seeded fitness classes.")
    else:
        print("Classes already exist.")