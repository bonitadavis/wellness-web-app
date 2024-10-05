from flask import Flask, render_template

app = Flask(__name__)

def get_posts():
     return [{"title": "Python hello", "created": "3"}]

@app.route("/")
def main():
     """Main page of the app"""
     return render_template("index.html", posts = get_posts())
