from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

scheduler = BackgroundScheduler()

def send_email(user_email, title, time_of_day):
    subject = f"Reminder: {title}"
    message = {
        "morning": f"Good morning! Don't forget to {title} today!",
        "noon": f"Hello! It's time for your midday {title} reminder.",
        "evening": f"Good evening! Remember to {title} before the day ends!"
    }
    body = message[time_of_day]

    from_email = "smu.health.2024@gmail.com"
    from_password = "HackSMU2024"  # Consider using an environment variable for security

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  
        server.starttls() 
        server.login(from_email, from_password) 
        server.send_message(msg) 
        server.quit()  
    except Exception as e:
        print(f"Failed to send email: {e}")


def schedule_reminders(goal):
    if goal['reminders']:
        user_email = goal['user_email'] 
        title = goal['title']

        current_time = datetime.now()

        notification_times = [
            ("morning", current_time.replace(hour=9, minute=0, second=0, microsecond=0)),
            ("noon", current_time.replace(hour=12, minute=0, second=0, microsecond=0)),
            ("evening", current_time.replace(hour=22, minute=0, second=0, microsecond=0)),
        ]

        #schedule for notification
        for time_of_day, notification_time in notification_times:
            if notification_time < current_time:
                notification_time += timedelta(days=1)

            while not goal['days_of_week'][notification_time.weekday()]:
                notification_time += timedelta(days=1)

            scheduler.add_job(send_email, 'date', run_date=notification_time, args=[user_email, title, time_of_day])

scheduler.start()
