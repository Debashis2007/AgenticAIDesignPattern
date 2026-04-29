import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

export default function Home() {
  const sessionId = useMemo(() => `session-${Date.now()}`, []);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I can help with timeline stress, conflicting immigration info, and drafting messages for recruiters/employers.",
      source: "system",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (event) => {
    event.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setLoading(true);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text, source: "ui" }]);

    const assistantIndex = messages.length + 1;
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", source: "streaming" },
    ]);

    try {
      const headers = { "Content-Type": "application/json" };
      if (API_KEY) headers["X-API-Key"] = API_KEY;

      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: "POST",
        headers,
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let streamed = "";

      const updateAssistantMessage = (content, source = "streaming") => {
        setMessages((prev) =>
          prev.map((m, idx) => (idx === assistantIndex ? { ...m, content, source } : m))
        );
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() || "";

        for (const eventBlock of events) {
          const lines = eventBlock
            .split("\n")
            .map((line) => line.trim())
            .filter(Boolean);
          const eventLine = lines.find((line) => line.startsWith("event:"));
          const dataLine = lines.find((line) => line.startsWith("data:"));
          if (!eventLine || !dataLine) continue;

          const eventName = eventLine.replace("event:", "").trim();
          const data = JSON.parse(dataLine.replace("data:", "").trim());

          if (eventName === "token") {
            streamed += data.chunk || "";
            updateAssistantMessage(streamed, "streaming");
          }

          if (eventName === "done") {
            updateAssistantMessage(data.reply || streamed, data.source || "llm");
          }
        }
      }

    } catch (error) {
      setMessages((prev) =>
        prev.map((m, idx) =>
          idx === assistantIndex
            ? {
                role: "assistant",
                content:
                  "I couldn't reach the backend. Please ensure FastAPI is running on port 8000.",
                source: "error",
              }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <h1>Immigration Chatbot</h1>

      <div className="chat-shell">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div className={`msg ${msg.role}`} key={`${msg.role}-${idx}`}>
              <div className="meta">
                {msg.role} · source: {msg.source}
              </div>
              <div className="content">
                {msg.role === "assistant" ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={sendMessage}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
          />
          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </form>

        <div className="hint">
          API: <code>{API_BASE}</code> · Session: <code>{sessionId}</code>
        </div>
      </div>
    </main>
  );
}
