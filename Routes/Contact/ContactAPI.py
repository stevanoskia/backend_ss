from flask import Blueprint, Flask, request, jsonify
from flask_redmail import RedMail
from Config.Config import app
import traceback

contact_api = Blueprint('contact', __name__)

redmail = RedMail(app)

@contact_api.route('/contact', methods=["GET", "PUT" , "POST"])
def contact():
    try:
        data = request.json

        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not name or not email or not message:
            return jsonify({'error': 'Missing required fields'}), 400

        subject = f'New Contact Form Submission from {name}'
        
        # Using redmail.send to send the email
        redmail.send(
            subject=subject,
            receivers=['nikoloski.davorr@gmail.com'],
            html=f"<h1>{subject}</h1><p>{message}/n From {email}</p>",
            sender='pyFlaskDBTest@hotmail.com'
        )

        return jsonify({'message': 'Email sent successfully'}), 200

    except Exception as e:
        traceback.print_exc()  # Print the full traceback
        return jsonify({'error': str(e)}), 500
