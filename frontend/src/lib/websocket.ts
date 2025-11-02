import { WebSocketMessage } from '@/types'

export class WebSocketClient {
  private ws: WebSocket | null = null
  private sessionId: string
  private messageHandlers: ((message: WebSocketMessage) => void)[] = []
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second
  private isIntentionallyClosed = false

  constructor(sessionId: string) {
    this.sessionId = sessionId
  }

  connect() {
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/conversation/${this.sessionId}`

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.reconnectDelay = 1000
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.messageHandlers.forEach(handler => handler(message))
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected', event.code, event.reason)

        // Only attempt reconnection if not intentionally closed
        if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

          setTimeout(() => {
            this.connect()
          }, this.reconnectDelay)

          // Exponential backoff
          this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000)
        } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error('Max reconnection attempts reached')
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }

  onMessage(handler: (message: WebSocketMessage) => void) {
    this.messageHandlers.push(handler)
  }

  sendAudio(audioBase64: string) {
    if (!this.ws) {
      console.error('WebSocket is not initialized')
      return
    }

    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'audio',
        data: { audio: audioBase64 }
      }))
    } else {
      console.warn('WebSocket is not open. Current state:', this.ws.readyState)
    }
  }

  sendText(text: string) {
    if (!this.ws) {
      console.error('WebSocket is not initialized')
      return
    }

    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'text',
        data: { text }
      }))
    } else {
      console.warn('WebSocket is not open. Current state:', this.ws.readyState)
    }
  }

  disconnect() {
    this.isIntentionallyClosed = true
    if (this.ws) {
      // Only send stop message if connection is fully open
      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'control',
          data: { command: 'stop' }
        }))
      }
      this.ws.close()
    }
  }
}
