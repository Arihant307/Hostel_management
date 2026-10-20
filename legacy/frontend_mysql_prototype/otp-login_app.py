# from flask_mail import Mail, Message
# import random

# # Configure Flask-Mail for sending OTPs
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Replace with your email
# app.config['MAIL_PASSWORD'] = 'your-email-password'  # Replace with your email password
# app.config['MAIL_USE_TLS'] = True

# mail = Mail(app)

# otp_storage = {}  # Store OTPs temporarily

# @app.route('/send_otp', methods=['POST'])
# def send_otp():
#     data = request.get_json()
#     email = data.get('email')

#     otp = random.randint(100000, 999999)  # Generate 6-digit OTP
#     otp_storage[email] = otp

#     msg = Message('Your Login OTP', sender='your-email@gmail.com', recipients=[email])
#     msg.body = f'Your OTP for login is: {otp}'
#     mail.send(msg)

#     return jsonify({'message': 'OTP sent successfully'}), 200

# @app.route('/verify_otp', methods=['POST'])
# def verify_otp():
#     data = request.get_json()
#     email = data.get('email')
#     otp = int(data.get('otp'))

#     if otp_storage.get(email) == otp:
#         del otp_storage[email]  # Remove OTP after use
#         return jsonify({'message': 'OTP verified successfully'}), 200
#     else:
#         return jsonify({'error': 'Invalid OTP'}), 400
