from typing import TypedDict
from langgraph.graph import StateGraph, START, END 
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv() 

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Chatbot")

# Display the chat history.
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

# defining the llm
llm = init_chat_model(os.getenv("CHAT_MODEL"), model_provider=os.getenv("MODEL_PROVIDER"), temperature=os.getenv("CHAT_TEMPERATURE"))
sys_message = SystemMessage(content="You are a friendly chatbot. Engage in a pleasant conversation with the user.")

# definining the graph
class State(TypedDict):
    messages: list[AnyMessage]

# defining the nodes
def chat(state):

    response = llm.invoke([sys_message] + state['messages'])

    return {"messages": state['messages'] + [AIMessage(content=response.content)]}



# building the graph
builder = StateGraph(State)
builder.add_node("chat", chat)

# logic
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

# compliling the grap
graph = builder.compile()



# Handle user input.
if prompt := st.chat_input("How are you?"):
    # Add user message to chat history
    user_message = HumanMessage(content=prompt)
    st.session_state.messages.append(user_message)

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Create a placeholder for the streaming response
    with st.chat_message("assistant"):
        response = graph.invoke({"messages": st.session_state.messages})

        st.write(response['messages'][-1].content)
        st.session_state.messages.append(AIMessage(content=response['messages'][-1].content))