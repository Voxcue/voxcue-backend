from flask import Blueprint, request, jsonify
from app.auth.auth import token_required
from app.tasks import update_todo_list_task

todo = Blueprint("todo", __name__)


@todo.route("/todo", methods=["POST"])
@token_required
def update_todo_list(current_user):
    user_id = current_user.id
    date = request.get_json.get('date')
    update_todo_list_task.delay(user_id,date)
    return jsonify({"message": "Todo list update initiated"}), 200
