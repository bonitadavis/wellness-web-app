
# from langchain import hub
# from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
# from langchain_core.runnables import RunnableWithMessageHistory
# from langchain.schema import StrOutputParser
# from langchain_core.memory import ConversationBufferMemory
# from uuid import uuid4
# import os
# from langchain_huggingface import HuggingFaceEndpoint

# # Set up API key for HuggingFace
# api_key = "your_api_key"
# os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key

# model_id = "mistralai/Mistral-7B-Instruct-v0.2"

# llm = HuggingFaceEndpoint(
#     repo_id=model_id,
#     temperature=0.5,
#     huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"]
# )

# SESSION_ID = str(uuid4())
# print(f"Session ID: {SESSION_ID}")

# # Memory for conversation history
# memory = ConversationBufferMemory()

# # Prompt templates
# NAME_PROMPT_TEMPLATE = """You are a user assistant. Helping them decide what they want their next mental or physical health goal to focus on.
# Question: {question}
# """
# name_prompt = PromptTemplate.from_template(NAME_PROMPT_TEMPLATE)

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful assistant. Answer only the current question to the best of your ability.",
#         ),
#         ("placeholder", "{chat_history}"),
#         ("human", "Current question: {input}"),
#     ]
# )

# chain = prompt | llm | StrOutputParser()

# # Chatbot loop
# while True:
#     q = input("> ")

#     if q == "exit":
#         break

#     # Handle goal-related commands
#     if q.startswith("create goal"):
#         title = input("What is the title of your goal? ")
#         category = input("What category does this goal fall under? ")
#         days = input("How many days a week will you commit to this goal? ")
#         reminders = input("What reminders would you like? ")
#         weeks = input("How many weeks do you want to set this goal for? ")

#         goal_data = {
#             "goal_id": str(uuid4()),
#             "user_id": SESSION_ID,  # Replace with actual user ID
#             "title": title,
#             "category": category,
#             "days": days,
#             "reminders": reminders,
#             "times_completed": 0,
#             "limit": None,  # Set limit if applicable
#             "weeks": weeks,
#             "streak": 0,
#             "completed": False,
#             "daily_completed": False
#         }

#         create_goal(goal_data)  # Make sure you have this function defined
#         print(f"Goal '{title}' created!")

#     elif q == "view goals":
#         goals = get_goals(SESSION_ID)  # Replace with actual user ID
#         if goals:
#             for goal in goals:
#                 print(goal)
#         else:
#             print("No goals found.")

#     elif q.startswith("update goal"):
#         goal_id = input("Enter the goal ID to update: ")
#         updates = {}
#         title = input("New title (leave blank to skip): ")
#         if title:
#             updates['title'] = title

#         category = input("New category (leave blank to skip): ")
#         if category:
#             updates['category'] = category

#         update_goal(goal_id, updates)  # Ensure this function is defined
#         print("Goal updated!")

#     elif q.startswith("delete goal"):
#         goal_id = input("Enter the goal ID to delete: ")
#         delete_goal(goal_id)  # Ensure this function is defined
#         print("Goal deleted!")

#     else:
#         # Add user message to memory
#         memory.add_user_message(q)

#         # Get chat history for LLM input
#         chat_history = memory.get_messages()

#         # Call the LLM with the chat history
#         response = chain.invoke(
#             {"input": q, "chat history": chat_history},
#             config={"configurable": {"session_id": SESSION_ID}}
#         )

#         print(response)

#         # Add assistant's response to memory
#         memory.add_assistant_message(response)









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
#model_id = "meta-llama/Llama-2-70b-hf"

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


while True:
    q = input("> ")

    if q.lower() in ["exit", "quit"]:
        break

    # Check for greetings
    is_greeting = any(greet in q.lower() for greet in ["hello", "hi", "hey", "greetings", "salutations"])

    is_health_related = any(keyword in q.lower() for keyword in ["health", "goal", "nutrition", "exercise", "mental", "wellness", "meditation", "yoga"])

    # Construct the prompt based on whether it's a greeting
    # if is_greeting:
    #     prompt_text = (
    #         "You are a friendly assistant. When greeted, respond warmly and concisely. Wait for next input from user "
    #     ).format(user_input=q)
    # else:
    #     prompt_text = (
    #         "You are a helpful assistant. Provide a brief and relevant response to the user's question. "
    #     ).format(user_input=q)

    ####WORKEDBEST####
    # if is_greeting:
    #     prompt_text = "You are a friendly assistant. When greeted, respond warmly and concisely."
    # else:
    #     # Check if the input is on health goals
    #     if "health" in q.lower() or "goal" in q.lower():
    #         prompt_text = "You are a helpful assistant focused on health goals. User: {user_input}".format(user_input=q)
    #     else:
    #         prompt_text = "I'm sorry, but I can only assist with questions related to health goals."

    if is_greeting:
        prompt_text = "You are a friendly assistant. When greeted, respond warmly and concisely."
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
