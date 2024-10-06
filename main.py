from flask import Flask, render_template, request, jsonify
from propelauth_py import init_base_auth, UnauthorizedException

app = Flask(__name__)

# Initialize PropelAuth
auth = init_base_auth(
    "https://62994739.propelauthtest.com",
    "bdb493aff8143e9cdcd82bba138064e34bb20ee62c040c513e62fc64977e0eda5da09c127aab6e47c94a8705f25994ed"
)

def get_posts():
     return [{"title": "Python hello", "created": "3"}]

@app.route("/add", methods=['GET', 'POST'])
def add_data():
    """Do something to add a goal"""
    name = request.args['name']
    goal_type = request.args['type']
    days = []
    for i in range(0, 7):
        days.append(request.args["d%d" % i] == 0)
    return add_data_internal(name, goal_type, days)

def add_data_internal(name: str, goal_type: str, days: list[bool]):
    print("We're adding {} {} {}".format(name, goal_type, days))
    return main()

@app.route("/update", methods=['GET', 'POST'])
def update_data():
    """Do something to update data"""
    return update_data_internal(int(request.args['goal']))

def update_data_internal(goal: int):
    print("We're updating goal number %d" % goal)
    return main()


@app.route("/")
def main():
     """Main page of the app"""
     return render_template("index.html", posts = get_posts())

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