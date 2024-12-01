from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Sample available slots; in production, pull from a database
available_slots = ['10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM']

# Function to send invitation email
def send_invitation_email(candidate_email, candidate_name, scheduling_link):
    message = Mail(
        from_email='goxthamg2003@gmail.com',
        to_emails=candidate_email,
        subject='Interview Invitation',
        html_content=f"""
            <p>Dear {candidate_name},</p>
            <p>We are pleased to invite you to schedule an interview with us.</p>
            <p>Please click the link below to choose your preferred time slot:</p>
            <a href="{scheduling_link}">Schedule Interview</a>
            <p>Thank you!</p>
        """
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Email sent with status code {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to send confirmation email
def send_confirmation_email(candidate_email, candidate_name, selected_slot):
    message = Mail(
        from_email='goxthamg2003@gmail.com',
        to_emails=candidate_email,
        subject='Interview Slot Confirmation',
        html_content=f"""
            <p>Dear {candidate_name},</p>
            <p>Your interview has been scheduled for {selected_slot}.</p>
            <p>To join the interview, please use the link below:</p>
            <a href="http://interview_application_link">Join Interview</a>
            <p>Thank you, and we look forward to speaking with you!</p>
        """
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Confirmation email sent with status code {response.status_code}")
    except Exception as e:
        print(f"Error sending confirmation email: {e}")

# Home route to show available slots
@app.route('/')
def home():
    return render_template('slots.html', slots=available_slots)

# Route to handle slot selection
@app.route('/select_slot', methods=['POST'])
def select_slot():
    selected_slot = request.form['slot']
    candidate_name = request.form['name']
    candidate_email = request.form['email']
    
    # Send confirmation email
    send_confirmation_email(candidate_email, candidate_name, selected_slot)

    # Redirect to a confirmation page
    return redirect(url_for('confirmation'))

# Confirmation page route
@app.route('/confirmation')
def confirmation():
    return "<h3>Your slot has been booked. Check your email for details.</h3>"

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use port 5001 or another available port

