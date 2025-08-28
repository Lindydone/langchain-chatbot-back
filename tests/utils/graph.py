from langgraph.graph import StateGraph, START, END
from api.core.node.call_model import make_call_model_node
from api.core.state.chatstate import ChatState

async def persist_noop(state: ChatState) -> ChatState:
    state["persist_called"] = True
    try:
        msgs = state.get("messages") or []
        if msgs and msgs[-1].get("role") == "assistant":
            msgs[-1]["content"] = (msgs[-1].get("content") or "") + " [persist]"
    except Exception:
        pass
    return state

def make_min_graph_with_persist(model):
    b = StateGraph(ChatState)
    b.add_node("call_model", make_call_model_node(model))
    b.add_node("persist", persist_noop)
    b.add_edge(START, "call_model")
    b.add_edge("call_model", "persist")
    b.add_edge("persist", END)
    return b.compile()
