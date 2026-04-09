"""
AgentFlow — AI Customer Support Agent API
Multi-step agent that qualifies leads, looks up orders, and resolves tickets.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models import ChatRequest, ChatResponse, AgentState
from app.agent import SupportAgent
from app.config import settings


agent: SupportAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    agent = SupportAgent()
    yield
    agent = None


app = FastAPI(
    title="AgentFlow",
    description="AI-powered customer support agent with multi-step reasoning",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "ready", "model": settings.LLM_MODEL}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the support agent and get a response."""
    result = await agent.run(
        message=request.message,
        session_id=request.session_id,
    )
    return result


@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """Real-time WebSocket connection for streaming agent responses."""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")

            # Stream agent steps back to the client
            async for step in agent.run_stream(
                message=message,
                session_id=session_id,
            ):
                await websocket.send_json(step)

    except WebSocketDisconnect:
        agent.clear_session(session_id)


@app.get("/sessions/{session_id}/state", response_model=AgentState)
async def get_session_state(session_id: str):
    """Get the current state of a conversation session."""
    state = agent.get_state(session_id)
    if not state:
        return AgentState(session_id=session_id)
    return state


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear a conversation session and its memory."""
    agent.clear_session(session_id)
    return {"message": f"Session {session_id} cleared"}
