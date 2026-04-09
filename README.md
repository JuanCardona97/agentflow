# AgentFlow

**AI-powered customer support agent with multi-step reasoning, tool use, and conversation memory**

AgentFlow is an autonomous support agent built with LangGraph that can look up orders, qualify leads, create support tickets, and search a knowledge base — all through natural conversation. It decides which tools to use, chains multiple actions together, and maintains context across the entire session.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-0.3-green)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What makes this different

Most "AI chatbot" demos are thin wrappers around an LLM API. AgentFlow is a **production-grade agent** that:

- **Reasons before acting** — Decides which tool to call (or whether to ask a clarifying question first)
- **Chains multiple tools** — Can look up an order, find it's delayed, and automatically create a ticket
- **Maintains memory** — Remembers everything said earlier in the conversation using LangGraph checkpointing
- **Shows its work** — The UI displays each tool call as a visible step, building trust with the user
- **Streams in real-time** — WebSocket support for token-by-token streaming and live tool status

---

## Architecture

```
                    ┌──────────────────────────────────────┐
                    │        LangGraph State Machine        │
                    │                                      │
  User message ───> │  ┌─────────┐    ┌────────────────┐  │
                    │  │  Agent   │───>│  Tool Router    │  │
                    │  │  (LLM)   │    │                  │  │
                    │  │          │<───│  Should I use    │  │
                    │  └─────────┘    │  a tool? Which?  │  │
                    │       ^         └───────┬──────────┘  │
                    │       │                 │              │
                    │       │         ┌───────v──────────┐  │
                    │       └─────────│   Tool Node      │  │
                    │                 │                    │  │
                    │                 │  ┌──────────────┐ │  │
                    │                 │  │ order_lookup  │ │  │
                    │                 │  │ lead_qualify  │ │  │
                    │                 │  │ ticket_create │ │  │
                    │                 │  │ knowledge_base│ │  │
                    │                 │  └──────────────┘ │  │
                    │                 └───────────────────┘  │
                    │                                      │
                    │  MemorySaver (conversation history)   │
                    └──────────────────────────────────────┘
```

**The agent loop:**

1. User sends a message
2. **Agent node** receives message + full conversation history
3. LLM decides: respond directly OR call one or more tools
4. If tools needed → **Tool node** executes them and returns results
5. Agent node receives tool results → may call more tools or generate final response
6. Response + tool call metadata sent back to the UI

---

## Tools

| Tool | Description | Example trigger |
|------|------------|-----------------|
| `order_lookup` | Find orders by ID or email, returns status/tracking/items | "Where is my order ORD-1001?" |
| `lead_qualify` | Score prospects (0-100) based on budget, timeline, company | "We need 200 units by Q3" |
| `ticket_create` | Escalate to human support with auto-assignment and priority | "I want to speak with a manager" |
| `search_knowledge_base` | Search FAQs, policies, product docs | "What's your return policy?" |

Each tool is a standalone LangChain `@tool` function that can be swapped out for real integrations (Shopify, Salesforce, Zendesk, etc.) without changing the agent logic.

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- A [Google Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone and configure

```bash
git clone https://github.com/JuanCardona97/agentflow.git
cd agentflow
cp .env.example .env
# Add your Google Gemini API key to .env
```

### 2. Run

```bash
docker compose up --build
```

### 3. Open

- **Chat UI:** http://localhost:3000
- **API docs:** http://localhost:8000/docs

---

## Try these conversations

**Order tracking:**
> "Hi, I'd like to check on my order"
> "The order ID is ORD-1001"
> "When will it arrive?"

**Lead qualification:**
> "I'm interested in your products for my company"
> "We're a team of 200 at TechCorp, looking for bulk headphones"
> "Our budget is around $30k and we need them by next quarter"

**Multi-step resolution:**
> "I received a damaged product from order ORD-1003"
> (Agent looks up order → searches return policy → creates ticket)

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message, get agent response + tool calls |
| `WebSocket` | `/ws/{session_id}` | Real-time streaming with tool status updates |
| `GET` | `/sessions/{id}/state` | Get session activity stats |
| `DELETE` | `/sessions/{id}` | Clear session memory |

### Chat request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is order ORD-1001?", "session_id": "user-123"}'
```

### Response

```json
{
  "message": "Your order ORD-1001 has been shipped via UPS! The tracking number is 1Z999AA10123456784, and the estimated delivery date is April 2, 2026.",
  "tool_calls": [
    {
      "tool": "order_lookup",
      "input": {"order_id": "ORD-1001"},
      "output": null
    }
  ],
  "session_id": "user-123"
}
```

---

## Project Structure

```
agentflow/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI server + WebSocket endpoint
│   │   ├── agent.py          # LangGraph agent with state machine
│   │   ├── state.py          # Conversation state schema
│   │   ├── models.py         # Pydantic request/response models
│   │   ├── config.py         # Environment configuration
│   │   └── tools/
│   │       ├── order_lookup.py       # Order search by ID/email
│   │       ├── lead_qualify.py       # Lead scoring engine
│   │       ├── ticket_create.py      # Support ticket creation
│   │       └── knowledge_base.py     # FAQ/policy search
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main layout
│   │   ├── App.css               # Styles
│   │   ├── main.jsx              # Entry point
│   │   └── components/
│   │       ├── ChatAgent.jsx     # Chat UI with tool step display
│   │       └── AgentStatus.jsx   # Session activity sidebar
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Agent Framework** | LangGraph | State machine with cycles, built-in memory, streaming |
| **LLM** | Gemini 2.5 Flash | Fast tool-calling, low cost, large context window |
| **Backend** | FastAPI | Async, WebSocket support, auto-generated docs |
| **Frontend** | React 19 + Vite | Lightweight, fast refresh |
| **Memory** | LangGraph MemorySaver | Conversation persistence across turns |

---

## Extending with real integrations

Each tool is a standalone function. To connect to real services, replace the simulated data:

```python
# Before (simulated)
order = _ORDERS.get(order_id)

# After (real Shopify integration)
import shopify
order = shopify.Order.find(order_id)
```

Common integrations:
- **Orders:** Shopify, WooCommerce, Stripe
- **CRM:** Salesforce, HubSpot, Pipedrive
- **Helpdesk:** Zendesk, Freshdesk, Intercom
- **Knowledge base:** Notion, Confluence, or RAG with vector DB

---

## Roadmap

- [ ] Streaming responses via WebSocket in the UI
- [ ] Human-in-the-loop: agent asks for approval before critical actions
- [ ] Multi-agent: route to specialized agents (billing, shipping, tech)
- [ ] Analytics dashboard: resolution rate, avg handle time, CSAT
- [ ] One-click deploy to Railway/Render
- [ ] Voice support with Vapi integration

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with LangGraph, FastAPI, and React
