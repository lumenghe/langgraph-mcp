import asyncio
import logging
from typing import Annotated, Literal, Sequence, TypedDict

from langchain.chat_models import init_chat_model
from langchain.schema.messages import HumanMessage
from langchain_core.messages import BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    number_of_steps: int


class MathAgent:
    """A math agent that uses multiple MCP servers for different mathematical operations."""

    def __init__(self, model_name: str = "google_vertexai:gemini-2.0-flash", temperature: float = 0):
        self.model = init_chat_model(model_name, temperature=temperature)
        self.client = None
        self.tools = None
        self.graph = None

    async def initialize(self) -> None:
        """Initialize the MCP client and build the graph."""
        logger.info("Initializing MCP client and tools...")

        # Configure MCP servers
        server_config = {
            "elementary_math": {
                "command": "python",
                "args": ["elementary_math_server.py"],
                "transport": "stdio",
            },
            "exponentiation_math": {
                "command": "python",
                "args": ["exponentiation_math_server.py"],
                "transport": "stdio",
            },
        }

        self.client = MultiServerMCPClient(server_config)

        try:
            # Load all MCP tools
            self.tools = await self.client.get_tools()
            logger.info(f"Successfully loaded {len(self.tools)} tools from MCP servers")

            # Log available tools
            for tool in self.tools:
                logger.info(f"Available tool: {tool.name}")

            # Build the LangGraph
            self._build_graph()

        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""

        def call_model(state: MessagesState) -> dict:
            """Call the model with bound tools."""
            try:
                response = self.model.bind_tools(self.tools).invoke(state["messages"])
                return {"messages": response}
            except Exception as e:
                logger.error(f"Error calling model: {e}")
                raise

        def should_continue(state: MessagesState) -> Literal["continue", "end"]:
            """Determine whether to continue with tool calls or end."""
            messages = state["messages"]
            last_message = messages[-1]

            # Check if the last message has tool calls
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                logger.info(f"Continuing with {len(last_message.tool_calls)} tool call(s)")
                return "continue"

            logger.info("No tool calls found, ending conversation")
            return "end"

        # Build the graph
        builder = StateGraph(MessagesState)
        builder.add_node("call_model", call_model)
        builder.add_node("tools", ToolNode(self.tools))

        builder.set_entry_point("call_model")
        builder.add_conditional_edges(
            "call_model",
            should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        builder.add_edge("tools", "call_model")

        self.graph = builder.compile()
        logger.info("Graph built successfully")

    async def process_query(self, query: str, previous_messages: list = None) -> dict:
        """Process a single query with optional conversation context."""
        if not self.graph:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        # Prepare messages
        if previous_messages:
            messages = previous_messages + [HumanMessage(content=query)]
        else:
            messages = [HumanMessage(content=query)]

        logger.info(f"Processing query: {query}")

        try:
            result = await self.graph.ainvoke({"messages": messages})
            return result
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def print_messages(self, messages: list, start_index: int = 0) -> None:
        """Print messages starting from a specific index."""
        for msg in messages[start_index:]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"{msg.type.upper()}: Making tool calls: {[tc['name'] for tc in msg.tool_calls]}")
            else:
                print(f"{msg.type.upper()}: {msg.content}")

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.client:
            logger.info("Cleaning up MCP client...")
            # Add any cleanup logic here if needed


async def demonstrate_math_agent():
    """Demonstrate the math agent with multi-MCP servers."""
    agent = MathAgent()

    try:
        # Initialize the agent
        await agent.initialize()

        print("=" * 60)
        print("🧮 LangGraph Multi-MCP Math Agent Demo")
        print("=" * 60)

        # Query 1: Basic arithmetic
        query1 = "What's (3 + 5) × 12?"
        print(f"\n🔍 Query 1: {query1}")
        print("-" * 40)

        result1 = await agent.process_query(query1)
        agent.print_messages(result1["messages"])

        # Query 2: Continue conversation with exponentiation
        query2 = "Now I want to get the square of that result"
        print(f"\n🔍 Query 2: {query2}")
        print("-" * 40)

        result2 = await agent.process_query(query2, result1["messages"])

        # Print only new messages
        new_message_count = len(result1["messages"])
        agent.print_messages(result2["messages"], new_message_count)

        # Query 3: More complex operation
        query3 = "What's 2^8 + 15?"
        print(f"\n🔍 Query 3: {query3}")
        print("-" * 40)

        result3 = await agent.process_query(query3)
        agent.print_messages(result3["messages"])

        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise

    finally:
        # Clean up
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(demonstrate_math_agent())
