'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const startLearning = async () => {
    setIsLoading(true)

    try {
      // For demo, we'll create or get a test user first
      // In production, this would come from authentication
      let userId = localStorage.getItem('test_user_id')

      if (!userId) {
        // Create a new test user
        const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: 'Test User',
            email: `test-${Date.now()}@example.com`,
            password: 'testpass123'
          }),
        })

        if (userResponse.ok) {
          const user = await userResponse.json()
          userId = user.id
          localStorage.setItem('test_user_id', userId)
        } else {
          console.error('Failed to create user:', await userResponse.text())
          alert('사용자 생성에 실패했습니다. 콘솔을 확인해주세요.')
          setIsLoading(false)
          return
        }
      }

      // Create a new session
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/conversations/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      })

      if (response.ok) {
        const session = await response.json()
        router.push(`/learning/${session.id}`)
      } else {
        console.error('Failed to create session:', await response.text())
        alert('세션 생성에 실패했습니다. 콘솔을 확인해주세요.')
      }
    } catch (error) {
      console.error('Failed to start learning:', error)
      alert('오류가 발생했습니다: ' + error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-6">
          VideoEngAI
        </h1>

        <p className="text-2xl text-gray-600 mb-4">
          AI 비디오 아바타와 함께하는 영어 학습
        </p>

        <p className="text-lg text-gray-500 mb-12">
          실시간 대화로 영어를 배우고, 즉각적인 피드백으로 실력을 향상시키세요
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <div className="text-4xl mb-4">🎥</div>
            <h3 className="text-xl font-semibold mb-2">실시간 비디오</h3>
            <p className="text-gray-600">
              AI 아바타와 자연스러운 대화를 나누세요
            </p>
          </div>

          <div className="p-6 bg-white rounded-lg shadow-md">
            <div className="text-4xl mb-4">✅</div>
            <h3 className="text-xl font-semibold mb-2">즉각적인 교정</h3>
            <p className="text-gray-600">
              문법과 발음을 실시간으로 교정받으세요
            </p>
          </div>

          <div className="p-6 bg-white rounded-lg shadow-md">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">진도 추적</h3>
            <p className="text-gray-600">
              학습 진행 상황을 체계적으로 관리하세요
            </p>
          </div>
        </div>

        <button
          onClick={startLearning}
          disabled={isLoading}
          className="px-8 py-4 bg-blue-600 text-white text-xl font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
        >
          {isLoading ? '시작하는 중...' : '지금 시작하기'}
        </button>

        <p className="mt-6 text-sm text-gray-500">
          무료로 체험해보세요 · 가입 필요 없음
        </p>
      </div>
    </main>
  )
}
