from langgraph.graph import StateGraph, START, END
from typing import Any, Optional
import logging

from api.providers.base import BaseChatModel
from api.core.state.chatstate import ChatState
from api.core.node.call_model import make_call_model_node

logger = logging.getLogger(__name__)

def create_graph(model: BaseChatModel):
    builder = StateGraph(ChatState)
    builder.add_node("call_model", make_call_model_node(model))
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)
    return builder.compile()
