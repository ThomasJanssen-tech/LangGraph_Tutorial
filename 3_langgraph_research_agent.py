from typing import TypedDict
from langgraph.graph import StateGraph, START, END 
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import streamlit as st
from functions import google_search

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

# defining Pydantic models
class ResearchRequired(BaseModel):
    is_required: bool = Field(
        description="Whether the agent needs to perform research (Google search) to answer the user's query. Use research ANY time the user asks questions about facts (just don't use it if the user asks how are you for example)"
    )

class SearchQuery(BaseModel):
    query: str = Field(
        description="The Google search query to be used for research."
    )

class ResearchResults(BaseModel):
    results: list[str] = Field(
        description="A list of relevant search results obtained from Google search. You include all the facts you can find in the text given to you."
    )

class AnswerSatisfying(BaseModel):
    is_satisfying: bool = Field(
        description="Whether the current answer is answering the user's query satisfactorily."
    )

# definining the graph
class State(TypedDict):
    messages: list[AnyMessage]
    research_query: str
    research_results: str
    research_conclusion: str
    next: str

# defining the nodes
def decide_research_required(state):

    sys_message = SystemMessage(content="Based on the conversation you have with the user, decide whether research is required. You should perform research if the user asks about facts/knowledge. Not if the user asks questions such as: how are you?")

    schema_llm = llm.with_structured_output(schema=ResearchRequired.model_json_schema(), strict=True)

    response = schema_llm.invoke(
        [sys_message] + state['messages']
    )

    print("== > Response < ==")

    print(response)

    if response['is_required']:
        return {"next":"write_search_query"}
    else:
        return {"next":"answer_user"}

def write_search_query(state):
    sys_message = SystemMessage(content="Your task is to define a search query for Google search based on the conversation you have with the user. The search query should be concise and relevant to the user's query.")

    schema_llm = llm.with_structured_output(schema=SearchQuery.model_json_schema(), strict=True)

    response = schema_llm.invoke(
        [sys_message] + state['messages']
    )

    print("RESPONSE:")
    print(response)

    return {"research_query": response['query']}

def perform_research(state):
    search_results = google_search(state['research_query'])

    print("== > Search Results < ==")
    print(search_results)

    sys_message = SystemMessage(content="You receive the HTML title and snippet of the top search results from Google search. Create a summary with all the information / facts you can find. DO NOT comment on the HTML / Javascript code but summarize the text which is included in the HTML (the information)")

    usr_message = HumanMessage(content=f"The following are the search results obtained from Google search: {search_results}.")

    print("USER MESSAGE:")
    print(usr_message)

    response = llm.invoke([sys_message] + [usr_message])

    print("== > Research Results < ==")

    print(response.content)

    return {"research_results": response.content}


def write_conclusion(state):
    sys_message = SystemMessage(content="Your task is to write a concise conclusion based on the research results provided, in the form of a response to the user. The conclusion should directly address the user's query and summarize the key findings from the research. Keep the conclusion under 500 characters.")

    usr_message = HumanMessage(content=f"The following are the research results obtained from Google search: {state['research_results']}.")

    response = llm.invoke([sys_message] + [usr_message])

    return {"research_conclusion": response.content}

def decide_answer_satisfying(state):
    sys_message = SystemMessage(content="Based on the question from the user, decide whether the following answer is answering the user's query satisfactory.")
    usr_message = HumanMessage(content=f"User's question: {state['messages'][-1]} \nAnswer based on research: {state['research_conclusion']}")

    schema_llm = llm.with_structured_output(schema=AnswerSatisfying.model_json_schema(), strict=True)

    response = schema_llm.invoke([sys_message] + [usr_message])


    if response['is_satisfying']:
        return {"next": "end_node","messages": state['messages'] + [AIMessage(content=state['research_conclusion'])]}
    else:
        return {"next": "write_search_query"}

def answer_user(state):

    sys_message = SystemMessage(content="Answer the user's query based on the conversation.")

    response = llm.invoke([sys_message] + state['messages'])

    return {"messages": state['messages'] + [AIMessage(content=response.content)]}


def end_node(state):
    return {}

# building the graph
builder = StateGraph(State)
builder.add_node("decide_research_required", decide_research_required)
builder.add_node("write_search_query", write_search_query)
builder.add_node("perform_research", perform_research)
builder.add_node("write_conclusion", write_conclusion)
builder.add_node("decide_answer_satisfying", decide_answer_satisfying)
builder.add_node("answer_user", answer_user)
builder.add_node("end_node", end_node)

# add edges
builder.add_edge(START, "decide_research_required")
builder.add_edge("write_search_query", "perform_research")
builder.add_edge("perform_research", "write_conclusion")
builder.add_edge("write_conclusion", "decide_answer_satisfying")
builder.add_edge("end_node", END)

# add conditional edges
builder.add_conditional_edges(
    "decide_research_required",
    lambda state: state.get("next"),
    {"write_search_query": "write_search_query", "answer_user": "answer_user"}
)

builder.add_conditional_edges(
    "decide_answer_satisfying",
    lambda state: state.get("next"),
    {"end_node": "end_node", "write_search_query": "write_search_query"}
)

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