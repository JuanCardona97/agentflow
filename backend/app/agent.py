"""
Support Agent — LangGraph-powered multi-step AI agent.

Implements a state machine that can:
- Route customer intents (order lookup, lead qualification, ticket creation)
- Call tools to fetch data and perform actions
- Maintain conversation memory across turns
- Stream intermediate steps for real-time UI feedback
"""

from typing import AsyncGenerator
from datetime import datetime, timezone

from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core import client_options
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.tools.order_lookup import order_lookup
from app.tools.lead_qualify import lead_qualify
from app.tools.ticket_create import ticket_create
from app.tools.knowledge_base import search_knowledge_base
from app.models import ChatResponse, ToolCall, AgentState
from app.state import ConversationState
from app.config import settings


SYSTEM_PROMPT = """You are AgentFlow, an AI customer support agent for an e-commerce company.

Your capabilities:
1. **Order lookup** — Find order status, tracking, and details by order ID or customer email
2. **Lead qualification** — Assess potential customers based on their needs and budget
3. **Ticket creation** — Create support tickets for issues that need human follow-up
4. **Knowledge base** — Search FAQs and documentation for product/policy answers

Rules:
- Always greet the customer warmly on first contact
- Ask clarifying questions when needed before using tools
- When looking up orders, ask for the order ID or email first
- For lead qualification, gather: name, company, use case, budget range, timeline
- Create tickets only when you cannot resolve the issue yourself
- Be concise but helpful — customers appreciate fast resolutions
- Always confirm actions before performing them (e.g., "I'll create a ticket for this")
- If you don't know something, say so honestly

Current date: {current_date}"""


class SupportAgent:
    """Multi-step support agent using LangGraph."""

    def __init__(self):
        self._tools = [
            order_lookup,
            lead_qualify,
            ticket_create,
            search_knowledge_base,
        ]

        self._llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            google_api_key=settings.GOOGLE_API_KEY,
            client_options=client_options.ClientOptions(
                api_endpoint="generativelanguage.googleapis.com",
            ),
            transport="rest",
        ).bind_tools(self._tools)

        self._memory = MemorySaver()
        self._graph = self._build_graph()
        self._states: dict[str, AgentState] = {}

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""

        graph = StateGraph(ConversationState)

        # Nodes
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", ToolNode(self._tools))

        # Edges
        graph.add_edge(START, "agent")
        graph.add_conditional_edges(
            "agent",
            self._should_use_tools,
            {"tools": "tools", END: END},
        )
        graph.add_edge("tools", "agent")

        return graph.compile(checkpointer=self._memory)

    async def _agent_node(self, state: ConversationState) -> dict:
        """The main agent reasoning node."""
        system_msg = SystemMessage(
            content=SYSTEM_PROMPT.format(
                current_date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            )
        )

        messages = [system_msg] + state["messages"]
        response = await self._llm.ainvoke(messages)

        return {"messages": [response]}

    def _should_use_tools(self, state: ConversationState) -> str:
        """Decide whether to route to tools or end the turn."""
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return END

    async def run(self, message: str, session_id: str) -> ChatResponse:
        """Run the agent for a single message and return the final response."""
        config = {"configurable": {"thread_id": session_id}}

        input_state = {"messages": [HumanMessage(content=message)]}

        # Run the graph to completion
        result = await self._graph.ainvoke(input_state, config=config)

        # Extract the final AI message
        ai_messages = [
            m for m in result["messages"]
            if isinstance(m, AIMessage) and m.content and not m.tool_calls
        ]
        final_message = ai_messages[-1] if ai_messages else None

        # Extract tool calls made during this turn
        tool_calls = []
        for m in result["messages"]:
            if isinstance(m, AIMessage) and m.tool_calls:
                for tc in m.tool_calls:
                    tool_calls.append(
                        ToolCall(
                            tool=tc["name"],
                            input=tc["args"],
                            output=None,
                        )
                    )

        # Update session state
        self._update_state(session_id, message, tool_calls)

        return ChatResponse(
            message=final_message.content if final_message else "I apologize, something went wrong. Could you try again?",
            tool_calls=tool_calls,
            session_id=session_id,
        )

    async def run_stream(
        self, message: str, session_id: str
    ) -> AsyncGenerator[dict, None]:
        """Stream agent steps in real-time via WebSocket."""
        config = {"configurable": {"thread_id": session_id}}
        input_state = {"messages": [HumanMessage(content=message)]}

        tool_calls = []

        async for event in self._graph.astream_events(
            input_state, config=config, version="v2"
        ):
            kind = event["event"]

            if kind == "on_chat_model_start":
                yield {"type": "thinking", "content": "Analyzing your message..."}

            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield {"type": "token", "content": chunk.content}

            elif kind == "on_tool_start":
                tool_name = event["name"]
                tool_input = event["data"].get("input", {})
                yield {
                    "type": "tool_start",
                    "tool": tool_name,
                    "input": tool_input,
                }

            elif kind == "on_tool_end":
                tool_name = event["name"]
                tool_output = event["data"].get("output", "")
                tool_calls.append(
                    ToolCall(tool=tool_name, input={}, output=str(tool_output))
                )
                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "output": str(tool_output)[:200],
                }

        self._update_state(session_id, message, tool_calls)
        yield {"type": "done"}

    def _update_state(
        self, session_id: str, message: str, tool_calls: list[ToolCall]
    ):
        """Track session state for the UI."""
        state = self._states.get(session_id, AgentState(session_id=session_id))
        state.message_count += 1
        state.tools_used.extend([tc.tool for tc in tool_calls])
        state.last_active = datetime.now(timezone.utc).isoformat()
        self._states[session_id] = state

    def get_state(self, session_id: str) -> AgentState | None:
        return self._states.get(session_id)

    def clear_session(self, session_id: str):
        self._states.pop(session_id, None)
