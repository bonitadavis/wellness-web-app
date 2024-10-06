from flask import Flask, render_template, request
import random

app = Flask(__name__)

def get_data():
     return [{"name": "Student"},
     {"goalID": 10, "title": "Python hello", "days": random.randint(0, 7), "limit": 7, "type": "physical"},
     {"goalID": 20, "title": "Mental health goal", "days": random.randint(0, 7), "limit": 7, "type": "mental"}]

@app.route("/add", methods=['GET', 'POST'])
def add_data():
    """Do something to add a goal"""
    name = request.args['name']
    goal_type = request.args['type']
    days = []
    notifs = int(request.args['notifs']) != 0
    weeks = request.args['weeks']
    for i in range(0, 7):
        days.append(int(request.args["d%d" % i]) != 0)
    return add_data_internal(name, goal_type, days, notifs, weeks)

def add_data_internal(name: str, goal_type: str, days: list[bool], notifs: bool, weeks: int):
    print("We're adding {}, {}, {}, {}, {}".format(name, goal_type, days, notifs, weeks))
    return main()

@app.route("/update", methods=['GET', 'POST'])
def update_data():
    """Do something to update data"""
    return update_data_internal(int(request.args['goal']))

def update_data_internal(goal_id: int):
    print("We're updating goal number %d" % goal_id)
    return main()

@app.route("/")
def main():
     """Main page of the app"""
     # Front-end conversion for display
     our_data = get_data()
     profile_data = our_data[0]
     incomplete_goals = []
     complete_goals = []
     for index in range(1, len(our_data)):
         our_type = our_data[index].pop("type", None)
         match our_type:
             case "physical":
                 our_data[index]["color"] = "#cc0035"
             case "mental":
                 our_data[index]["color"] = "#354ca1"
         if (our_data[index]["days"] == our_data[index]["limit"]):
             complete_goals.append(our_data[index])
         else:
             incomplete_goals.append(our_data[index])
     return render_template("index.html", profile_data = profile_data, incomplete_goals = incomplete_goals, complete_goals = complete_goals)

