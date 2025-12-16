import { apiClient, getToken } from '@/lib/api-client'
import { ToolInfo } from '@/api/model'
import { CanvasData, Message, Session } from '@/types/types'

export type ListCanvasesResponse = {
  id: string
  name: string
  description?: string
  thumbnail?: string
  created_at: string
}

export async function listCanvases(): Promise<ListCanvasesResponse[]> {
  const user_id = getToken()
  let response
  if (user_id) {
    response = await apiClient.get(`/api/canvas/by/user_id/${user_id}`)
  } else {
    response = await apiClient.get('/api/canvas/list')
  }

  if (!response.ok) {
    console.error('Failed to fetch canvases:', response.statusText)
    return []
  }
  return await response.json()
}

export async function createCanvas(data: {
  name: string
  canvas_id: string
  messages: Message[]
  session_id: string
  user_id: string | null
  text_model: {
    provider: string
    model: string
    url: string
  }
  tool_list: ToolInfo[]

  system_prompt: string
}): Promise<{ id: string }> {
  const response = await apiClient.post('/api/canvas/create', data)
  return await response.json()
}

export async function getCanvas(id: string): Promise<{ data: CanvasData; name: string; sessions: Session[] }> {
  const response = await apiClient.get(`/api/canvas/${id}`)
  return await response.json()
}

export async function saveCanvas(
  id: string,
  payload: {
    data: CanvasData
    thumbnail: string
  },
): Promise<void> {
  const response = await apiClient.post(`/api/canvas/${id}/save`, payload)
  return await response.json()
}

export async function renameCanvas(id: string, name: string): Promise<void> {
  const response = await apiClient.post(`/api/canvas/${id}/rename`, { name })
  return await response.json()
}

export async function deleteCanvas(id: string): Promise<void> {
  const response = await apiClient.delete(`/api/canvas/${id}/delete`)
  return await response.json()
}
