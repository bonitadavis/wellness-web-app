from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import create_goal
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

# if "MONGODB_PASS" in os.environ:
#     uri = "mongodb+srv://sarahmendoza:{}@cluster0.cmoki.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(os.environ["MONGODB_PASS"])
# else:
#     raise "MONGODB_PASS not in environment"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# db = client["SMU_HealthTracker"]

scheduler = BackgroundScheduler()

def send_email(user_email, title, time_of_day, name):
    subject = f"Reminder: {title}"
    message = {
        "morning": f"Good morning, {name}! Don't forget to {title} today!",
        "noon": f"Hello, {name}! It's time for your midday {title} reminder.",
        "evening": f"Good evening, {name}! Remember to {title} before the day ends!"
    }
    body = message[time_of_day]

    from_email = "smu.health.2024@gmail.com"
    from_password = "zofg leib hzzh xbxe" 

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
    name = db.users.find_one({"user_id": goal["user_id"]}).get("name")
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

            scheduler.add_job(send_email, 'date', run_date=notification_time, args=[user_email, title, time_of_day, name])

scheduler.start()


# def main():
#     goal = db.goals.find_one({"goal_id": "123"})
#     db.users.update_one({"userID": "123456"},  {"$set": {"name": "John"}})
#     user = db.users.find_one({"userID": "123456"})
#     name = user.get("name")
#     send_email("nsavova@smu.edu", goal["title"], "evening", name)

# if __name__ == "__main__":
#     main()