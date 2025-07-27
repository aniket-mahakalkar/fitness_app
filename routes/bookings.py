from flask import Blueprint, request, jsonify
from utils.utils import validate_booking_request
from services.booking_service import book_class, get_bookings_by_email,cancel_booking
import logging

bp = Blueprint('bookings', __name__)

@bp.route('/book', methods=['POST'])
def book():
    data = request.get_json()
    is_valid, msg = validate_booking_request(data)
    if not is_valid:
        return jsonify( msg), 400

    booking, error = book_class(data)
    if error:
        return jsonify(error), 400

    logging.info(f"Booked class {data['class_id']} for {data['customer_email']}")
    return jsonify('Booking successful'), 201

@bp.route('/cancel-booking', methods=['DELETE'])
def cancel_booking_route():
    data = request.get_json()
    customer_email = data.get("customer_email")
    class_id = data.get("class_id")

    if not customer_email or not class_id:
        return jsonify("Missing customer_email or class_id"), 400

    try:
        booking, error = cancel_booking(customer_email, class_id)
        if error:
            return jsonify(error), 404
        return jsonify(f"Booking for {customer_email} in class {class_id} cancelled successfully."), 200
    except Exception as e:
        return jsonify(str(e)), 500

@bp.route('/bookings', methods=['GET'])
def bookings():
    email = request.args.get('email')
    if not email:
        return jsonify('Email is required'), 400

    results, error = get_bookings_by_email(email)
    if error:
        return jsonify(error), 404

    return jsonify(results), 200