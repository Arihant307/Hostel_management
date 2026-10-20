# from flask import Flask, request, jsonify
# from flask_mysqldb import MySQL
# import MySQLdb.cursors

# app = Flask(__name__)

# # MySQL Configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'  # Change if needed
# app.config['MYSQL_PASSWORD'] = ''  # Change if needed
# app.config['MYSQL_DB'] = 'hostel_management'

# mysql = MySQL(app)

# # Route to get all rooms
# @app.route('/get_rooms', methods=['GET'])
# def get_rooms():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM rooms")
#     rooms = cursor.fetchall()
#     return jsonify(rooms)

# # Route to add a new room
# @app.route('/add_room', methods=['POST'])
# def add_room():
#     data = request.get_json()
#     room_number = data.get('room_number')
#     room_type = data.get('type')
#     capacity = data.get('capacity')

#     if not room_number or not room_type or not capacity:
#         return jsonify({'error': 'Missing required fields'}), 400

#     cursor = mysql.connection.cursor()
#     cursor.execute("INSERT INTO rooms (room_number, type, capacity, occupied) VALUES (%s, %s, %s, %s)",
#                    (room_number, room_type, capacity, 0))
#     mysql.connection.commit()
#     return jsonify({'message': 'Room added successfully'}), 201

# # Route to edit a room
# @app.route('/edit_room/<int:id>', methods=['PUT'])
# def edit_room(id):
#     data = request.get_json()
#     room_type = data.get('type')
#     capacity = data.get('capacity')

#     if not room_type or not capacity:
#         return jsonify({'error': 'Missing required fields'}), 400

#     cursor = mysql.connection.cursor()
#     cursor.execute("UPDATE rooms SET type=%s, capacity=%s WHERE id=%s", (room_type, capacity, id))
#     mysql.connection.commit()
#     return jsonify({'message': 'Room updated successfully'}), 200

# # Route to delete a room
# @app.route('/delete_room/<int:id>', methods=['DELETE'])
# def delete_room(id):
#     cursor = mysql.connection.cursor()
#     cursor.execute("DELETE FROM rooms WHERE id=%s", (id,))
#     mysql.connection.commit()
#     return jsonify({'message': 'Room deleted successfully'}), 200

# # Route to assign a room to a student
# @app.route('/assign_room/<int:room_id>', methods=['POST'])
# def assign_room(room_id):
#     data = request.get_json()
#     student_id = data.get('student_id')

#     if not student_id:
#         return jsonify({'error': 'Missing student ID'}), 400

#     cursor = mysql.connection.cursor()

#     # Check if the room is already full
#     cursor.execute("SELECT occupied, capacity FROM rooms WHERE id=%s", (room_id,))
#     room = cursor.fetchone()

#     if room and room[0] >= room[1]:  # occupied >= capacity
#         return jsonify({'error': 'Room is full'}), 400

#     # Assign the room
#     cursor.execute("UPDATE users SET room=%s WHERE id=%s", (room_id, student_id))
#     cursor.execute("UPDATE rooms SET occupied = occupied + 1 WHERE id=%s", (room_id,))
#     mysql.connection.commit()

#     return jsonify({'message': 'Room assigned successfully'}), 200

# if __name__ == '__main__':
#     app.run(debug=True)
