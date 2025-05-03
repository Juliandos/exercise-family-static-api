import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

jackson_family = FamilyStructure("Jackson")

# Añadir miembros iniciales
initial_members = [
    {"first_name": "John", "age": 33, "lucky_numbers": [7, 13, 22]},
    {"first_name": "Jane", "age": 35, "lucky_numbers": [10, 14, 3]},
    {"first_name": "Jimmy", "age": 5, "lucky_numbers": [1]}
]

for member in initial_members:
    jackson_family.add_member(member)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def get_members():
    members = jackson_family.get_all_members()
    return jsonify(members), 200

@app.route('/members/<int:member_id>', methods=['GET'])
def get_single_member(member_id):
    member = jackson_family.get_member(member_id)
    if member:
        return jsonify({
            "id": member["id"],
            "first_name": member["first_name"],
            "age": member["age"],
            "lucky_numbers": member["lucky_numbers"]
        }), 200
    return jsonify({"error": "Member not found"}), 400

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    required_fields = ['first_name', 'age', 'lucky_numbers']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        age = int(data['age'])
        if age <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Age must be a positive integer"}), 400

    if not isinstance(data['lucky_numbers'], list) or not all(isinstance(num, int) for num in data['lucky_numbers']):
        return jsonify({"error": "lucky_numbers must be a list of integers"}), 400

    member = {
        "first_name": data['first_name'],
        "age": age,
        "lucky_numbers": data['lucky_numbers']
    }
    if 'id' in data:
        if not isinstance(data['id'], int):
            return jsonify({"error": "id must be an integer"}), 400
        member['id'] = data['id']

    jackson_family.add_member(member)
    return jsonify({}), 200

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    if jackson_family.delete_member(member_id):
        return jsonify({"done": True}), 200
    return jsonify({"error": "Member not found"}), 400

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)