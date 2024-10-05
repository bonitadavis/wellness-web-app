from flask_mail import Mail, Message
from flask import Flask

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)

def send_notification(email, goal):
    msg = Message('Goal Reminder', sender='noreply@example.com', recipients=[email])
    msg.body = f"Don't forget to complete your goal: {goal['description']} today!"
    mail.send(msg)
