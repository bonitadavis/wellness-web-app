
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://sarahmendoza:password@cluster0.cmoki.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["sample_mflix"]
collection = db["movies"]



def get_user_habits():
    document = collection.find_one()
    return document
    #return list(db.habits.find({"user_id": user_id}))

doc = get_user_habits()
#print(doc)