'use client';

import { useState, useEffect } from 'react';
import ChatInterface from '@/components/ChatInterface';
import { Loader2 } from 'lucide-react'; // Assuming lucide-react is installed and available

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Initializing AI Loan Assistant...</h2>
        <p className="text-gray-400">Setting up your secure connection</p>
      </div>
    </div>
  );
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate app initialization
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <ChatInterface />
  );
}