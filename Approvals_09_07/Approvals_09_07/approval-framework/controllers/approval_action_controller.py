# from flask import Blueprint, request, jsonify, current_app
# from bson.objectid import ObjectId

# approval_action_bp = Blueprint('approval_action_bp', __name__)

# @approval_action_bp.route('/approval-actions', methods=['POST'])
# def create_approval_action():
#     data = request.json
#     approval_actions = current_app.mongo.db.approval_actions
#     approval_actions.insert_one(data)
#     return jsonify({"message": "Approval action created successfully"}), 201

# @approval_action_bp.route('/approval-actions/<id>', methods=['GET'])
# def get_approval_action(id):
#     approval_actions = current_app.mongo.db.approval_actions
#     approval_action = approval_actions.find_one({"_id": ObjectId(id)})
#     return jsonify(approval_action), 200
