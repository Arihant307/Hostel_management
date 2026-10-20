from flask import Blueprint, jsonify
from sqlalchemy import func

from db import db
from models import Payment, Room, User
from security import admin_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/', methods=['GET'])
def dashboard_home():
    return jsonify({"message": "Welcome to the Dashboard!"})


@dashboard_bp.route('/stats', methods=['GET'])
@admin_required
def dashboard_stats():
    """Real numbers for the admin dashboard overview card."""
    total_students = User.query.filter(User.role != "admin").count()
    rooms = Room.query.all()
    occupancy = dict(
        db.session.query(User.room_preference, func.count(User.id))
        .filter(User.role != "admin", User.room_preference.isnot(None))
        .group_by(User.room_preference)
        .all()
    )
    total_capacity = sum(r.capacity for r in rooms)
    occupied_beds = sum(min(occupancy.get(r.number, 0), r.capacity) for r in rooms)
    available_rooms = sum(1 for r in rooms if occupancy.get(r.number, 0) < r.capacity)
    total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0

    return jsonify({
        "total_students": total_students,
        "total_rooms": len(rooms),
        "available_rooms": available_rooms,
        "total_capacity": total_capacity,
        "occupied_beds": occupied_beds,
        "occupancy_rate": round(occupied_beds * 100 / total_capacity) if total_capacity else 0,
        "total_revenue": float(total_revenue),
    })
