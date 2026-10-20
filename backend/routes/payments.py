"""Payment endpoints.

The frontend (admin/payment.js, admin/payment-history.js) has always called
`/add_payment` and `/get_payments`, but those routes only existed in the
unused MySQL prototype. They are implemented here on the existing Payment model
with the same request/response fields.
"""
from flask import Blueprint, jsonify
from sqlalchemy import func

from db import db
from models import Payment, User
from security import admin_required, clean_str, get_json

payments_bp = Blueprint('payments', __name__)

PAYMENT_METHODS = {"credit-card", "debit-card", "paypal", "bank-transfer", "cash", "upi"}


def _resolve_student(identifier):
    """Accept either a numeric student ID or the student's email."""
    identifier = clean_str(identifier, 100)
    if not identifier:
        return None
    if "@" in identifier:
        user = User.query.filter(func.lower(User.email) == identifier.lower()).first()
    elif identifier.isdigit():
        user = db.session.get(User, int(identifier))
    else:
        return None
    if user is None or user.is_admin:
        return None
    return user


@payments_bp.route('/add_payment', methods=['POST'])
@admin_required
def add_payment():
    data = get_json()
    method = clean_str(data.get('method'), 30).lower()
    try:
        amount = round(float(data.get('amount')), 2)
    except (TypeError, ValueError):
        amount = 0

    if not data.get('student_id') or amount <= 0 or not method:
        return jsonify({'error': 'Missing required fields', 'message': 'Missing required fields'}), 400
    if method not in PAYMENT_METHODS:
        return jsonify({'error': 'Invalid payment method', 'message': 'Invalid payment method'}), 400
    if amount > 10_000_000:
        return jsonify({'error': 'Amount is too large', 'message': 'Amount is too large'}), 400

    student = _resolve_student(data.get('student_id'))
    if student is None:
        return jsonify({'error': 'Student not found', 'message': 'Student not found'}), 404

    payment = Payment(user_id=student.id, amount=amount, method=method)
    db.session.add(payment)
    db.session.commit()
    return jsonify({'message': 'Payment recorded successfully', 'id': payment.id}), 201


@payments_bp.route('/get_payments', methods=['GET'])
@admin_required
def get_payments():
    rows = (
        db.session.query(Payment, User)
        .join(User, Payment.user_id == User.id)
        .order_by(Payment.created_at.desc(), Payment.id.desc())
        .all()
    )
    return jsonify([
        {
            'id': p.id,
            'student_id': p.user_id,
            'student_name': u.username,
            'amount': p.amount,
            'method': p.method,
            'date': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else None,
        }
        for p, u in rows
    ])
