from flask import Flask, render_template, request, jsonify
from propelauth_py import init_base_auth, UnauthorizedException
from collections import namedtuple
from datetime import datetime
from bson import ObjectId
import models
import chatbot_module

app = Flask(__name__)

# Initialize PropelAuth
auth = init_base_auth(
    "https://62994739.propelauthtest.com",
    "bdb493aff8143e9cdcd82bba138064e34bb20ee62c040c513e62fc64977e0eda5da09c127aab6e47c94a8705f25994ed"
)

#global_user_id = 0
global_user_id = "123456"
global_message_pairs = []
global_chat_history = ""

def get_data() -> dict[list]:
    # print([*models.db["users"].find({})])

    if (global_user_id != 0):
        user = models.db["users"].find_one({"userID": global_user_id})
        if (user is None):
            print("User does not exist in database, displaying logged out view")
            return []
        
        if "_id" in user:
            user["_id"] = str(user["_id"])

        print(user)
        goals = [*models.db["goals"].find({"userID": user.get("userID", 0)})]
        print("There are {} goals".format(len(goals)))
        for goal in goals:
            if "_id" in goal:
                goal["_id"] = str(goal["_id"])
            print(goal)
        goals.insert(0, user)
        return goals
    else:
        print("No data can be retrieved as user is logged out")
        return []

@app.route("/add", methods=['GET', 'POST'])
def add_data():
    """Do something to add a goal"""
    name = request.args['name']
    goal_type = request.args['type']
    days = []
    notifs = int(request.args['notifs']) != 0
    weeks = int(request.args['weeks'])
    for i in range(0, 7):
        days.append(int(request.args["d%d" % i]) != 0)
    return add_data_internal(name, goal_type, days, notifs, weeks)

def add_data_internal(name: str, goal_type: str, days: list[bool], notifs: bool, weeks: int):
    print("We're adding {}, {}, {}, {}, {}".format(name, goal_type, days, notifs, weeks))
    models.create_goal(models.db, global_user_id, name, goal_type, days, notifs, weeks)
    return main()

@app.route("/edit", methods=['GET', 'POST'])
def edit_goal():
    """Do something to edit a goal"""
    goal_id = request.args['id']
    name = request.args['name']
    notifs = int(request.args['notifs']) != 0
    return edit_goal_internal(goal_id, name, notifs)

def edit_goal_internal(goal_id: str, name: str, notifs: bool):
    print("We're changing goal number {} to name {} and notifications {}".format(goal_id, name, notifs))
    Request = namedtuple("Request", ["method", "json"])
    models.edit_goal(models.db, Request("PUT", {"name": name, "reminders": notifs}), goal_id)
    return main()

@app.route("/complete", methods=['GET', 'POST'])
def complete_goal():
    """Do something to update data"""
    return complete_goal_internal(request.args['goal'])

def complete_goal_internal(goal_id: str):
    print("We're completing goal number {}".format(goal_id))
    models.complete_goal(models.db, global_user_id, goal_id) 
    return main()

@app.route("/login", methods=['GET', 'POST'])
def login_user():
    """Do something to log in a user"""
    user_id = request.args['id']
    email = request.args['email']
    name = request.args['name']
    return login_user_internal(user_id, email, name)

def login_user_internal(user_id: str, email: str, name: str):
    global global_user_id
    print("We logged in {} whose email is {} and ID is {}".format(name, email, user_id))
    if (models.db["users"].find_one({"userID": global_user_id}) is None):
        models.register_user(models.db, name, email, user_id)
    global_user_id = user_id
    return get_data()

@app.route("/message", methods=['GET', 'POST'])
def message_user():
    global global_message_pairs
    message = request.args['text']
    global_message_pairs.append(message_user_internal(message))
    return main()

def message_user_internal(msg: str):
    print("We are messaging {}".format(msg))
    user_msg = {"date": datetime.now(), "msg": msg}
    global global_chat_history
    response, global_chat_history = chatbot_module.call_chatbot(msg, global_chat_history)
    bot_msg = {"date": datetime.now(), "msg": response}
    return (user_msg, bot_msg)

@app.route("/")
def main():
     """Main page of the app"""
     print(global_message_pairs)

     # Front-end conversion for display
     print("Getting data")
     our_data = get_data()
     if len(our_data) > 0:
        profile_data = our_data[0]
        incomplete_goals = []
        complete_goals = []
        day_names = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        for goal in our_data[1:]:
            days = []
            for day_index, _ in enumerate(goal["days"]):
                if (goal["days"][day_index]):
                    days.append(day_names[day_index])
            goal["user_days"] = ', '.join(days)
            goal["weeks"] = goal["limit"] // len(days)
            match goal["category"]:
                case "physical":
                    goal["color"] = "#cc0035"
                case "mental":
                    goal["color"] = "#354ca1"
            if (goal["days"] == goal["limit"]):
                complete_goals.append(goal)
            else:
                incomplete_goals.append(goal)
        return render_template("index.html",
            profile_data = profile_data,
            incomplete_goals = incomplete_goals,
            complete_goals = complete_goals,
            messages = global_message_pairs)
     else:
         return render_template("index.html",
             profile_data = [],
             incomplete_goals = [],
             complete_goals = [],
             messages = [])

@app.route("/api/whoami", methods=["GET"])
def whoami():
     auth_header = request.headers.get("Authorization")
     if not auth_header:
          return jsonify({"error": "Missing authorization header"}), 401
     try:
        user = auth.validate_access_token_and_get_user(auth_header)
        return jsonify({"user_id": user.user_id, "email": user.email}), 200
     except UnauthorizedException:
        return jsonify({"error": "Invalid access token"}), 401

