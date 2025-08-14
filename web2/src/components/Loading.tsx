interface LoadingProps {
  text?: string;
}

export function Loading({ text = 'Loading' }: LoadingProps) {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <div className="inline-flex items-center space-x-2">
          <div className="animate-pulse text-terminal-green font-mono">
            [{Array.from({ length: 10 }, (_, i) => (
              <span
                key={i}
                className="inline-block animate-pulse"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                ═
              </span>
            ))}]
          </div>
        </div>
        <p className="mt-2 text-sm text-terminal-gray font-mono">
          {text}<span className="cursor"></span>
        </p>
      </div>
    </div>
  );
}

export function LoadingSpinner() {
  return (
    <div className="flex justify-center p-4">
      <div className="border border-terminal-green rounded-full w-8 h-8 animate-spin border-t-transparent"></div>
    </div>
  );
}