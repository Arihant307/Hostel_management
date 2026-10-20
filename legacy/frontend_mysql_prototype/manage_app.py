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

# # Route to get all courses
# @app.route('/get_courses', methods=['GET'])
# def get_courses():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM courses")
#     courses = cursor.fetchall()
#     return jsonify(courses)

# # Route to add a new course
# @app.route('/add_course', methods=['POST'])
# def add_course():
#     data = request.get_json()
#     name = data.get('name')
#     description = data.get('description')

#     if not name or not description:
#         return jsonify({'error': 'Missing required fields'}), 400

#     cursor = mysql.connection.cursor()
#     cursor.execute("INSERT INTO courses (name, description) VALUES (%s, %s)", (name, description))
#     mysql.connection.commit()
#     return jsonify({'message': 'Course added successfully'}), 201

# # Route to edit a course
# @app.route('/edit_course/<int:id>', methods=['PUT'])
# def edit_course(id):
#     data = request.get_json()
#     name = data.get('name')
#     description = data.get('description')

#     if not name or not description:
#         return jsonify({'error': 'Missing required fields'}), 400

#     cursor = mysql.connection.cursor()
#     cursor.execute("UPDATE courses SET name=%s, description=%s WHERE id=%s", (name, description, id))
#     mysql.connection.commit()
#     return jsonify({'message': 'Course updated successfully'}), 200

# # Route to delete a course
# @app.route('/delete_course/<int:id>', methods=['DELETE'])
# def delete_course(id):
#     cursor = mysql.connection.cursor()
#     cursor.execute("DELETE FROM courses WHERE id=%s", (id,))
#     mysql.connection.commit()
#     return jsonify({'message': 'Course deleted successfully'}), 200

# if __name__ == '__main__':
#     app.run(debug=True)
