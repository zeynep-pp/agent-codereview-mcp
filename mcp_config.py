import os
from agents.mcp import MCPServerSse, MCPServerStdio, MCPServerSseParams, MCPServerStdioParams
from typing import Dict


class MCPConfig:
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.firecrawl_api_key:
            raise ValueError(
                "FIRECRAWL_API_KEY environment variable is not set")

        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            raise ValueError(
                "TAVILY_API_KEY environment variable is not set")

        self.firecrawl_url = f"https://mcp.firecrawl.dev/{self.firecrawl_api_key}/sse"
        #self.react_code_review_url = "https://react-code-review-mcp-main.vercel.app/sse"
        self.react_code_review_url = "http://localhost:3000/sse"

    def get_firecrawl_params(self):
        return MCPServerSseParams(url=self.firecrawl_url)

    def get_react_code_review_params(self):
        return MCPServerSseParams(url=self.react_code_review_url)

    def get_tavily_params(self):
        return MCPServerStdioParams(
            command="npx",
            args=["-y", "tavily-mcp@0.2.4"],
            env={"TAVILY_API_KEY": str(self.tavily_api_key)}
        )

    async def create_servers(self):
        servers = {}
        
        # Always include Firecrawl and Tavily servers
        try:
            firecrawl_server = MCPServerSse(
                cache_tools_list=True,
                name="Firecrawl MCP",
                params=self.get_firecrawl_params(),
                client_session_timeout_seconds=60
            )
            servers["firecrawl"] = firecrawl_server
        except Exception as e:
            print(f"Warning: Failed to create Firecrawl server: {e}")

        try:
            tavily_server = MCPServerStdio(
                cache_tools_list=True,
                name="Tavily MCP(for web scrape and craw)",
                params=self.get_tavily_params(),
            )
            servers["tavily"] = tavily_server
        except Exception as e:
            print(f"Warning: Failed to create Tavily server: {e}")

        # Try to include React Code Review server, but don't fail if it's not available
        try:
            react_code_review_server = MCPServerSse(
                cache_tools_list=True,
                name="React Code Review MCP",
                params=self.get_react_code_review_params(),
                client_session_timeout_seconds=15
            )
            servers["react_code_review"] = react_code_review_server
            print("✓ React Code Review MCP server configured")
        except Exception as e:
            print(f"Warning: React Code Review MCP server not available: {e}")
            print("The app will continue without React code review functionality.")

        return servers
