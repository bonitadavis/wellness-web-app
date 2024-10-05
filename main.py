from flask import Flask, render_template
import random

app = Flask(__name__)

def get_posts():
     return [{"title": "Python hello", "days": random.randint(0, 7), "limit": 7}]

@app.route("/update", methods=['GET', 'POST'])
def update_posts():
    """Do something to update posts"""
    print("We're updating this post!")
    return main()

@app.route("/")
def main():
     """Main page of the app"""
     return render_template("index.html", posts = get_posts())
