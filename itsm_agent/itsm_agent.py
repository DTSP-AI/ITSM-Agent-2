from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import Annotated, TypedDict, List, Optional
import logging

logger = logging.getLogger(__name__)

# ----------------------------------
# STATE DEFINITION
# ----------------------------------
class ITSMState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    request_type: str                     # incident, service_request, change, etc.
    urgency: Optional[str]               # low, medium, high
    user_context: Optional[dict]         # username, department, permissions, etc.
    ticket_id: Optional[str]
    escalation_flag: Optional[bool]
    resolution: Optional[str]
    cmdb_asset: Optional[str]
    service_now_link: Optional[str]
    active_task_id: Optional[str]          # ID of task selected in UI
    active_task_context: Optional[dict]    # Full task data dict from UI
    agent_commentary: Optional[str]        # Main Agent analysis of the task

# ----------------------------------
# TOOL-LINKED NODE DEFINITIONS
# ----------------------------------
def classify_request(state: ITSMState) -> ITSMState:
    msg = state["messages"][-1].content.lower()
    if "password" in msg or "reset" in msg:
        state["request_type"] = "service_request"
    elif "can't" in msg or "error" in msg or "issue" in msg:
        state["request_type"] = "incident"
    else:
        state["request_type"] = "general"
    logger.info(f"Classified request type: {state['request_type']}")
    return state

def query_cmdb(state: ITSMState) -> ITSMState:
    user = state.get("user_context", {}).get("username", "unknown")
    # Placeholder stub for CMDB lookup
    state["cmdb_asset"] = f"LAPTOP-{user.upper()}-001"
    return state

def check_sla_and_route(state: ITSMState) -> ITSMState:
    if state.get("urgency") == "high":
        state["escalation_flag"] = True
    return state

def generate_ticket(state: ITSMState) -> ITSMState:
    # Stub: would create a ticket via ServiceNow API or similar
    ticket_type = state["request_type"]
    state["ticket_id"] = f"TCKT-{ticket_type[:3].upper()}-12345"
    state["service_now_link"] = f"https://servicenow.example.com/ticket/{state['ticket_id']}"
    return state

def generate_response(state: ITSMState) -> ITSMState:
    if state.get("request_type") == "incident":
        reply = f"🚨 Incident logged: {state['ticket_id']}. Our team is on it."
    elif state.get("request_type") == "service_request":
        reply = f"✅ Request submitted: {state['ticket_id']}. Hang tight."
    else:
        reply = "Thanks for reaching out. We'll follow up shortly."
    reply += f"\n🔗 Track it here: {state.get('service_now_link')}"
    state["messages"].append(AIMessage(content=reply))
    return state

def end_node(state: ITSMState) -> ITSMState:
    return state

# Add comment_on_task node for task commentary
def comment_on_task(state: ITSMState) -> ITSMState:
    task = state.get("active_task_context")
    if not task:
        return state

    task_name = task.get("name", "Unknown Task")
    summary = task.get("summary", "")
    detail = task.get("full_details", {})

    commentary = f"🧠 Reviewing task: **{task_name}**\n"
    commentary += f"Summary: {summary}\n"
    commentary += f"Details: {detail}\n"

    if "error" in str(detail).lower():
        commentary += "\n⚠️ I detected a possible issue. Recommend escalation."
    else:
        commentary += "\n✅ Task appears normal. Proceeding."

    state["agent_commentary"] = commentary
    return state

# ----------------------------------
# LANGGRAPH DEFINITION
# ----------------------------------
workflow = StateGraph(ITSMState)
workflow.add_node("classify_request", classify_request)
workflow.add_node("query_cmdb", query_cmdb)
workflow.add_node("check_sla", check_sla_and_route)
workflow.add_node("generate_ticket", generate_ticket)
workflow.add_node("generate_response", generate_response)
workflow.add_node("comment_on_task", comment_on_task)

workflow.set_entry_point("classify_request")
workflow.add_edge("classify_request", "query_cmdb")
workflow.add_edge("query_cmdb", "check_sla")
workflow.add_edge("check_sla", "generate_ticket")
workflow.add_edge("generate_ticket", "comment_on_task")
workflow.add_edge("comment_on_task", "generate_response")
workflow.add_edge("generate_response", END)

itsm_graph = workflow.compile()

# ----------------------------------
# CURSOR ENTRYPOINT
# ----------------------------------
if __name__ == "__main__":
    test_input = ITSMState(
        messages=[HumanMessage(content="I can't log into my laptop")],
        urgency="high",
        user_context={"username": "jdoe", "department": "finance"},
        request_type="",
        ticket_id=None,
        escalation_flag=False,
        resolution=None,
        cmdb_asset=None,
        service_now_link=None,
        active_task_context={
            "id": "task-1",
            "name": "CMDB Lookup",
            "status": "Complete",
            "percent": 100,
            "summary": "Looking up asset LPT-JDOE-001",
            "full_details": {
                "query": "SELECT * FROM cmdb WHERE user='jdoe'",
                "result": "Found 1 asset"
            }
        },
    )

    result = itsm_graph.invoke(test_input)
    for msg in result["messages"]:
        print(f"{msg.type.upper()}: {msg.content}")
    print("\nAGENT COMMENTARY:")
    print(result.get("agent_commentary")) 