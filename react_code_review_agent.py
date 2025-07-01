from agents import Agent, Runner
from agents.mcp import MCPServerSse, MCPServer
from logging_utils import LoggingUtils
from typing import List, Optional, Sequence


class ReactCodeReviewAgent:
    def __init__(self, mcp_servers: Sequence[MCPServer], verbose: bool = False, output_guardrails: Optional[List] = None):
        self.mcp_servers = mcp_servers
        self.verbose = verbose
        self.logger = LoggingUtils(verbose)

        # Filter out None servers and create instructions based on available servers
        available_servers = [server for server in mcp_servers if server is not None]
        
        # Check if React Code Review server is available
        react_server_available = any(
            hasattr(server, 'name') and 'React Code Review' in str(server.name) 
            for server in available_servers
        )
        
        if react_server_available:
            instructions = """You are a helpful React code review assistant that helps developers analyze and improve their React code.
            You can review React components, suggest improvements, identify best practices, and help with code quality.
            Use the react-nextjs-code-review tool to analyze React and Next.js code when users ask for code reviews.
            """
        else:
            instructions = """You are a helpful React code review assistant that helps developers with React development.
            Note: The specialized React code review tool is currently unavailable, but you can still provide general guidance on React best practices,
            code structure, and development patterns based on your knowledge.
            """
            print("⚠️  React Code Review MCP tool not available - using general assistance mode")

        self.agent = Agent(
            name="React Code Review Assistant",
            instructions=instructions,
            mcp_servers=available_servers,
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
