import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: "greeting",
      role: "assistant",
      content: "Hi! Craving something? Ask me which restaurant has it, or about any restaurant on FoodHub.",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages, open]);

  async function send(e) {
    e.preventDefault();
    const message = input.trim();
    if (!message || busy) return;
    setInput("");
    const nextMessages = [...messages, { id: crypto.randomUUID(), role: "user", content: message }];
    setMessages(nextMessages);
    setBusy(true);
    try {
      const data = await api("/chat/", {
        method: "POST",
        // skip the canned greeting; send prior turns as history
        body: {
          message,
          history: nextMessages.slice(1, -1).map(({ role, content }) => ({ role, content })),
        },
      });
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "assistant", content: `Sorry, something went wrong: ${err.message}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <strong>FoodHub Assistant</strong>
            <button aria-label="Close chat" onClick={() => setOpen(false)}>×</button>
          </div>
          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m) => (
              <div key={m.id} className={`chat-bubble ${m.role}`}>{m.content}</div>
            ))}
            {busy && <div className="chat-bubble assistant muted">Thinking…</div>}
          </div>
          <form className="chat-input" onSubmit={send}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. Who has pad thai?"
              maxLength={500}
            />
            <button type="submit" disabled={busy || !input.trim()}>Send</button>
          </form>
        </div>
      )}
      <button
        className="chat-toggle"
        aria-label={open ? "Close chat" : "Chat with FoodHub assistant"}
        onClick={() => setOpen((o) => !o)}
      >
        {open ? "×" : "💬"}
      </button>
    </div>
  );
}
