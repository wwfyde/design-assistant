import { Message, Model } from '@/types/types'
import { apiClient } from '@/lib/api-client'
import { ToolInfo } from './model'

export const getChatSession = async (sessionId: string) => {
  const response = await apiClient.get(`/api/chat_session/${sessionId}`)
  const data = await response.json()
  return data as Message[]
}

export const sendMessages = async (payload: {
  sessionId: string
  canvasId: string
  newMessages: Message[]
  textModel: Model
  toolList: ToolInfo[]
  systemPrompt: string | null
}) => {
  const response = await apiClient.post('/api/chat', {
    messages: payload.newMessages,
    canvas_id: payload.canvasId,
    session_id: payload.sessionId,
    text_model: payload.textModel,
    tool_list: payload.toolList,
    system_prompt: payload.systemPrompt,
  })
  const data = await response.json()
  return data as Message[]
}

export const cancelChat = async (sessionId: string) => {
  const response = await apiClient.post(`/api/cancel/${sessionId}`)
  return await response.json()
}
