from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from backend.graph.nodes import should_continue, call_model, check_greeting_or_irrelevant, tools


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def get_agent():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("check_input", check_greeting_or_irrelevant)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    workflow.set_entry_point("check_input")
    
    workflow.add_edge("check_input", "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        }
    )
    workflow.add_edge("tools", "agent")
    
    app = workflow.compile()
    
    return app

def run_agent(question: str):
    agent = get_agent()
    
    initial_state = {
        "messages": [HumanMessage(content=question)]
    }
    
    result = agent.invoke(initial_state)
    
    messages = result["messages"]
    final_message = messages[-1]
    
    if isinstance(final_message, AIMessage):
        return final_message.content
    else:
        return str(final_message)