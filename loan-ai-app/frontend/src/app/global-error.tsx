'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center bg-gray-900 text-white font-sans">
          <h2 className="text-2xl font-bold text-red-500 mb-4">Critical System Error</h2>
          <p className="text-red-200 mb-4">The application encountered a critical error in the root layout.</p>
          {error.digest && (
            <p className="text-gray-500 text-xs mb-6 font-mono bg-black/30 p-2 rounded">
              Error ID: {error.digest}
            </p>
          )}
          <button
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            onClick={() => reset()}
          >
            Reload Application
          </button>
        </div>
      </body>
    </html>
  );
}