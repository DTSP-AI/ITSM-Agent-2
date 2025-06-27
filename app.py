import streamlit as st
from itsm_agent.itsm_agent import itsm_graph, ITSMState, HumanMessage

# --- Page Config & Title ---
st.set_page_config(page_title="ITSM Agent Interface", layout="wide", initial_sidebar_state="expanded")
st.title("ITSM Expert Agent Chat")

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "tasks" not in st.session_state:
    st.session_state["tasks"] = [
        {
            "id": "subagent-1",
            "name": "CMDB Lookup",
            "status": "In Progress",
            "percent": 70,
            "summary": "Looking up asset LPT-JDOE-001",
            "full_details": {
                "query": "SELECT * FROM cmdb WHERE user='jdoe'",
                "result": "Found 1 asset"
            }
        },
        {
            "id": "subagent-2",
            "name": "Incident Classification",
            "status": "In Progress",
            "percent": 50,
            "summary": "Classifying user request as incident",
            "full_details": {
                "input": "I can't log into my laptop",
                "classification": "incident"
            }
        },
        {
            "id": "subagent-3",
            "name": "Ticket Generation",
            "status": "Pending",
            "percent": 0,
            "summary": "Waiting to generate ticket",
            "full_details": {
                "ticket_type": None,
                "ticket_id": None
            }
        }
    ]

# --- Task Chat State Initialization ---
if "active_task_id" not in st.session_state:
    st.session_state["active_task_id"] = None
if "active_task_context" not in st.session_state:
    st.session_state["active_task_context"] = None
if "task_chat_history" not in st.session_state:
    st.session_state["task_chat_history"] = {}

# --- Layout: Sidebar (Tasks) & Main (Chat) ---
col1, col2 = st.columns([1, 3])

with col1:
    st.header("SubAgent Tasks")
    for idx, task in enumerate(st.session_state["tasks"]):
        with st.expander(f"{task['name']} — {task['status']}", expanded=True):
            st.progress(task["percent"])
            st.write(task["summary"])
            # Trigger task detail chat view
            show_key = f"show_details_{idx}"
            if st.button("Show Details", key=show_key):
                st.session_state["active_task_id"] = task["id"]
                st.session_state["active_task_context"] = task
                if task["id"] not in st.session_state["task_chat_history"]:
                    st.session_state["task_chat_history"][task["id"]] = []

with col2:
    # Main display: Task Detail Chat or Default Chat
    if st.session_state.get("active_task_id"):
        # Task Detail Chat View
        context = st.session_state["active_task_context"]
        st.header(f"Task Detail: {context['name']}")
        st.json(context["full_details"])
        st.subheader("Task Chat")
        task_id = st.session_state["active_task_id"]
        history = st.session_state["task_chat_history"].get(task_id, [])
        for msg in history:
            if getattr(msg, "type", None) == "human":
                st.chat_message("user").write(msg.content)
            else:
                st.chat_message("ai").write(msg.content)
        user_input = st.chat_input("Ask a question about this task...")
        if user_input:
            human_msg = HumanMessage(content=user_input)
            history.append(human_msg)
            # Prepare state for task chat
            itsm_state = ITSMState(
                messages=history,
                request_type="",
                urgency=None,
                user_context=None,
                ticket_id=None,
                escalation_flag=None,
                resolution=None,
                cmdb_asset=None,
                service_now_link=None,
                active_task_id=task_id,
                active_task_context=context,
                agent_commentary=None
            )
            result = itsm_graph.invoke(itsm_state)
            # Append only new AI messages
            for msg in result["messages"][len(history):]:
                history.append(msg)
            st.session_state["task_chat_history"][task_id] = history
            st.experimental_rerun()
        if st.button("Back to Main Chat"):
            st.session_state["active_task_id"] = None
    else:
        # Default Chat View
        st.header("Chat")
        # Chat rendering
        for msg in st.session_state["chat_history"]:
            if getattr(msg, "type", None) == "human":
                st.chat_message("user").write(msg.content)
            else:
                st.chat_message("ai").write(msg.content)

        # Chat input
        user_input = st.chat_input("How can I assist you with your IT issue?")
        if user_input:
            # Append to chat history
            human_msg = HumanMessage(content=user_input)
            st.session_state["chat_history"].append(human_msg)
            # Prepare ITSMState
            itsm_state = ITSMState(
                messages=st.session_state["chat_history"],
                urgency="high",  # For demo, hardcoded
                user_context={"username": "jdoe", "department": "finance"},
                request_type="",
                ticket_id=None,
                escalation_flag=False,
                resolution=None,
                cmdb_asset=None,
                service_now_link=None,
            )
            # Invoke agent
            result = itsm_graph.invoke(itsm_state)
            # Append all returned messages
            for msg in result["messages"]:
                if msg not in st.session_state["chat_history"]:
                    st.session_state["chat_history"].append(msg)
            # Simulate task progress update
            for task in st.session_state["tasks"]:
                task["status"] = "Complete"
                task["percent"] = 100
            st.experimental_rerun()

# --- Footer ---
st.markdown("""
---
<div style='text-align:center; color:gray;'>
    <small>ITSM Agent UI &copy; 2024 &bull; Version 0.1</small>
</div>
""", unsafe_allow_html=True) 