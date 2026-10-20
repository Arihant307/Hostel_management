# @app.route('/add_payment', methods=['POST'])
# def add_payment():
#     data = request.get_json()
#     student_id = data.get('student_id')
#     amount = data.get('amount')
#     method = data.get('method')

#     if not student_id or not amount or not method:
#         return jsonify({'error': 'Missing required fields'}), 400

#     cursor = mysql.connection.cursor()
#     cursor.execute("INSERT INTO payments (student_id, amount, method, date) VALUES (%s, %s, %s, NOW())",
#                     (student_id, amount, method))
#     mysql.connection.commit()
#     return jsonify({'message': 'Payment recorded successfully'}), 201

# @app.route('/get_payments', methods=['GET'])
# def get_payments():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM payments ORDER BY date DESC")
#     payments = cursor.fetchall()
#     return jsonify(payments)
