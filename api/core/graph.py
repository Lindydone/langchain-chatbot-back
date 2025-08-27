from langgraph.graph import StateGraph, START, END
from api.core.state.chatstate import ChatState
from api.core.node.call_model import make_call_model_node
from api.core.node.persist import persist
from api.providers.base import BaseChatModel

def create_graph(model: BaseChatModel):
    builder = StateGraph(ChatState)
    builder.add_node("call_model", make_call_model_node(model))
    builder.add_node("persist", persist)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", "persist")
    builder.add_edge("persist", END)
    return builder.compile()