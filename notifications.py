from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import requests 

scheduler = BackgroundScheduler()

def send_email(user_email, title, time_of_day):
    """Function to send a templated email based on the time of day."""
    subject = f"Reminder: {title} at {time_of_day}"
    message = {
        "morning": f"Good morning! Don't forget to {title} today!",
        "noon": f"Hello! It's time for your midday {title} reminder.",
        "evening": f"Good evening! Remember to {title} before the day ends!"
    }
    email_body = message[time_of_day]

    #TODO: email sending

def schedule_notifications(goal):
    if goal['notifications']:
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

