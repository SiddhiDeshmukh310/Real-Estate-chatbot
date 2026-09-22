import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import ChartSection from "./ChartSection";
import DataTable from "./DataTable";

const SUGGESTIONS = [
  "Analyze Wakad",
  "Analyze Aundh",
  "Compare Wakad and Akurdi",
  "Best Investment Area",
];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://sigmavalue-assignment.onrender.com";

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      sender: "assistant",
      text: "Hello! I am your **Real Estate Insights** assistant for Pune. Ask me to analyze localities like **Wakad**, **Aundh**, **Akurdi**, or **Ambegaon Budruk**, or compare areas for investment returns.",
      data: null,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const textToSend = queryText || input.trim();
    if (!textToSend || loading) return;

    const userMsg = { id: Date.now().toString(), sender: "user", text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput("");
    setLoading(true);

    try {
      const endpoint = `${API_BASE_URL}/api/analyze/`;
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: textToSend, session_id: "user_session_v2" }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const resData = await response.json();
      const botMsg = {
        id: (Date.now() + 1).toString(),
        sender: "assistant",
        text: resData.summary || "No response generated.",
        data: resData,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Backend fetch error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: "assistant",
          text: "Error connecting to backend service. Please check your network connection or verify the backend service status.",
          data: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="messages-list">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-row ${msg.sender}`}>
            <div className="message-avatar">
              {msg.sender === "user" ? <User size={18} /> : <Bot size={18} />}
            </div>
            <div className="message-content">
              <div className="response-card">
                <div className="summary-box">{msg.text}</div>
                {msg.data && msg.data.chart && (
                  <ChartSection chartData={msg.data.chart} areas={msg.data.areas} />
                )}
                {msg.data && msg.data.tables && (
                  <DataTable tables={msg.data.tables} />
                )}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message-row assistant">
            <div className="message-avatar"><Bot size={18} /></div>
            <div className="message-content" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Loader2 size={16} className="spin-loader" />
              <span>Analyzing Pune dataset...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-footer">
        <div className="suggestions-row">
          {SUGGESTIONS.map((sug, i) => (
            <button key={i} className="chip-btn" onClick={() => handleSend(sug)} disabled={loading}>
              {sug}
            </button>
          ))}
        </div>
        <form
          className="input-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <input
            className="chat-input"
            type="text"
            placeholder="Ask anything... (e.g. Compare Wakad and Akurdi)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button className="send-btn" type="submit" disabled={loading || !input.trim()}>
            <span>Send</span>
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}

