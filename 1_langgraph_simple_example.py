from typing import TypedDict
from langgraph.graph import StateGraph, START, END 
import random

# definining the graph
class State(TypedDict):
    graph_state: str

# defining the nodes
def start_node(state):
    print("-> Start node")

    return {"graph_state": state['graph_state']+" I am"}

def happy_node(state):
    print("-> Happy node")

    return {"graph_state": state['graph_state']+" happy"}

def sad_node(state):
    print("-> Sad node")

    return {"graph_state": state['graph_state']+" sad"}


# defining the edges
def decide_mood(state):

    if random.random() < 0.5:
        return "happy_node"
    else:
        return "sad_node"
    

# building the graph
builder = StateGraph(State)
builder.add_node("start_node", start_node)
builder.add_node("happy_node", happy_node)
builder.add_node("sad_node", sad_node)

# adding edges
builder.add_edge(START, "start_node")
builder.add_conditional_edges("start_node", decide_mood, ["happy_node", "sad_node"])
builder.add_edge("happy_node", END)
builder.add_edge("sad_node", END)

# compliling the grap
graph = builder.compile()

# invoking the graph
mood = graph.invoke({"graph_state":""})

print(mood['graph_state'])
