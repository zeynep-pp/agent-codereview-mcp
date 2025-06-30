from agents import Agent, Runner
from agents.mcp import MCPServerSse, MCPServer
from logging_utils import LoggingUtils
from typing import List, Optional, Sequence


class ReactCodeReviewAgent:
    def __init__(self, mcp_servers: Sequence[MCPServer], verbose: bool = False, output_guardrails: Optional[List] = None):
        self.mcp_servers = mcp_servers
        self.verbose = verbose
        self.logger = LoggingUtils(verbose)

        self.agent = Agent(
            name="React Code Review Assistant",
            instructions="""You are a helpful React code review assistant that helps developers analyze and improve their React code.
            You can review React components, suggest improvements, identify best practices, and help with code quality.
            """,
            mcp_servers=list(mcp_servers),
            model="gpt-4o",
            output_guardrails=output_guardrails or [],
        )

    async def find_answer(self, user_input: str):
        prompt = f"""The user is looking for: {user_input}
        """

        self.logger.print_searching("React Code Review Assistant")

        result = Runner.run_streamed(
            starting_agent=self.agent, input=prompt, max_turns=10)

        await self.logger.stream_results(result)

        self.logger.print_complete()
