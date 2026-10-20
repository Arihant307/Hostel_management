"""Course endpoints used by admin/manage-courses.js.

Like the payment routes, these were only defined in the unused MySQL
prototype. They are implemented here on the existing Course model, keeping the
URLs and JSON fields the page already uses.
"""
from flask import Blueprint, jsonify

from db import db
from models import Course
from security import admin_required, clean_str, get_json

courses_bp = Blueprint('courses', __name__)


def _validated(data):
    name = clean_str(data.get('name'), 100)
    description = clean_str(data.get('description'), 1000)
    if not name or not description:
        return None, None
    return name, description


@courses_bp.route('/get_courses', methods=['GET'])
@admin_required
def get_courses():
    courses = Course.query.order_by(Course.id).all()
    return jsonify([
        {'id': c.id, 'name': c.name, 'description': c.description or ''} for c in courses
    ])


@courses_bp.route('/add_course', methods=['POST'])
@admin_required
def add_course():
    name, description = _validated(get_json())
    if not name:
        return jsonify({'error': 'Missing required fields', 'message': 'Missing required fields'}), 400
    course = Course(name=name, description=description)
    db.session.add(course)
    db.session.commit()
    return jsonify({'message': 'Course added successfully', 'id': course.id}), 201


@courses_bp.route('/edit_course/<int:id>', methods=['PUT'])
@admin_required
def edit_course(id):
    course = db.session.get(Course, id)
    if course is None:
        return jsonify({'error': 'Course not found', 'message': 'Course not found'}), 404
    name, description = _validated(get_json())
    if not name:
        return jsonify({'error': 'Missing required fields', 'message': 'Missing required fields'}), 400
    course.name = name
    course.description = description
    db.session.commit()
    return jsonify({'message': 'Course updated successfully'}), 200


@courses_bp.route('/delete_course/<int:id>', methods=['DELETE'])
@admin_required
def delete_course(id):
    course = db.session.get(Course, id)
    if course is None:
        return jsonify({'error': 'Course not found', 'message': 'Course not found'}), 404
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted successfully'}), 200
