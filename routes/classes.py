from flask import Blueprint, jsonify, request
from services.class_service import get_upcoming_classes

bp = Blueprint('classes', __name__)

@bp.route('/classes', methods=['GET'])
def get_classes():
    tz = request.args.get('tz', 'Asia/Kolkata')
    return jsonify(get_upcoming_classes(user_tz=tz)), 200