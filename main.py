from flask import Flask, render_template, request, jsonify
from propelauth_py import init_base_auth, UnauthorizedException
import random

app = Flask(__name__)

# Initialize PropelAuth
auth = init_base_auth(
    "https://62994739.propelauthtest.com",
    "bdb493aff8143e9cdcd82bba138064e34bb20ee62c040c513e62fc64977e0eda5da09c127aab6e47c94a8705f25994ed"
)

def get_data():
     return [{"name": "Student"},
     {"title": "Python hello", "days": random.randint(0, 7), "limit": 7, "type": "physical", "goalID": 10},
     {"title": "Mental health goal", "days": random.randint(0, 7), "limit": 7, "type": "mental", "goalID": 20}]

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

@app.route("/login", methods=['GET', 'POST'])
def login_user():
    user_id = request.args['id']
    email = request.args['email']
    name = request.args['name']
    return login_user_internal(user_id, email, name)

def login_user_internal(user_id: str, email: str, name: str):
    print("We logged in {} whose email is {} and ID is {}".format(name, email, user_id))
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

