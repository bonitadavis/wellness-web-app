from flask import Flask, render_template, request
import random

app = Flask(__name__)

def get_data():
     return [{"name": "Student"},
     {"title": "Python hello", "days": random.randint(0, 7), "limit": 7, "type": "physical"},
     {"title": "Mental health goal", "days": random.randint(0, 7), "limit": 7, "type": "mental"}]

@app.route("/update", methods=['GET', 'POST'])
def update_data():
    """Do something to update data"""
    return update_data_internal(int(request.args['goal']))

def update_data_internal(goal):
    print("We're updating goal number %d" % goal)
    return main()

@app.route("/")
def main():
     """Main page of the app"""
     # Front-end conversion for display
     our_data = get_data()
     for index in range(1, len(our_data)):
         our_type = our_data[index].pop("type", None)
         match our_type:
             case "physical":
                 our_data[index]["color"] = "#cc0035"
             case "mental":
                 our_data[index]["color"] = "#354ca1"
     return render_template("index.html", data = our_data)

