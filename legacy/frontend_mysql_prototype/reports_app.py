# @app.route('/get_student_reports', methods=['GET'])
# def get_student_reports():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("""
#         SELECT users.fullname AS name, users.email, rooms.room_number, 
#             CASE WHEN payments.student_id IS NOT NULL THEN 1 ELSE 0 END AS payment_status
#         FROM users 
#         LEFT JOIN rooms ON users.room = rooms.id
#         LEFT JOIN payments ON users.id = payments.student_id
#     """)
#     students = cursor.fetchall()
#     return jsonify(students)

# @app.route('/get_room_occupancy', methods=['GET'])
# def get_room_occupancy():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("""
#         SELECT type, COUNT(*) as occupancy_count 
#         FROM rooms WHERE occupied > 0 GROUP BY type
#     """)
#     occupancy_data = cursor.fetchall()

#     room_types = [entry["type"] for entry in occupancy_data]
#     occupancy_counts = [entry["occupancy_count"] for entry in occupancy_data]

#     return jsonify({"room_types": room_types, "occupancy_counts": occupancy_counts})
