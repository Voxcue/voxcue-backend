from flask import jsonify, request
from . import api_bp


@api_bp.route('/hello', methods=['GET'])
def get_items():
    return jsonify("hello")

