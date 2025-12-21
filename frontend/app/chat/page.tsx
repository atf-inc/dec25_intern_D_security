"use client";

import { useState, useRef, useEffect } from "react";
import { 
  MessageSquare, 
  Send, 
  Bot,
  User,
  Loader2,
  Trash2,
  Sparkles
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { ChatMessage } from "@/types";

const SUGGESTED_QUESTIONS = [
  "What is SQL injection and how do I prevent it?",
  "Explain the OWASP Top 10 vulnerabilities",
  "How do I securely store passwords?",
  "What are common security issues in Python code?",
  "How to prevent XSS attacks in React?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function handleSend(message?: string) {
    const text = message || input.trim();
    if (!text || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }

  function handleClearChat() {
    setMessages([]);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-blue-500" />
            Security Chat
          </h1>
          <p className="text-slate-500 mt-1">
            Ask questions about security best practices
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="btn-ghost text-red-500 hover:text-red-600 flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Clear Chat
          </button>
        )}
      </div>

      {/* Chat Container */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <EmptyState onSuggestionClick={handleSend} />
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {loading && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="flex items-center gap-2 text-slate-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Thinking...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </CardContent>

        {/* Input Area */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-700">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about security practices..."
                rows={1}
                className="input resize-none pr-12"
                style={{ minHeight: "44px", maxHeight: "120px" }}
              />
            </div>
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              className="btn-primary h-11 px-4"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </Card>
    </div>
  );
}

function EmptyState({ onSuggestionClick }: { onSuggestionClick: (q: string) => void }) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center">
      <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-6">
        <Sparkles className="w-8 h-8 text-blue-600 dark:text-blue-400" />
      </div>
      <h2 className="text-xl font-semibold mb-2">Security AI Assistant</h2>
      <p className="text-slate-500 mb-8 max-w-md">
        Ask me anything about security vulnerabilities, best practices, 
        or how to fix security issues in your code.
      </p>
      
      <div className="w-full max-w-lg">
        <p className="text-sm text-slate-500 mb-3">Try asking:</p>
        <div className="space-y-2">
          {SUGGESTED_QUESTIONS.map((question, idx) => (
            <button
              key={idx}
              onClick={() => onSuggestionClick(question)}
              className="w-full p-3 text-left rounded-lg border border-slate-200 dark:border-slate-700
                         hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  
  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
        ${isUser 
          ? "bg-green-100 dark:bg-green-900/30" 
          : "bg-blue-100 dark:bg-blue-900/30"}
      `}>
        {isUser ? (
          <User className="w-4 h-4 text-green-600 dark:text-green-400" />
        ) : (
          <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        )}
      </div>
      
      <div className={`
        max-w-[80%] p-4 rounded-2xl
        ${isUser 
          ? "bg-green-600 text-white rounded-tr-none" 
          : "bg-slate-100 dark:bg-slate-800 rounded-tl-none"}
      `}>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          {message.content.split('\n').map((line, i) => (
            <p key={i} className={`${i > 0 ? 'mt-2' : ''} ${isUser ? 'text-white' : ''}`}>
              {line}
            </p>
          ))}
        </div>
        <p className={`text-xs mt-2 ${isUser ? 'text-green-200' : 'text-slate-400'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}

