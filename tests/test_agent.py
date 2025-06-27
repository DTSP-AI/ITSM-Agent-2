import unittest
from itsm_agent.itsm_agent import itsm_graph, ITSMState
from langchain_core.messages import HumanMessage, AIMessage
import re

class TestITSMGraph(unittest.TestCase):
    def test_incident_classification_and_ticket(self):
        state = ITSMState(
            messages=[HumanMessage(content="I can't log into my laptop")],
            urgency="high",
            user_context={"username": "jdoe", "department": "finance"},
            request_type="",
            ticket_id=None,
            escalation_flag=False,
            resolution=None,
            cmdb_asset=None,
            service_now_link=None,
        )
        result = itsm_graph.invoke(state)
        self.assertEqual(result["request_type"], "incident")
        self.assertTrue(result["ticket_id"].startswith("TCKT-INC"))
        self.assertIn("Incident logged", result["messages"][-1].content)

    def test_service_request_classification(self):
        state = ITSMState(
            messages=[HumanMessage(content="Please reset my password")],
            urgency="medium",
            user_context={"username": "alice", "department": "hr"},
            request_type="",
            ticket_id=None,
            escalation_flag=False,
            resolution=None,
            cmdb_asset=None,
            service_now_link=None,
        )
        result = itsm_graph.invoke(state)
        self.assertEqual(result["request_type"], "service_request")
        self.assertTrue(result["ticket_id"].startswith("TCKT-SER"))
        self.assertIn("Request submitted", result["messages"][-1].content)

    def test_ticket_id_format(self):
        state = ITSMState(
            messages=[HumanMessage(content="I have an issue with my email")],
            urgency="low",
            user_context={"username": "bob", "department": "ops"},
            request_type="",
            ticket_id=None,
            escalation_flag=False,
            resolution=None,
            cmdb_asset=None,
            service_now_link=None,
        )
        result = itsm_graph.invoke(state)
        self.assertRegex(result["ticket_id"], r"TCKT-[A-Z]{3}-\d+")

if __name__ == "__main__":
    unittest.main() 