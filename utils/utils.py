import pytz
from models.models import FitnessClass

def utc_to_local(utc_dt, timezone='Asia/Kolkata'):

    try:

        local_tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:

        local_tz = pytz.timezone("Asia/Kolkata")
    
    return utc_dt.replace(tzinfo = pytz.utc).astimezone(local_tz)


def validate_booking_request(data):

    required_fields = ['class_id', 'customer_name', 'customer_email']

    for field in required_fields:

        if field not in data or not data[field]:

            return False, f'Missing field: {field}'
        
    return True, 'Valid'


def get_available_classes():
    classes = FitnessClass.query.all()
    results = []
    for fc in classes:
        available_slots = fc.capacity - fc.bookings.count()
        if available_slots > 0:
            results.append({
                "name": fc.name,
                "available_slots": available_slots,
                "datetime": fc.date_time,
                "instructor_name": fc.instructor_name
            })
    return results