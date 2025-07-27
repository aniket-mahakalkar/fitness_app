from datetime import datetime

from models.models import FitnessClass
from utils.utils import utc_to_local


def get_upcoming_classes(user_tz='Asia/Kolkata'):



    classes = FitnessClass.query.filter(FitnessClass.datetime > datetime.now(), ~FitnessClass.is_cancelled).all()
    all_classes = []

    for cls in classes:

        all_classes.append({
            'id': cls.id,
            'name': cls.name,
            'datetime': utc_to_local(cls.datetime, user_tz).strftime("%Y-%m-%d %H:%M"),
            'instructor': cls.instructor_name,
            'available_slots': cls.available_slots
        })

    return all_classes