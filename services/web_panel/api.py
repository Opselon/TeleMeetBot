from flask import Blueprint, jsonify, request
import database

web_panel_api = Blueprint('web_panel_api', __name__)

@web_panel_api.route('/config', methods=['GET'])
def get_config():
    key = request.args.get('key')
    if not key:
        return jsonify({"error": "Key is required"}), 400
    value = database.get_config(key)
    return jsonify({key: value})

@web_panel_api.route('/config', methods=['POST'])
def set_config():
    data = request.get_json()
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({"error": "Key and value are required"}), 400
    database.set_config(data['key'], data['value'])
    return jsonify({"message": "Config saved successfully"})
