import { BASE_API_URL } from '../constants'
import { apiClient } from '@/lib/api-client'

export interface BalanceResponse {
  balance: string
}

export async function getBalance(): Promise<BalanceResponse> {
  const response = await apiClient.get(`${BASE_API_URL}/api/billing/getBalance`)

  if (!response.ok) {
    throw new Error(`Failed to fetch balance: ${response.status}`)
  }

  return await response.json()
}
