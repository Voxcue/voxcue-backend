from flask import jsonify

def handle_error(error):
    response = {
        "message": str(error),
        "type": "Error"
    }
    return jsonify(response), 500


def register_error_handlers(app):
    app.register_error_handler(Exception, handle_error)
