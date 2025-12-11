import { apiClient } from '@/lib/api-client'
import { Prompt } from '@/types/prompt'

export async function listPrompts(offset: number = 0, limit: number = 20): Promise<Prompt[]> {
  const params = new URLSearchParams({
    offset: offset.toString(),
    limit: limit.toString(),
  })
  const response = await apiClient.get(`/api/prompts?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Failed to fetch prompts')
  }
  return await response.json()
}
