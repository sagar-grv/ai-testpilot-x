"""agents package — registers all V1 agents in AgentRegistry."""
from agents.registry import AgentRegistry
from agents.requirement_agent import RequirementAgent
from agents.testcase_agent import TestCaseAgent
from agents.verification_agent import VerificationAgent
from agents.selenium_agent import SeleniumAgent
from agents.api_agent import APIAgent
from agents.execution_agent import ExecutionAgent
from agents.bug_agent import BugAgent
from agents.healing_agent import HealingAgent
from agents.report_agent import ReportAgent

AgentRegistry.register("requirement", RequirementAgent)
AgentRegistry.register("testcase", TestCaseAgent)
AgentRegistry.register("verification", VerificationAgent)
AgentRegistry.register("selenium", SeleniumAgent)
AgentRegistry.register("api", APIAgent)
AgentRegistry.register("execution", ExecutionAgent)
AgentRegistry.register("bug", BugAgent)
AgentRegistry.register("healing", HealingAgent)
AgentRegistry.register("report", ReportAgent)
