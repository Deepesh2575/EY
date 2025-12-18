'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900 flex items-center justify-center text-white">
        <div className="text-center p-8 bg-dark-700 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold mb-4">Something went wrong globally!</h2>
          <p className="text-red-400 mb-6">{error.message}</p>
          <button
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-md transition-colors"
            onClick={
              () => reset()
            }
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  )
}
