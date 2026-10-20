from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend access

# Simulated database
users_db = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email in users_db:
        return jsonify({"success": False, "message": "Email already registered."}), 400

    users_db[email] = password
    return jsonify({"success": True, "message": "Registration successful!"})

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/get_student_reports', methods=['GET'])
def get_student_reports():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT users.fullname AS name, users.email, rooms.room_number, 
            CASE WHEN payments.student_id IS NOT NULL THEN 1 ELSE 0 END AS payment_status
        FROM users 
        LEFT JOIN rooms ON users.room = rooms.id
        LEFT JOIN payments ON users.id = payments.student_id
    """)
    students = cursor.fetchall()
    return jsonify(students)

@app.route('/get_room_occupancy', methods=['GET'])
def get_room_occupancy():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT type, COUNT(*) as occupancy_count 
        FROM rooms WHERE occupied > 0 GROUP BY type
    """)
    occupancy_data = cursor.fetchall()

    room_types = [entry["type"] for entry in occupancy_data]
    occupancy_counts = [entry["occupancy_count"] for entry in occupancy_data]

    return jsonify({"room_types": room_types, "occupancy_counts": occupancy_counts})

@app.route('/add_payment', methods=['POST'])
def add_payment():
    data = request.get_json()
    student_id = data.get('student_id')
    amount = data.get('amount')
    method = data.get('method')

    if not student_id or not amount or not method:
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO payments (student_id, amount, method, date) VALUES (%s, %s, %s, NOW())",
                    (student_id, amount, method))
    mysql.connection.commit()
    return jsonify({'message': 'Payment recorded successfully'}), 201

@app.route('/get_payments', methods=['GET'])
def get_payments():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM payments ORDER BY date DESC")
    payments = cursor.fetchall()
    return jsonify(payments)


from flask_mail import Mail, Message
import random

# Configure Flask-Mail for sending OTPs
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Replace with your email password
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

otp_storage = {}  # Store OTPs temporarily

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')

    otp = random.randint(100000, 999999)  # Generate 6-digit OTP
    otp_storage[email] = otp

    msg = Message('Your Login OTP', sender='your-email@gmail.com', recipients=[email])
    msg.body = f'Your OTP for login is: {otp}'
    mail.send(msg)

    return jsonify({'message': 'OTP sent successfully'}), 200

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = int(data.get('otp'))

    if otp_storage.get(email) == otp:
        del otp_storage[email]  # Remove OTP after use
        return jsonify({'message': 'OTP verified successfully'}), 200
    else:
        return jsonify({'error': 'Invalid OTP'}), 400



from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Change if needed
app.config['MYSQL_PASSWORD'] = ''  # Change if needed
app.config['MYSQL_DB'] = 'hostel_management'

mysql = MySQL(app)

# Route to get all rooms
@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    return jsonify(rooms)

# Route to add a new room
@app.route('/add_room', methods=['POST'])
def add_room():
    data = request.get_json()
    room_number = data.get('room_number')
    room_type = data.get('type')
    capacity = data.get('capacity')

    if not room_number or not room_type or not capacity:
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO rooms (room_number, type, capacity, occupied) VALUES (%s, %s, %s, %s)",
                (room_number, room_type, capacity, 0))
    mysql.connection.commit()
    return jsonify({'message': 'Room added successfully'}), 201

# Route to edit a room
@app.route('/edit_room/<int:id>', methods=['PUT'])
def edit_room(id):
    data = request.get_json()
    room_type = data.get('type')
    capacity = data.get('capacity')

    if not room_type or not capacity:
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE rooms SET type=%s, capacity=%s WHERE id=%s", (room_type, capacity, id))
    mysql.connection.commit()
    return jsonify({'message': 'Room updated successfully'}), 200

# Route to delete a room
@app.route('/delete_room/<int:id>', methods=['DELETE'])
def delete_room(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM rooms WHERE id=%s", (id,))
    mysql.connection.commit()
    return jsonify({'message': 'Room deleted successfully'}), 200

# Route to assign a room to a student
@app.route('/assign_room/<int:room_id>', methods=['POST'])
def assign_room(room_id):
    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'Missing student ID'}), 400

    cursor = mysql.connection.cursor()

    # Check if the room is already full
    cursor.execute("SELECT occupied, capacity FROM rooms WHERE id=%s", (room_id,))
    room = cursor.fetchone()

    if room and room[0] >= room[1]:  # occupied >= capacity
        return jsonify({'error': 'Room is full'}), 400

    # Assign the room
    cursor.execute("UPDATE users SET room=%s WHERE id=%s", (room_id, student_id))
    cursor.execute("UPDATE rooms SET occupied = occupied + 1 WHERE id=%s", (room_id,))
    mysql.connection.commit()

    return jsonify({'message': 'Room assigned successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Change if needed
app.config['MYSQL_PASSWORD'] = ''  # Change if needed
app.config['MYSQL_DB'] = 'hostel_management'

mysql = MySQL(app)

# Route to get all courses
@app.route('/get_courses', methods=['GET'])
def get_courses():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    return jsonify(courses)

# Route to add a new course
@app.route('/add_course', methods=['POST'])
def add_course():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name or not description:
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO courses (name, description) VALUES (%s, %s)", (name, description))
    mysql.connection.commit()
    return jsonify({'message': 'Course added successfully'}), 201

# Route to edit a course
@app.route('/edit_course/<int:id>', methods=['PUT'])
def edit_course(id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name or not description:
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE courses SET name=%s, description=%s WHERE id=%s", (name, description, id))
    mysql.connection.commit()
    return jsonify({'message': 'Course updated successfully'}), 200

# Route to delete a course
@app.route('/delete_course/<int:id>', methods=['DELETE'])
def delete_course(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM courses WHERE id=%s", (id,))
    mysql.connection.commit()
    return jsonify({'message': 'Course deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session key

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hostel_management'

mysql = MySQL(app)

# Route to log in users
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()

    if user:
        session['loggedin'] = True
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = 'admin' if user['is_admin'] else 'student'  # Store role

        return jsonify({'message': 'Login successful', 'role': session['role']}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Route to log out users
@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

# Middleware to check if the user is an admin
def admin_required(f):
    def wrapper(*args, **kwargs):
        if 'loggedin' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized access'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Protecting the Admin Panel Route
@app.route('/admin-panel')
@admin_required
def admin_panel():
    return jsonify({'message': 'Welcome to Admin Panel'}), 200
