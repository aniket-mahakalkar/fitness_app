from models.models import FitnessClass, Booking, Customer
from utils.utils import  validate_booking_request
from db import db


def book_class(data):

    is_valid , message = validate_booking_request(data)

    if not is_valid:

        return None, message

    class_id = data['class_id']
    customer_name = data['customer_name']
    customer_email = data['customer_email']


    try:

        fitness_class = FitnessClass.query.get(class_id)
        if not fitness_class:
            return None, "Class not found"

        if fitness_class.available_slots <= 0:
            return None, "Slots not available"


        customer = Customer.query.filter_by(email=customer_email).first()
        if not customer:
            customer = Customer(name = customer_name, email = customer_email)
            db.session.add(customer)
            db.session.commit()

        existing_booking = Booking.query.filter_by(
            class_id = class_id,
            customer_id = customer.id,

        ).first()

        if existing_booking:

            return  None, "You have already booked this booking"

        booking = Booking(class_id = class_id,customer_id = customer.id)
        db.session.add(booking)
        fitness_class.available_slots -= 1
        db.session.commit()

        return booking, None

    except Exception as e:
        db.session.rollback()
        print('Error:', e)
        return None, e

def cancel_booking(email, class_id):
    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        return None, "Customer not found"

    booking = Booking.query.filter_by(customer_id=customer.id, class_id=class_id).first()
    if not booking:
        return None, "No booking found for this customer and class"

    fitness_class = FitnessClass.query.get(class_id)
    if not fitness_class:
        return None, "Associated class not found"

    db.session.delete(booking)
    if not fitness_class.is_cancelled:
        fitness_class.available_slots += 1
    db.session.commit()

    return booking, None


def get_bookings_by_email(email):
    if not email:
        return None, "Email is required"

    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        return None, "Customer not found"

    bookings = Booking.query.filter_by(customer_id=customer.id).all()
    if not bookings:
        return None, "No bookings found for this customer"
    booking_list = []
    for b in bookings:
        if not b.fitness_class:
            continue

        booking_list.append({
            'class_name': b.fitness_class.name,
            'instructor': b.fitness_class.instructor_name,
            'class_time': b.fitness_class.datetime.strftime("%Y-%m-%d %H:%M"),
            'booking_time': b.booking_time.strftime("%Y-%m-%d %H:%M")
        })

    return booking_list, None