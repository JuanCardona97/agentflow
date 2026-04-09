"""
API Models — Pydantic schemas for requests and responses.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Customer message",
        examples=["Where is my order ORD-1001?"],
    )
    session_id: str = Field(
        default="default",
        description="Conversation session ID for memory persistence",
    )


class ToolCall(BaseModel):
    """Record of a tool the agent called during processing."""

    tool: str = Field(description="Name of the tool called")
    input: dict = Field(default_factory=dict, description="Tool input parameters")
    output: str | None = Field(default=None, description="Tool output (truncated)")


class ChatResponse(BaseModel):
    """Response body for the /chat endpoint."""

    message: str = Field(description="Agent's response message")
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Tools called during this turn",
    )
    session_id: str = Field(description="Session ID for this conversation")


class AgentState(BaseModel):
    """Current state of a conversation session."""

    session_id: str
    message_count: int = 0
    tools_used: list[str] = Field(default_factory=list)
    last_active: str | None = None
