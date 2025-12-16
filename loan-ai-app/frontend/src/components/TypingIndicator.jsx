function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 px-4 py-3 bg-dark-800 rounded-lg w-fit">
      <div className="flex space-x-1">
        <div 
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot"
          style={{ animationDelay: '0ms' }}
        />
        <div 
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot"
          style={{ animationDelay: '200ms' }}
        />
        <div 
          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot"
          style={{ animationDelay: '400ms' }}
        />
      </div>
      <span className="text-sm text-gray-400 ml-2">AI is typing...</span>
    </div>
  )
}

export default TypingIndicator


