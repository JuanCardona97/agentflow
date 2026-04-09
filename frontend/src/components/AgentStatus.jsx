export default function AgentStatus({ toolCalls }) {
  if (toolCalls.length === 0) return null;

  const counts = {};
  toolCalls.forEach((tc) => {
    counts[tc.tool] = (counts[tc.tool] || 0) + 1;
  });

  const toolLabels = {
    order_lookup: "Order lookups",
    lead_qualify: "Leads qualified",
    ticket_create: "Tickets created",
    search_knowledge_base: "KB searches",
  };

  return (
    <div className="agent-status">
      <h3>Session activity</h3>
      <div className="stats">
        {Object.entries(counts).map(([tool, count]) => (
          <div key={tool} className="stat-row">
            <span className="stat-label">
              {toolLabels[tool] || tool}
            </span>
            <span className="stat-value">{count}</span>
          </div>
        ))}
        <div className="stat-row total">
          <span className="stat-label">Total actions</span>
          <span className="stat-value">{toolCalls.length}</span>
        </div>
      </div>
    </div>
  );
}
