import { useCallback, useEffect, useRef, useState } from "react";
import { chatStream, createSession } from "./api";
import type { Message } from "./types";

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Akwaaba! I'm Kofi, your Ghana guide.\n\ntraditions | food | languages | music | history | travel | naming customs\n\nWhat would you like to explore?",
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    createSession().then(setSessionId);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async () => {
    const msg = input.trim();
    if (!msg || !sessionId || loading) return;
    setInput("");

    const userMsg: Message = { role: "user", content: msg };
    const assistantMsg: Message = { role: "assistant", content: "", streaming: true };
    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setLoading(true);

    try {
      let accumulated = "";
      for await (const token of chatStream(sessionId, msg)) {
        accumulated += token;
        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = { role: "assistant", content: accumulated, streaming: true };
          return copy;
        });
      }
      setMessages((prev) => {
        const copy = [...prev];
        copy[copy.length - 1] = { role: "assistant", content: accumulated, streaming: false };
        return copy;
      });
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : "Something went wrong";
      setMessages((prev) => {
        const copy = [...prev];
        copy[copy.length - 1] = { role: "assistant", content: `Error: ${err}`, streaming: false };
        return copy;
      });
    } finally {
      setLoading(false);
    }
  }, [input, sessionId, loading]);

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>Kofi</h1>
        <span className="subtitle">Your Ghana Cultural Guide</span>
      </header>

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="bubble">
              {m.content.split("\n").map((line, j) => (
                <p key={j}>{line || "\u00A0"}</p>
              ))}
              {m.streaming && <span className="cursor" />}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <form
        className="input-bar"
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me about Ghana..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
