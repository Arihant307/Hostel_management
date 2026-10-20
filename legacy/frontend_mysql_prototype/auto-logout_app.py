# from flask import Flask, request, jsonify, session, redirect, url_for
# from flask_mysqldb import MySQL
# import MySQLdb.cursors
# import os

# app = Flask(__name__)
# app.secret_key = os.urandom(24)  # Secure session key

# # MySQL Configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'hostel_management'

# mysql = MySQL(app)

# # Route to log in users
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')

#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
#     user = cursor.fetchone()

#     if user:
#         session['loggedin'] = True
#         session['user_id'] = user['id']
#         session['email'] = user['email']
#         session['role'] = 'admin' if user['is_admin'] else 'student'  # Store role

#         return jsonify({'message': 'Login successful', 'role': session['role']}), 200
#     else:
#         return jsonify({'error': 'Invalid credentials'}), 401

# # Route to log out users
# @app.route('/logout')
# def logout():
#     session.clear()
#     return jsonify({'message': 'Logged out successfully'}), 200

# # Middleware to check if the user is an admin
# def admin_required(f):
#     def wrapper(*args, **kwargs):
#         if 'loggedin' not in session or session.get('role') != 'admin':
#             return jsonify({'error': 'Unauthorized access'}), 403
#         return f(*args, **kwargs)
#     wrapper.__name__ = f.__name__
#     return wrapper

# # Protecting the Admin Panel Route
# @app.route('/admin-panel')
# @admin_required
# def admin_panel():
#     return jsonify({'message': 'Welcome to Admin Panel'}), 200
