'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to the console (visible in browser dev tools)
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center">
      <h2 className="text-2xl font-bold text-red-500 mb-4">Something went wrong!</h2>
      <div className="bg-gray-900/50 p-4 rounded border border-red-500/30 mb-6 max-w-2xl overflow-auto">
        <p className="text-red-200 font-mono text-sm">{error.message}</p>
        {error.digest && <p className="text-gray-500 text-xs mt-2">Error Digest: {error.digest}</p>}
      </div>
      <button
        className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        onClick={() => reset()}
      >
        Try again
      </button>
    </div>
  );
}