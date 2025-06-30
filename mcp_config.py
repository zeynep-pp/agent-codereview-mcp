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
        self.react_code_review_url = "https://react-code-review-mcp-main.vercel.app/sse"

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
        firecrawl_server = MCPServerSse(
            cache_tools_list=True,
            name="Firecrawl MCP",
            params=self.get_firecrawl_params(),
            client_session_timeout_seconds=60
        )

        react_code_review_server = MCPServerSse(
            cache_tools_list=True,
            name="React Code Review MCP",
            params=self.get_react_code_review_params(),
            client_session_timeout_seconds=15
        )

        tavily_server = MCPServerStdio(
            cache_tools_list=True,
            name="Tavily MCP(for web scrape and craw)",
            params=self.get_tavily_params(),
        )

        return {
            "firecrawl": firecrawl_server,
            "react_code_review": react_code_review_server,
            "tavily": tavily_server
        }
