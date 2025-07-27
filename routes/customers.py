from flask import Blueprint, jsonify, request
from services.customer_service import get_all_customers

bp = Blueprint('customers', __name__)

@bp.route('/customers', methods=['GET'])
def list_clients():

    all_customers = get_all_customers()

    if all_customers is None:

        return jsonify('Failed to fetch all customers') , 500
    if not  all_customers:
        return jsonify('No Customers found') , 200
    return jsonify(get_all_customers()), 200