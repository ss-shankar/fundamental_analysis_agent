import os

from strands import Agent
from strands.models import BedrockModel

SYSTEM_PROMPT = """You are a fundamental analysis agent.
Given a company name, give a brief fundamental overview covering:
business model, revenue drivers, competitive position, and key risks."""

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", "us-east-1")


def create_orchestrator() -> Agent:
    model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
    return Agent(model=model, system_prompt=SYSTEM_PROMPT)


def analyze(company: str) -> str:
    agent = create_orchestrator()
    result = agent(f"Analyze the company: {company}")
    return str(result)
