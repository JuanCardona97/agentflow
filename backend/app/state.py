"""
Conversation State — LangGraph state schema.

Defines the data that flows through the agent graph.
Uses the `add_messages` annotation so LangGraph automatically
appends new messages instead of overwriting.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ConversationState(TypedDict):
    """State that persists across the agent graph nodes."""

    messages: Annotated[list[BaseMessage], add_messages]
