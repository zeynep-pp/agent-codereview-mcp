import asyncio
import os
import sys
try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False
from dotenv import load_dotenv
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from agents import set_tracing_disabled
from agents.exceptions import OutputGuardrailTripwireTriggered
from agent import JobFinderAgent
from react_code_review_agent import ReactCodeReviewAgent
from web_search_agent import WebSearchAgent
from agent_guardrails import bootcamp_relevance_guardrail
from mcp_config import MCPConfig
from logging_utils import LoggingUtils

load_dotenv()
set_tracing_disabled(True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is not None:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
else:
    raise ValueError("OPENAI_API_KEY is not set in the environment.")

VERBOSE = os.getenv("VERBOSE", "false").lower() in ["true", "1", "yes"]


def getch():
    """Get a single character from stdin."""
    if not HAS_TERMIOS or not sys.stdin.isatty():
        # Fallback to regular input for non-interactive or unsupported terminals
        return input()
    
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except (OSError, AttributeError):
        # Fallback if termios operations fail
        return input()


def display_agent_menu(console: Console):
    agents = [
        ("Job Finder Agent", "Find relevant job opportunities"),
        ("React Code Review Agent", "React code analysis and improvement assistant"),
        ("Web Search Agent", "Search the web for any information"),
        ("Quit", "Exit the application")
    ]

    selected = 0
    interactive_mode = HAS_TERMIOS and sys.stdin.isatty()

    while True:
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]Agent Assistant Platform[/bold cyan]",
            border_style="cyan"
        ))

        if interactive_mode:
            console.print(
                "\n[bold]Choose an agent (use ↑↓ arrows, Enter to select):[/bold]")

            for i, (name, description) in enumerate(agents):
                if i == selected:
                    console.print(
                        f"[bold green]→ {name}[/bold green] - [dim]{description}[/dim]")
                else:
                    console.print(
                        f"  [white]{name}[/white] - [dim]{description}[/dim]")

            console.print(
                "\n[dim]Use ↑/↓ arrows to navigate, Enter to select, 'q' to quit[/dim]")
        else:
            console.print("\n[bold]Choose an agent:[/bold]")
            for i, (name, description) in enumerate(agents):
                console.print(f"[yellow]{i+1}[/yellow]. {name} - [dim]{description}[/dim]")
            console.print("[yellow]q[/yellow]. Quit")
            console.print("\n[dim]Enter your choice (1, 2, or q):[/dim]")

        if interactive_mode:
            key = getch()
            
            if key == '\x1b':  # ESC sequence for arrow keys
                try:
                    key += getch()  # Get the next character
                    if key == '\x1b[':
                        key += getch()  # Get the third character
                        if key == '\x1b[A':  # Up arrow
                            selected = (selected - 1) % len(agents)
                        elif key == '\x1b[B':  # Down arrow
                            selected = (selected + 1) % len(agents)
                except:
                    pass
            elif key == '\r' or key == '\n':  # Enter
                if selected == 0:
                    return "1"
                elif selected == 1:
                    return "2"
                elif selected == 2:
                    return "3"
                else:
                    return "q"
            elif key.lower() == 'q':
                return "q"
        else:
            key = getch()
            # Non-interactive mode - handle text input
            if key.strip() == '1':
                return "1"
            elif key.strip() == '2':
                return "2"
            elif key.strip() == '3':
                return "3"
            elif key.strip().lower() == 'q':
                return "q"


async def main():
    logger = LoggingUtils(verbose=VERBOSE)
    console = logger.console

    try:
        choice = display_agent_menu(console)

        if choice == "q":
            console.print(
                "\n[bold yellow]Thanks for using Agent Assistant Platform! Goodbye! 👋[/bold yellow]")
            return

        if choice == "1":
            agent_name = "Job Finder Agent"
        elif choice == "2":
            agent_name = "React Code Review Agent"
        else:
            agent_name = "Web Search Agent"
        logger.print_welcome(agent_name)

        mcp_config = MCPConfig()
        logger.print_connecting()

        servers = await mcp_config.create_servers()
        
        if choice == "3":  # Web Search Agent
            async with servers["tavily"] as tavily_server:
                logger.print_connected()
                
                web_search_agent = WebSearchAgent(
                    mcp_servers=[tavily_server], verbose=VERBOSE)
                
                selected_agent = web_search_agent
                
                while True:
                    user_input = Prompt.ask(
                        f"\n[bold green]What can I help you with today? (type 'quit' to exit)[/bold green]")

                    if user_input.lower().strip() in ['quit', 'exit', 'q']:
                        logger.console.print(
                            "\n[bold yellow]Thanks for using Agent Assistant Platform! Goodbye! 👋[/bold yellow]")
                        break

                    await selected_agent.find_answer(user_input)
        else:
            async with servers["firecrawl"] as firecrawl_server, servers["react_code_review"] as react_code_review_server:
                logger.print_connected()

                job_finder = JobFinderAgent(
                    mcp_servers=[firecrawl_server], verbose=VERBOSE)

                react_code_review_agent = ReactCodeReviewAgent(
                    mcp_servers=[react_code_review_server],
                    verbose=VERBOSE,
                    output_guardrails=[bootcamp_relevance_guardrail]
                )

                selected_agent = job_finder if choice == "1" else react_code_review_agent

                while True:
                    user_input = Prompt.ask(
                        f"\n[bold green]What can I help you with today? (type 'quit' to exit)[/bold green]")

                    if user_input.lower().strip() in ['quit', 'exit', 'q']:
                        logger.console.print(
                            "\n[bold yellow]Thanks for using Agent Assistant Platform! Goodbye! 👋[/bold yellow]")
                        break

                    try:
                        await selected_agent.find_answer(user_input)
                    except OutputGuardrailTripwireTriggered as e:
                        logger.console.print("\n" + "━" * 60)
                        logger.console.print(
                            "⚠️  [bold red]GUARDRAIL ACTIVATED[/bold red] ⚠️", justify="center")
                        logger.console.print("━" * 60)
                        logger.console.print(
                            "\n[bold red]❌ This response is not related to React code review.[/bold red]")
                        logger.console.print("\n" + "━" * 60)
                        if VERBOSE:
                            logger.console.print(f"[dim]Debug info: {e}[/dim]")

    except ValueError as e:
        logger.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if "FIRECRAWL_API_KEY" in str(e):
            logger.console.print(
                "Please ensure FIRECRAWL_API_KEY is set in your .env file")
        elif "TAVILY_API_KEY" in str(e):
            logger.console.print(
                "Please ensure TAVILY_API_KEY is set in your .env file")
    except Exception as e:
        logger.console.print(
            f"[bold red]An unexpected error occurred: {str(e)}[/bold red]")


if __name__ == "__main__":
    asyncio.run(main())
