import os
import unittest
from application.handlers import agent


class TestAgent(unittest.TestCase):

    def test_load_brain(self):
        data_dir = os.path.join(os.path.dirname(__file__), "../data/release")
        agent.AgentHandler.load_brain(data_dir)
        self.assertTrue(agent.AgentHandler.BRAIN)
        agent.AgentHandler.BRAIN = None
