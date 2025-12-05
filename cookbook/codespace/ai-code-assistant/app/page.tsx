'use client';

import { useState, useRef, useEffect } from 'react';
import { CodeBlock } from '../components/CodeBlock';
import { LoadingSpinner } from '../components/LoadingSpinner';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Execution {
  code: string;
  output: string;
  error?: string;
  timestamp: number;
  logs?: string[];
  chartUrls?: string[];
}

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [streamingLogs, setStreamingLogs] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate sessionId only on client side to avoid hydration mismatch
  useEffect(() => {
    setSessionId(generateSessionId());
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, executions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !sessionId) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setStreamingLogs([]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error('Request failed');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader');

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === 'status' || data.type === 'log') {
                setStreamingLogs((prev) => [...prev, data.message]);
              } else if (data.type === 'execution') {
                setExecutions((prev) => [...prev, data.execution]);
              } else if (data.type === 'done') {
                setMessages((prev) => [...prev, data.message]);
                // Don't add executions here - they were already added via 'execution' events
              } else if (data.type === 'error') {
                throw new Error(data.error);
              }
            } catch (parseError: any) {
              console.error('Failed to parse SSE data:', line, parseError);
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.message}`,
        },
      ]);
    } finally {
      setIsLoading(false);
      setStreamingLogs([]);
    }
  };

  const getExecutionForMessage = (index: number): Execution | undefined => {
    // Match execution to message by timing
    const message = messages[index];
    if (message.role !== 'user') return undefined;

    return executions.find((exec) => {
      const messageIndex = messages.indexOf(message);
      return messageIndex * 2 <= executions.indexOf(exec);
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-950">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                🤖 AI Code Assistant
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-gray-400">Powered by</span>
                <span className="px-3 py-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-bold rounded-full shadow-lg">
                  ⚡ AgentBay
                </span>
              </div>
            </div>
            {messages.length > 0 && (
              <button
                onClick={() => {
                  setMessages([]);
                  setExecutions([]);
                  setInput('');
                }}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                <span>🔄</span>
                <span className="hidden sm:inline">New Chat</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-6 pb-32">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">💻</div>
            <h2 className="text-2xl font-semibold text-gray-200 mb-2">
              Welcome to AI Code Assistant
            </h2>
            <p className="text-gray-400 mb-6">
              Ask me to write code, analyze data, or create visualizations!
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
              <button
                onClick={() =>
                  setInput('Analyze 1000 random data points: calculate mean, median, std, and create a histogram with normal distribution overlay')
                }
                className="p-4 bg-gray-800 rounded-lg shadow hover:shadow-md hover:bg-gray-700 transition-all text-left border border-gray-700"
              >
                <div className="font-semibold text-gray-100 mb-1">
                  📊 Statistical Analysis
                </div>
                <div className="text-sm text-gray-400">
                  Advanced data analysis with visualization
                </div>
              </button>
              <button
                onClick={() =>
                  setInput('Create a professional 2x2 dashboard: sales trends (line), revenue by region (bar), profit margins (area), and customer segments (pie chart)')
                }
                className="p-4 bg-gray-800 rounded-lg shadow hover:shadow-md hover:bg-gray-700 transition-all text-left border border-gray-700"
              >
                <div className="font-semibold text-gray-100 mb-1">
                  📈 Business Dashboard
                </div>
                <div className="text-sm text-gray-400">
                  Multi-panel executive dashboard
                </div>
              </button>
              <button
                onClick={() =>
                  setInput('Generate a sine and cosine wave comparison: plot both functions from 0 to 2π with different colors, add grid, legend, and labels')
                }
                className="p-4 bg-gray-800 rounded-lg shadow hover:shadow-md hover:bg-gray-700 transition-all text-left border border-gray-700"
              >
                <div className="font-semibold text-gray-100 mb-1">
                  🌊 Wave Functions
                </div>
                <div className="text-sm text-gray-400">
                  Trigonometric function visualization
                </div>
              </button>
              <button
                onClick={() =>
                  setInput('Create a scatter plot with 200 random points showing correlation between two variables, add regression line and R² value')
                }
                className="p-4 bg-gray-800 rounded-lg shadow hover:shadow-md hover:bg-gray-700 transition-all text-left border border-gray-700"
              >
                <div className="font-semibold text-gray-100 mb-1">
                  📉 Correlation Analysis
                </div>
                <div className="text-sm text-gray-400">
                  Scatter plot with regression
                </div>
              </button>
              <button
                onClick={() =>
                  setInput('Generate a heatmap showing correlation matrix for 5 random variables with 100 data points each')
                }
                className="p-4 bg-gray-800 rounded-lg shadow hover:shadow-md hover:bg-gray-700 transition-all text-left border border-gray-700"
              >
                <div className="font-semibold text-gray-100 mb-1">
                  🔥 Heatmap Visualization
                </div>
                <div className="text-sm text-gray-400">
                  Correlation matrix heatmap
                </div>
              </button>
              <button
                onClick={() =>
                  setInput('Create a box plot comparing distributions of 4 different datasets with 50 samples each, show outliers')
                }
                className="p-4 bg-gray-800 rounded-lg shadow hover:shadow-md hover:bg-gray-700 transition-all text-left border border-gray-700"
              >
                <div className="font-semibold text-gray-100 mb-1">
                  📦 Distribution Comparison
                </div>
                <div className="text-sm text-gray-400">
                  Box plot with multiple datasets
                </div>
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message, index) => (
              <div key={index}>
                {/* Message */}
                <div
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-3xl rounded-2xl px-6 py-4 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800 text-gray-100 shadow-sm border border-gray-700'
                    }`}
                  >
                    <div className="text-sm font-semibold mb-1 opacity-75">
                      {message.role === 'user' ? 'You' : 'AI Assistant'}
                    </div>
                    <div className="whitespace-pre-wrap">
                      {message.role === 'assistant'
                        ? message.content.replace(/!\[.*?\]\(.*?\)/g, '').trim()
                        : message.content}
                    </div>
                  </div>
                </div>

                {/* Code Execution Results */}
                {message.role === 'assistant' && (() => {
                  // For each assistant message, find its corresponding execution
                  // Assistant messages come after user messages, so count how many assistant messages came before this one
                  const assistantIndex = messages.slice(0, index + 1).filter(m => m.role === 'assistant').length - 1;
                  const execution = executions[assistantIndex];

                  return execution ? (
                    <div className="mt-4">
                      <CodeBlock execution={execution} />
                    </div>
                  ) : null;
                })()}
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 rounded-2xl px-6 py-4 shadow-sm border border-gray-700">
                  <LoadingSpinner logs={streamingLogs} />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input Form */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 shadow-lg">
        <form onSubmit={handleSubmit} className="max-w-5xl mx-auto p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me to write code, analyze data, or create visualizations..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 rounded-xl border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-600 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? '⏳' : '➤'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
