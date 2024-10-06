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

api_key = "api  key"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key


model_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm = HuggingFaceEndpoint(
    repo_id=model_id,
    temperature=0.5,
    huggingfacehub_api_token=os.environ["HUGGINGFACEHUB_API_TOKEN"]
)


SESSION_ID = str(uuid4())
print(f"Session ID: {SESSION_ID}")


NAME_PROMPT_TEMPLATE = """You are a pirate captain who has been lost at sea for thirty years. Respond to only the provided question in the most frustrating manner possible.
Question: {question}
"""

name_prompt = PromptTemplate.from_template(NAME_PROMPT_TEMPLATE)



prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer only the current question to the best of your ability.",
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

    if (q == "exit"):
        break

    response = chain_with_message_history.invoke(
        { "input":q, "chat history": convo_history.getMessages()},
        config = {"configurable": {"session_id": SESSION_ID}}
    )

    type(response)
    print(response)

    convo_history.add_message(q)
    convo_history.add_ai_message(response)
