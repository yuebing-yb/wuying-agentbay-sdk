interface LoadingSpinnerProps {
  logs?: string[];
}

export function LoadingSpinner({ logs = [] }: LoadingSpinnerProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
        <span className="text-sm text-gray-300 font-medium">Processing...</span>
      </div>

      {logs.length > 0 && (
        <div className="mt-3 space-y-1 bg-gray-900 rounded-lg p-3 border border-gray-700">
          <div className="text-xs font-semibold text-gray-300 mb-2">⚡ Execution Progress</div>
          {logs.map((log, index) => (
            <div key={index} className="text-xs text-gray-400 font-mono animate-fade-in">
              {log}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
