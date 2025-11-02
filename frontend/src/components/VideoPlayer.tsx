'use client'

import { useEffect, useRef, useState } from 'react'

interface VideoPlayerProps {
  videoUrl?: string
  isLoading?: boolean
}

export default function VideoPlayer({ videoUrl, isLoading }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (videoUrl && videoRef.current) {
      videoRef.current.src = videoUrl
      videoRef.current.play().catch(err => {
        console.error('Failed to play video:', err)
        setError(true)
      })
    }
  }, [videoUrl])

  return (
    <div className="relative w-full aspect-video bg-gray-900 rounded-lg overflow-hidden shadow-2xl">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <div className="text-white text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p>비디오 생성 중...</p>
          </div>
        </div>
      )}

      {!videoUrl && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-blue-900 to-purple-900">
          <div className="text-white text-center p-8">
            <div className="text-6xl mb-4">👋</div>
            <h3 className="text-2xl font-semibold mb-2">안녕하세요!</h3>
            <p className="text-gray-300">대화를 시작할 준비가 되었습니다</p>
          </div>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <div className="text-white text-center">
            <p>비디오를 불러올 수 없습니다</p>
          </div>
        </div>
      )}

      <video
        ref={videoRef}
        className={`w-full h-full object-cover ${!videoUrl && 'hidden'}`}
        autoPlay
        playsInline
      />
    </div>
  )
}
