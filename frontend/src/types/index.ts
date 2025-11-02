export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  audioUrl?: string
  videoUrl?: string
}

export interface Correction {
  id: string
  type: 'grammar' | 'pronunciation' | 'vocabulary'
  original: string
  corrected: string
  explanation?: string
  severity: 'low' | 'medium' | 'high'
}

export interface WebSocketMessage {
  type: 'response' | 'transcription' | 'correction' | 'error'
  data: {
    text?: string
    audio?: string
    video_url?: string
    has_errors?: boolean
    corrections?: Correction[]
    better_expression?: string
    feedback?: string
    message?: string
  }
}

export interface Session {
  id: string
  userId: string
  startedAt: Date
  endedAt?: Date
  duration?: number
}

export interface Progress {
  totalSessions: number
  totalDuration: number
  totalCorrections: number
  grammarScore: number
  pronunciationScore: number
  vocabularyScore: number
}
