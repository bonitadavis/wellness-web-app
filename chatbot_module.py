from models import create_goal, register_user, complete_goal, update_goal, edit_goal, reset_daily_goals
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

if "MONGODB_PASS" in os.environ:
    uri = "mongodb+srv://sarahmendoza:{}@cluster0.cmoki.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(os.environ["MONGODB_PASS"])
else:
    raise "MONGODB_PASS not in environment"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["SMU_HealthTracker"]

#############ATTEMPT ONE####################
from langchain import hub
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory

from operator import itemgetter

from uuid import uuid4
import os

from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

#api_key = "api  key"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"


model_id = "mistralai/Mistral-7B-Instruct-v0.2"
#model_id = "meta-llama/Llama-2-7b-chat"

llm = HuggingFaceEndpoint(
    repo_id=model_id,
    temperature=0.5,
    huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"]
)


SESSION_ID = str(uuid4())
print(f"Session ID: {SESSION_ID}")


NAME_PROMPT_TEMPLATE = """You are a user assistant. Helping them decide what they want their next mental or physical health goal to focus on.
Question: {question}
"""

name_prompt = PromptTemplate.from_template(NAME_PROMPT_TEMPLATE)



prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant focused solely on helping users set productive MENTAL or PHYSICAL health goals. If the user's question is completely unrelated to health goals, respond with: 'I'm sorry, but I can only assist with questions related to health goals.' Do not infer or generate context-based responses. Keep your responses short and NO REPETITION.",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "Current question: {input}"),
    ]
)

chain = prompt | llm | StrOutputParser()


convo_chain = name_prompt | llm | StrOutputParser()


convo_history = ChatMessageHistory()

chain_with_message_history = RunnableWithMessageHistory(
    chain,
    lambda SESSION_ID: convo_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


while True:
    q = input("> ")

    if q.lower() in ["exit", "quit", "bye", "thank you bye", "goodbye"]:
        break

    # Check for greetings
    is_greeting = any(greet in q.lower() for greet in ["hello", "hi", "hey"])

    is_health_related = any(keyword in q.lower() for keyword in ["health", "goal", "nutrition", "exercise", "mental", "wellness", "meditation", "yoga"])

    is_goal_creation = "create goal" in q.lower() or "set a goal" in q.lower()


    if is_greeting:
        prompt_text = "You are a friendly assistant. When greeted, respond warmly and concisely."
    elif is_goal_creation:
        title = input("What is the title of your goal? ")
        category = input("What category is this goal in? ")

        # Display the days of the week for selection
        print("Which days do you want to work on this goal? (Select by number, separated by commas):")
        for i, day in enumerate(days_of_week):
            print(f"{i + 1}. {day}")

        # Get user input for days
        selected_days = input("Enter the numbers of the days (e.g., 1,3,5): ")
        selected_indices = [int(i.strip()) - 1 for i in selected_days.split(",") if i.strip().isdigit()]
        days = [i in selected_indices for i in range(len(days_of_week))]

        reminders = input("Would you like to set reminders? (yes/no) ").lower() == 'yes'
        weeks = int(input("For how many weeks do you want to set this goal? "))

        #retrieve from session
        user_id = 123456  

        # Create the goal in the database
        create_goal(db, user_id, title, category, days, reminders, weeks)

        print("Your goal has been created successfully! I'm glad I could help and best of luck with your goals :)")
        break
    elif is_health_related:
        prompt_text = "You are a helpful assistant focused on health goals. User: {user_input}".format(user_input=q)
    else:
        prompt_text = "Say exactly the following and nothing more: 'I'm sorry, but I can only assist with questions related to health goals.'"



    # Prepare the input data for the model
    input_data = {
        "input": prompt_text,
        "chat_history": convo_history.messages
    }

    # Invoke the chain with the current input and conversation history
    response = chain_with_message_history.invoke(
        input_data,
        config={"configurable": {"session_id": SESSION_ID}}
    )

    # Print the response
    print(response)

    # Add the user and AI messages to the conversation history
    convo_history.add_message(q)
    convo_history.add_ai_message(response)

    # Optional: Clear conversation history after a greeting to limit context
    if is_greeting:
        convo_history.clear()  # or reset to limit context carry-over




# while True:
#     q = input("> ")

#     if q.lower() in ["exit", "quit"]:
#         break

#     # Prepare a context-aware prompt
#     if q.lower() in ["hello", "hi", "hey"]:
#         prompt_text = f"You are a friendly assistant. Respond to greetings warmly and briefly. User: {q}"
#     else:
#         prompt_text = f"You are a helpful assistant. Respond to the following question with relevant information. User: {q}"

#     # Create the input for the model
#     input_data = {
#         "input": prompt_text,
#         "chat_history": convo_history.messages
#     }

#     # Invoke the chain with the current input and conversation history
#     response = chain_with_message_history.invoke(
#         input_data,
#         config={"configurable": {"session_id": SESSION_ID}}
#     )

#     # prompt_text = (
#     #     "You are a friendly assistant. If the user greets you, respond warmly with no additional information and wait for a response from the human. "
#     #     "If they ask a question, provide helpful and relevant information. "
#     #     "User: {user_input}"
#     # ).format(user_input=q)

#     # # Prepare the input data for the model
#     # input_data = {
#     #     "input": prompt_text,
#     #     "chat_history": convo_history.messages
#     # }

#     # # Invoke the chain with the current input and conversation history
#     # response = chain_with_message_history.invoke(
#     #     input_data,
#     #     config={"configurable": {"session_id": SESSION_ID}}
#     # )

#     print(response)

#     # Add the user and AI messages to the conversation history
#     convo_history.add_message(q)
#     convo_history.add_ai_message(response)
