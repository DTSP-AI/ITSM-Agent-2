"""
CLI entrypoint for the ITSM Expert Agent.
"""
import sys
from itsm_agent.itsm_agent import itsm_graph, ITSMState
from langchain_core.messages import HumanMessage

def main():
    """Run the ITSM agent with CLI input."""
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("HUMAN: ")
    state = ITSMState(
        messages=[HumanMessage(content=user_input)],
        urgency="high",  # For demo, default to high
        user_context={"username": "cli_user", "department": "IT"},
        request_type="",
        ticket_id=None,
        escalation_flag=False,
        resolution=None,
        cmdb_asset=None,
        service_now_link=None,
    )
    result = itsm_graph.invoke(state)
    for msg in result["messages"]:
        print(f"{msg.type.upper()}: {msg.content}")

if __name__ == "__main__":
    main() 