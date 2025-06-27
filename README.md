# ITSM Expert Agent

An AI-powered IT Service Management (ITSM) agent using LangGraph and LangChain.

## Project Purpose
This project provides an extensible, testable ITSM agent that classifies user issues, simulates CMDB lookups, handles SLA-based routing, generates tickets, and crafts user-facing responses.

## Architecture (LangGraph Workflow)
```
+-------------------+
|  HumanMessage     |
+-------------------+
          |
          v
+-------------------+
| classify_request  |
+-------------------+
          |
          v
+-------------------+
|   query_cmdb      |
+-------------------+
          |
          v
+-------------------+
|   check_sla       |
+-------------------+
          |
          v
+-------------------+
| generate_ticket   |
+-------------------+
          |
          v
+-------------------+
| generate_response |
+-------------------+
          |
          v
+-------------------+
|     Output        |
+-------------------+
```

## Usage

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the agent
```bash
python run.py
```

## Testing

Run all tests with:
```bash
python -m unittest discover tests
```

## Extension Plan
- **Real CMDB/ServiceNow Integration:**
  - Replace stubbed functions in `itsm_agent.py` with API calls.
  - Use MCP ToolWrapper or ServiceNow REST API.
- **UI View:**
  - Add a Streamlit or NextJS frontend to track tickets.
- **Agent Permissions:**
  - Implement role-based access and escalation chains in the state.

## Project Structure
```
itsm-agent/
├── itsm_agent/
│   ├── __init__.py
│   ├── itsm_agent.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   └── test_agent.py
├── requirements.txt
├── .env
├── README.md
└── run.py
``` 