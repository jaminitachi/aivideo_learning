'use client'

import { Message } from '@/types'
import { useRef, useEffect } from 'react'

interface ChatInterfaceProps {
  messages: Message[]
}

export default function ChatInterface({ messages }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="h-96 overflow-y-auto bg-white rounded-lg shadow-lg p-4 space-y-4">
      {messages.length === 0 && (
        <div className="text-center text-gray-400 py-8">
          <p>대화 내역이 여기에 표시됩니다</p>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70%] rounded-lg px-4 py-2 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-900'
            }`}
          >
            <p className="text-sm font-medium mb-1">
              {message.role === 'user' ? '나' : 'AI 선생님'}
            </p>
            <p>{message.content}</p>
            <p className="text-xs mt-1 opacity-70">
              {new Date(message.timestamp).toLocaleTimeString('ko-KR')}
            </p>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}
