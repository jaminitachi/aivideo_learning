'use client'

import { useState } from 'react'
import { RefreshCw } from 'lucide-react'

interface Phrase {
  id: string
  english: string
  korean: string
  category: string
}

interface RepeatPracticeProps {
  onPracticePhrase: (phrase: string) => void
}

export default function RepeatPractice({ onPracticePhrase }: RepeatPracticeProps) {
  const [currentPhrase, setCurrentPhrase] = useState<Phrase | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const practicePhrases: Phrase[] = [
    {
      id: '1',
      english: "I'm good, thanks for asking!",
      korean: "잘 지내요, 물어봐 주셔서 감사해요!",
      category: "greeting"
    },
    {
      id: '2',
      english: "What brings you here today?",
      korean: "오늘 여기는 무슨 일로 오셨어요?",
      category: "conversation"
    },
    {
      id: '3',
      english: "That sounds interesting!",
      korean: "재미있겠네요!",
      category: "response"
    },
    {
      id: '4',
      english: "Could you explain that again?",
      korean: "다시 한 번 설명해 주실 수 있나요?",
      category: "clarification"
    },
    {
      id: '5',
      english: "I really appreciate your help.",
      korean: "도움 주셔서 정말 감사합니다.",
      category: "gratitude"
    }
  ]

  const getRandomPhrase = () => {
    const randomIndex = Math.floor(Math.random() * practicePhrases.length)
    setCurrentPhrase(practicePhrases[randomIndex])
  }

  const practice = () => {
    if (currentPhrase) {
      onPracticePhrase(currentPhrase.english)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">반복 연습</h3>
        <button
          onClick={getRandomPhrase}
          disabled={isLoading}
          className="flex items-center space-x-2 px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg transition-colors"
        >
          <RefreshCw size={16} />
          <span>새로운 문장</span>
        </button>
      </div>

      {!currentPhrase ? (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">연습할 문장을 선택하세요</p>
          <button
            onClick={getRandomPhrase}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            시작하기
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-600 mb-2">영어</p>
            <p className="text-lg font-semibold text-gray-900">{currentPhrase.english}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600 mb-2">한국어 뜻</p>
            <p className="text-gray-900">{currentPhrase.korean}</p>
          </div>

          <button
            onClick={practice}
            className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
          >
            이 문장으로 연습하기
          </button>
        </div>
      )}

      <div className="pt-4 border-t border-gray-200">
        <p className="text-sm text-gray-600">
          💡 <strong>팁:</strong> 문장을 여러 번 반복해서 연습하면 자연스럽게 말할 수 있게 됩니다!
        </p>
      </div>
    </div>
  )
}
