import { useState, useRef, useEffect, useCallback } from "react";
import Markdown from "react-markdown";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_URL = API_URL.replace(/^http/, "ws");

const SUGGESTIONS = [
  { text: "Where is my order ORD-1001?" },
  { text: "What's your return policy?" },
  { text: "I'd like to report a problem" },
  { text: "I'm interested in bulk pricing" },
];

export default function ChatAgent({ sessionId, onToolCalls }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [activeTools, setActiveTools] = useState([]);
  const bottomRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef("");
  const toolsRef = useRef([]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText, activeTools]);

  // Connect WebSocket on mount
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/ws/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => console.log("WebSocket connected");
    ws.onclose = () => console.log("WebSocket disconnected");
    ws.onerror = () => console.error("WebSocket error");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "token":
          streamRef.current += data.content;
          setStreamingText(streamRef.current);
          break;

        case "tool_start":
          streamRef.current = "";
          setStreamingText("");
          toolsRef.current = [...toolsRef.current, { tool: data.tool, status: "running" }];
          setActiveTools(toolsRef.current);
          break;

        case "tool_end":
          toolsRef.current = toolsRef.current.map((t) =>
            t.tool === data.tool ? { ...t, status: "completed" } : t
          );
          setActiveTools(toolsRef.current);
          onToolCalls((prev) => [
            ...prev,
            { tool: data.tool, input: {}, output: data.output },
          ]);
          break;

        case "thinking":
          break;

        case "done": {
          const finalTools = toolsRef.current;
          const finalText = streamRef.current;
          const newMsgs = [];

          if (finalTools.length > 0) {
            newMsgs.push({ role: "tools", tools: finalTools.map((t) => ({ tool: t.tool, status: t.status })) });
          }
          if (finalText.trim()) {
            newMsgs.push({ role: "assistant", content: finalText });
          }

          if (newMsgs.length > 0) {
            setMessages((msgs) => [...msgs, ...newMsgs]);
          }

          streamRef.current = "";
          toolsRef.current = [];
          setStreamingText("");
          setActiveTools([]);
          setLoading(false);
          break;
        }
      }
    };

    return () => {
      ws.close();
    };
  }, [sessionId, onToolCalls]);

  const sendMessage = useCallback(
    (text) => {
      const question = typeof text === "string" ? text : input.trim();
      if (!question || loading) return;

      setInput("");
      setMessages((prev) => [...prev, { role: "user", content: question }]);
      setLoading(true);
      setStreamingText("");
      setActiveTools([]);

      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ message: question }));
      } else {
        // Fallback to REST if WebSocket is not connected
        fetchFallback(question);
      }
    },
    [input, loading]
  );

  const fetchFallback = useCallback(
    async (question) => {
      try {
        const res = await fetch(`${API_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: question, session_id: sessionId }),
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Agent error");
        }

        const data = await res.json();

        if (data.tool_calls?.length > 0) {
          setMessages((prev) => [
            ...prev,
            { role: "tools", tools: data.tool_calls },
          ]);
          onToolCalls((prev) => [...prev, ...data.tool_calls]);
        }

        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.message },
        ]);
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          { role: "error", content: err.message },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [sessionId, onToolCalls]
  );

  const handleSubmit = useCallback(
    (e) => {
      e?.preventDefault();
      sendMessage();
    },
    [sendMessage]
  );

  const handleSuggestion = useCallback(
    (text) => {
      sendMessage(text);
    },
    [sendMessage]
  );

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.length === 0 && !loading && (
          <div className="empty-state">
            <div className="empty-state-orb">
              <div className="empty-state-orb-ring" />
              <div className="empty-state-orb-ring" />
              <div className="empty-state-orb-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
            </div>
            <h2>How can I help you?</h2>
            <p>I can track orders, answer questions from our knowledge base, qualify leads, and create support tickets.</p>
            <div className="suggestions">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="suggestion"
                  onClick={() => handleSuggestion(s.text)}
                  style={{ animationDelay: `${0.55 + i * 0.08}s` }}
                >
                  {s.text}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => {
          if (msg.role === "tools") {
            return (
              <div key={i} className="tool-steps">
                {msg.tools.map((tc, j) => (
                  <div key={j} className="tool-step">
                    <span className={`tool-badge ${tc.tool}`}>
                      {formatToolName(tc.tool)}
                    </span>
                    <span className="tool-status">completed</span>
                  </div>
                ))}
              </div>
            );
          }

          return (
            <div key={i} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.role === "assistant" ? (
                  <Markdown>{msg.content}</Markdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          );
        })}

        {/* Live tool calls while streaming */}
        {activeTools.length > 0 && (
          <div className="tool-steps">
            {activeTools.map((tc, j) => (
              <div key={j} className="tool-step">
                <span className={`tool-badge ${tc.tool}`}>
                  {formatToolName(tc.tool)}
                </span>
                <span className={`tool-status ${tc.status === "running" ? "tool-status--running" : ""}`}>
                  {tc.status === "running" ? "running..." : "completed"}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Streaming text as it arrives */}
        {streamingText && (
          <div className="message assistant">
            <div className="message-content">
              <Markdown>{streamingText}</Markdown>
              <span className="streaming-cursor" />
            </div>
          </div>
        )}

        {loading && !streamingText && activeTools.length === 0 && (
          <div className="message assistant">
            <div className="typing-indicator">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <div className="input-wrap">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
          />
          <div className="input-glow" />
        </div>
        <button type="submit" disabled={loading || !input.trim()}>
          <span className="btn-text">Send</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
    </div>
  );
}

function formatToolName(name) {
  const names = {
    order_lookup: "Order lookup",
    lead_qualify: "Lead qualification",
    ticket_create: "Ticket created",
    search_knowledge_base: "Knowledge base search",
  };
  return names[name] || name;
}
