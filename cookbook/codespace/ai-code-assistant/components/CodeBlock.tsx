interface Execution {
  code: string;
  output: string;
  error?: string;
  timestamp: number;
  logs?: string[];
  chartUrls?: string[];
}

interface CodeBlockProps {
  execution: Execution;
}

export function CodeBlock({ execution }: CodeBlockProps) {
  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg">
      {/* Execution Logs - AgentBay Process */}
      {execution.logs && execution.logs.length > 0 && (
        <div className="border-b border-gray-700">
          <div className="px-4 py-2 bg-indigo-900/50 flex items-center">
            <span className="text-xs font-semibold text-indigo-300">
              ⚡ AgentBay Execution Process
            </span>
          </div>
          <div className="px-4 py-3 bg-gray-800/50">
            {execution.logs.map((log, index) => (
              <div key={index} className="text-xs text-gray-300 font-mono mb-1">
                {log}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Code Section */}
      <div className="border-b border-gray-700">
        <div className="px-4 py-2 bg-gray-800 flex items-center justify-between">
          <span className="text-xs font-semibold text-gray-300">
            🐍 Python Code
          </span>
          <button
            onClick={() => {
              navigator.clipboard.writeText(execution.code);
            }}
            className="text-xs text-gray-400 hover:text-white transition-colors"
          >
            📋 Copy
          </button>
        </div>
        <pre className="px-4 py-3 overflow-x-auto text-sm">
          <code className="text-green-400 font-mono">{execution.code}</code>
        </pre>
      </div>

      {/* Output Section */}
      {execution.output && (
        <div className={execution.error ? 'border-b border-red-900' : ''}>
          <div
            className={`px-4 py-2 flex items-center ${
              execution.error ? 'bg-red-900/30' : 'bg-gray-800'
            }`}
          >
            <span className="text-xs font-semibold text-gray-300">
              {execution.error ? '❌ Error' : '✅ Output'}
            </span>
          </div>
          <pre
            className={`px-4 py-3 overflow-x-auto text-sm ${
              execution.error ? 'text-red-400' : 'text-blue-400'
            } font-mono`}
          >
            {execution.output}
          </pre>
        </div>
      )}

      {/* Charts Section */}
      {execution.chartUrls && execution.chartUrls.length > 0 && (
        <div className="border-t border-gray-700">
          <div className="px-4 py-2 bg-gray-800 flex items-center">
            <span className="text-xs font-semibold text-gray-300">
              📊 Generated Chart{execution.chartUrls.length > 1 ? 's' : ''}
            </span>
          </div>
          <div className="px-4 py-4 bg-gray-800/50 space-y-4">
            {execution.chartUrls.map((url, index) => (
              <img
                key={index}
                src={url}
                alt={`Generated chart ${index + 1}`}
                className="max-w-full h-auto rounded border border-gray-600"
              />
            ))}
          </div>
        </div>
      )}

      {/* Timestamp */}
      <div className="px-4 py-2 bg-gray-800 border-t border-gray-700">
        <span className="text-xs text-gray-500">
          Executed at {new Date(execution.timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}
