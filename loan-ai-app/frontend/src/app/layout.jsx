'use client'

import './globals.css'
import { Briefcase } from 'lucide-react'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-dark-900 text-white">
        <header className="border-b border-dark-700 bg-dark-800 sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-6 h-6 text-primary-500" />
              <h1 className="text-xl font-bold">AI Loan Officer</h1>
            </div>
            <div className="flex items-center gap-4">
              <a href="/dashboard" className="text-sm text-primary-400 hover:text-primary-300 font-medium">Dashboard</a>
              <p className="text-sm text-dark-600">Instant loan approval powered by AI</p>
            </div>
          </div>
        </header>
        <main className="min-h-screen bg-dark-900">
          {children}
        </main>
      </body>
    </html>
  )
}
