import secrets

from flask import Blueprint, jsonify, request, session
from sqlalchemy import func

from db import db
from models import Payment, User
from security import (
    MIN_PASSWORD_LENGTH,
    admin_required,
    clean_str,
    current_user,
    get_json,
    login_required,
    login_user,
    valid_email,
)

auth_bp = Blueprint('auth', __name__)


def _find_by_email(email):
    return User.query.filter(func.lower(User.email) == email.lower()).first()


def _student_or_404(student_id):
    user = db.session.get(User, student_id)
    if user is None or user.is_admin:
        return None
    return user


@auth_bp.route('/register', methods=['POST'])
def register():
    data = get_json()
    fullname = clean_str(data.get('fullname'), 80)
    email = clean_str(data.get('email'), 100).lower()
    password = data.get('password') or ''

    if not fullname or not email or not password:
        return jsonify({"message": "Full name, email and password are required."}), 400
    if not valid_email(email):
        return jsonify({"message": "Please enter a valid email address."}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"message": f"Password must be at least {MIN_PASSWORD_LENGTH} characters."}), 400
    if _find_by_email(email):
        return jsonify({"message": "Email already exists"}), 400

    # Public registration always creates a student account.
    new_user = User(username=fullname, email=email, role="student")
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = get_json()
    email = clean_str(data.get('email'), 100)
    password = data.get('password') or ''
    # Optional: the portal the user is logging in through ("admin" or "student").
    expected_role = clean_str(data.get('role'), 20).lower()

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    user = _find_by_email(email)
    if user is None or not user.check_password(password):
        return jsonify({"message": "Invalid email or password."}), 401

    if expected_role == "admin" and not user.is_admin:
        return jsonify({"message": "This account does not have admin access."}), 403

    db.session.commit()  # persists a legacy-password upgrade, if one happened
    login_user(user)
    return jsonify({
        "message": "Login successful!",
        "role": user.role,
        "name": user.username,
        "email": user.email,
    }), 200


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    user = current_user()
    return jsonify({"id": user.id, "name": user.username, "email": user.email, "role": user.role})


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    user = current_user()
    # The profile is always the logged-in user's. An admin may look up another
    # user with ?email=; a student may only read their own profile.
    email = clean_str(request.args.get('email'), 100)
    if email and email.lower() != user.email.lower():
        if not user.is_admin:
            return jsonify({'error': 'You can only view your own profile'}), 403
        user = _find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'fullname': user.username,
        'email': user.email
    })


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = current_user()
    data = get_json()
    fullname = clean_str(data.get('fullname'), 80)
    email = clean_str(data.get('email'), 100)
    if not fullname:
        return jsonify({'error': 'Full name is required'}), 400
    if email and email.lower() != user.email.lower():
        return jsonify({'error': 'You can only update your own profile'}), 403
    user.username = fullname
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})


# --- Admin Student Management Endpoints ---
@auth_bp.route('/students', methods=['GET'])
@admin_required
def get_students():
    users = User.query.filter(User.role != "admin").order_by(User.id).all()
    students = []
    for user in users:
        students.append({
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'phone': user.phone,
            'room': user.room_preference,
        })
    return jsonify(students)


@auth_bp.route('/students', methods=['POST'])
@admin_required
def add_student():
    data = get_json()
    name = clean_str(data.get('name'), 80)
    email = clean_str(data.get('email'), 100).lower()
    phone = clean_str(data.get('phone'), 20) or None
    room = clean_str(data.get('room'), 20) or None
    password = data.get('password') or ''
    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400
    if not valid_email(email):
        return jsonify({'error': 'Please enter a valid email address'}), 400
    if _find_by_email(email):
        return jsonify({'error': 'Email already exists'}), 400

    temporary_password = None
    if not password:
        # No insecure shared default password: generate a one-off password and
        # show it to the admin once so it can be passed to the student.
        temporary_password = secrets.token_urlsafe(9)
        password = temporary_password
    elif len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({'error': f'Password must be at least {MIN_PASSWORD_LENGTH} characters'}), 400

    new_user = User(username=name, email=email, phone=phone, room_preference=room, role="student")
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    body = {'message': 'Student added successfully', 'id': new_user.id}
    if temporary_password:
        body['temporary_password'] = temporary_password
    return jsonify(body), 201


@auth_bp.route('/students/<int:id>', methods=['PUT'])
@admin_required
def edit_student(id):
    data = get_json()
    user = _student_or_404(id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404

    if 'email' in data:
        email = clean_str(data.get('email'), 100).lower()
        if not valid_email(email):
            return jsonify({'error': 'Please enter a valid email address'}), 400
        other = _find_by_email(email)
        if other and other.id != user.id:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = email
    if 'name' in data:
        name = clean_str(data.get('name'), 80)
        if not name:
            return jsonify({'error': 'Name cannot be empty'}), 400
        user.username = name
    if 'phone' in data:
        user.phone = clean_str(data.get('phone'), 20) or None
    if 'room' in data:
        user.room_preference = clean_str(data.get('room'), 20) or None
    db.session.commit()
    return jsonify({'message': 'Student updated successfully'})


@auth_bp.route('/students/<int:id>', methods=['DELETE'])
@admin_required
def delete_student(id):
    user = _student_or_404(id)
    if not user:
        return jsonify({'error': 'Student not found'}), 404
    # Remove dependent payments first so the foreign key is not violated.
    Payment.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})


@auth_bp.route('/get_student_reports', methods=['GET'])
@admin_required
def get_student_reports():
    users = User.query.filter(User.role != "admin").order_by(User.id).all()
    paid_ids = {row[0] for row in db.session.query(Payment.user_id).distinct()}
    reports = []
    for user in users:
        reports.append({
            'name': user.username,
            'email': user.email,
            'room_number': user.room_preference,
            'payment_status': user.id in paid_ids
        })
    return jsonify(reports)
