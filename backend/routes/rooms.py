from flask import Blueprint, jsonify
from sqlalchemy import func

from db import db
from models import Room, User
from security import admin_required, clean_str, get_json, login_required

room_bp = Blueprint('rooms', __name__)

ROOM_TYPES = {"single", "double", "shared"}


def _occupancy_by_room_number():
    """Number of students assigned to each room number."""
    rows = (
        db.session.query(User.room_preference, func.count(User.id))
        .filter(User.role != "admin", User.room_preference.isnot(None))
        .group_by(User.room_preference)
        .all()
    )
    return {number: count for number, count in rows}


@room_bp.route('/', methods=['GET'])
@login_required
def get_rooms():
    rooms = Room.query.order_by(Room.id).all()
    occupancy = _occupancy_by_room_number()
    room_list = [
        {
            'id': room.id,
            'number': room.number,
            'capacity': room.capacity,
            'type': room.room_type,
            'occupied': occupancy.get(room.number, 0),
        } for room in rooms
    ]
    return jsonify(room_list)


@room_bp.route('/add', methods=['POST'])
@admin_required
def add_room():
    data = get_json()
    number = clean_str(data.get('number'), 10)
    room_type = clean_str(data.get('type'), 20).lower() or None

    try:
        capacity = int(data.get('capacity'))
    except (TypeError, ValueError):
        capacity = 0

    if not number or capacity < 1:
        return jsonify({'error': 'Room number and a capacity of at least 1 are required',
                        'message': 'Room number and a capacity of at least 1 are required'}), 400
    if capacity > 50:
        return jsonify({'error': 'Capacity cannot exceed 50', 'message': 'Capacity cannot exceed 50'}), 400
    if room_type and room_type not in ROOM_TYPES:
        return jsonify({'error': 'Invalid room type', 'message': 'Invalid room type'}), 400
    if Room.query.filter_by(number=number).first():
        return jsonify({'error': 'A room with this number already exists',
                        'message': 'A room with this number already exists'}), 400

    new_room = Room(number=number, capacity=capacity, room_type=room_type)
    db.session.add(new_room)
    db.session.commit()
    return jsonify({'message': 'Room added successfully', 'id': new_room.id}), 201


@room_bp.route('/get_room_occupancy', methods=['GET'])
@admin_required
def get_room_occupancy():
    rooms = Room.query.order_by(Room.id).all()
    occupancy = _occupancy_by_room_number()
    return jsonify({
        'room_types': [room.number for room in rooms],
        'occupancy_counts': [occupancy.get(room.number, 0) for room in rooms]
    })
