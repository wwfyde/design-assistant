import { apiClient } from '@/lib/api-client'
import { Message } from '@/types/types'

export const sendMagicGenerate = async (payload: {
  sessionId: string
  canvasId: string
  newMessages: Message[]
  systemPrompt: string | null
}) => {
  const response = await apiClient.post('/api/magic', {
    messages: payload.newMessages,
    canvas_id: payload.canvasId,
    session_id: payload.sessionId,
    system_prompt: payload.systemPrompt,
  })
  const data = await response.json()
  return data as Message[]
}

export const cancelMagicGenerate = async (sessionId: string) => {
  const response = await apiClient.post(`/api/magic/cancel/${sessionId}`)
  return await response.json()
}
