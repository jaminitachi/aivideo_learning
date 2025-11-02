'use client'

import { Correction } from '@/types'

interface CorrectionFeedbackProps {
  corrections: Correction[]
  betterExpression?: string
  feedback?: string
}

export default function CorrectionFeedback({
  corrections,
  betterExpression,
  feedback
}: CorrectionFeedbackProps) {
  if (corrections.length === 0 && !feedback) {
    return null
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low':
        return 'text-blue-600 bg-blue-50 border-blue-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getTypeEmoji = (type: string) => {
    switch (type) {
      case 'grammar':
        return '📝'
      case 'pronunciation':
        return '🗣️'
      case 'vocabulary':
        return '📚'
      default:
        return '✨'
    }
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-900">피드백</h3>

      {corrections.map((correction, index) => (
        <div
          key={index}
          className={`p-4 rounded-lg border ${getSeverityColor(correction.severity)}`}
        >
          <div className="flex items-start space-x-2">
            <span className="text-2xl">{getTypeEmoji(correction.type)}</span>
            <div className="flex-1">
              <p className="font-medium capitalize mb-2">
                {correction.type === 'grammar' && '문법'}
                {correction.type === 'pronunciation' && '발음'}
                {correction.type === 'vocabulary' && '어휘'}
              </p>
              <div className="space-y-1 text-sm">
                <p>
                  <span className="line-through opacity-70">{correction.original}</span>
                  {' → '}
                  <span className="font-semibold">{correction.corrected}</span>
                </p>
                {correction.explanation && (
                  <p className="text-xs opacity-80">{correction.explanation}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}

      {betterExpression && (
        <div className="p-4 rounded-lg bg-green-50 border border-green-200">
          <p className="text-sm font-medium text-green-900 mb-2">
            💡 더 자연스러운 표현
          </p>
          <p className="text-green-700">{betterExpression}</p>
        </div>
      )}

      {feedback && (
        <div className="p-4 rounded-lg bg-purple-50 border border-purple-200">
          <p className="text-sm text-purple-900">{feedback}</p>
        </div>
      )}
    </div>
  )
}
