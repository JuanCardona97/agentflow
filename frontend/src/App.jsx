import { useState, useCallback, useEffect } from "react";
import ChatAgent from "./components/ChatAgent";
import AgentStatus from "./components/AgentStatus";
import "./App.css";

export default function App() {
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [toolCalls, setToolCalls] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const closeSidebar = useCallback(() => setSidebarOpen(false), []);


  useEffect(() => {
    const handleKey = (e) => { if (e.key === "Escape") closeSidebar(); };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [closeSidebar]);

  useEffect(() => {
    document.body.style.overflow = sidebarOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [sidebarOpen]);

  return (
    <div className="app">
      {/* Sidebar backdrop (mobile) */}
      <div
        className={`sidebar-backdrop ${sidebarOpen ? "active" : ""}`}
        onClick={closeSidebar}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar-brand">
          <div className="brand-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <div>
            <h1 className="brand-name">AgentFlow</h1>
            <p className="brand-sub">AI Support Agent</p>
          </div>
          <button className="sidebar-close" onClick={closeSidebar} aria-label="Close sidebar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <nav className="sidebar-nav">
          <span className="nav-label">Capabilities</span>
          <div className="nav-item">
            <span className="nav-icon nav-icon--orders">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="22" height="18" rx="3"/><path d="M1 9h22"/></svg>
            </span>
            <div>
              <strong>Order Lookup</strong>
              <small>Track orders by ID or email</small>
            </div>
          </div>
          <div className="nav-item">
            <span className="nav-icon nav-icon--leads">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </span>
            <div>
              <strong>Lead Qualification</strong>
              <small>Score &amp; categorize prospects</small>
            </div>
          </div>
          <div className="nav-item">
            <span className="nav-icon nav-icon--tickets">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
            </span>
            <div>
              <strong>Ticket Creation</strong>
              <small>Escalate to human support</small>
            </div>
          </div>
          <div className="nav-item">
            <span className="nav-icon nav-icon--kb">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </span>
            <div>
              <strong>Knowledge Base</strong>
              <small>Search FAQs &amp; policies</small>
            </div>
          </div>
        </nav>

        <AgentStatus toolCalls={toolCalls} />

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>System online</span>
        </div>
      </aside>

      {/* Mobile top bar — outside main to avoid flex layout shifts */}
      <header className="topbar">
        <button className="topbar-menu" onClick={() => setSidebarOpen(true)} aria-label="Open menu">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="4" y1="6" x2="20" y2="6" />
            <line x1="4" y1="12" x2="16" y2="12" />
            <line x1="4" y1="18" x2="12" y2="18" />
          </svg>
        </button>
        <div className="topbar-brand">
          <div className="brand-mark brand-mark--sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <span className="topbar-title">AgentFlow</span>
        </div>
      </header>

      {/* Main content */}
      <main className="main">
        <div className="main-grid-overlay" />
        <ChatAgent key={sessionId} sessionId={sessionId} onToolCalls={setToolCalls} />
      </main>
    </div>
  );
}
