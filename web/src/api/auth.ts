import { BASE_API_URL } from '../constants'
import i18n from '../i18n'
import { clearJaazApiKey } from './config'
import { apiClient } from '@/lib/api-client'
import { LLMConfig } from '@/types/types'

export interface AuthStatus {
  status: 'logged_out' | 'pending' | 'logged_in'
  is_logged_in: boolean
  user_info?: UserInfo
  tokenExpired?: boolean
}

export interface UserInfo {
  id: string
  username: string
  email: string
  image_url?: string
  provider?: string
  created_at?: string
  updated_at?: string
}

export interface DeviceAuthResponse {
  status: string
  code: string
  expires_at: string
  message: string
}

export interface DeviceAuthPollResponse {
  status: 'pending' | 'authorized' | 'expired' | 'error'
  message?: string
  token?: string
  user_info?: UserInfo
}

export interface ApiResponse {
  status: string
  message: string
}

export async function startDeviceAuth(): Promise<DeviceAuthResponse> {
  const response = await apiClient.post(`${BASE_API_URL}/api/device/auth`)

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const data = await response.json()

  // Open browser for user authentication using Electron API
  const authUrl = `${BASE_API_URL}/auth/device?code=${data.code}`

  // Check if we're in Electron environment
  if (window.electronAPI?.openBrowserUrl) {
    try {
      await window.electronAPI.openBrowserUrl(authUrl)
    } catch (error) {
      console.error('Failed to open browser via Electron:', error)
      // Fallback to window.open if Electron API fails
      window.open(authUrl, '_blank')
    }
  } else {
    // Fallback for web environment
    window.open(authUrl, '_blank')
  }

  return {
    status: data.status,
    code: data.code,
    expires_at: data.expires_at,
    message: i18n.t('common:auth.browserLoginMessage'),
  }
}

export async function pollDeviceAuth(deviceCode: string): Promise<DeviceAuthPollResponse> {
  const response = await apiClient.get(`${BASE_API_URL}/api/device/poll?code=${deviceCode}`)

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

export async function getAuthStatus(): Promise<AuthStatus> {
  // Get auth status from local storage
  const token = localStorage.getItem('jaaz_access_token')
  const userInfo = localStorage.getItem('jaaz_user_info')

  console.log('Getting auth status:', {
    hasToken: !!token,
    hasUserInfo: !!userInfo,
    userInfo: userInfo ? JSON.parse(userInfo) : null,
  })

  if (token && userInfo) {
    try {
      // Always try to refresh token when we have one
      const newToken = await refreshToken(token)

      // Save the new token
      localStorage.setItem('jaaz_access_token', newToken)
      console.log('Token refreshed successfully')

      const authStatus = {
        status: 'logged_in' as const,
        is_logged_in: true,
        user_info: JSON.parse(userInfo),
      }
      return authStatus
    } catch (error) {
      console.log('Token refresh failed:', error)

      // Only clear auth data if token is truly expired (401), not for network errors
      if (error instanceof Error && error.message === 'TOKEN_EXPIRED') {
        console.log('Token expired, clearing auth data')
        localStorage.removeItem('jaaz_access_token')
        localStorage.removeItem('jaaz_user_info')

        // Clear jaaz provider api_key
        try {
          await clearJaazApiKey()
        } catch (clearError) {
          console.error('Failed to clear jaaz api key:', clearError)
        }

        const loggedOutStatus = {
          status: 'logged_out' as const,
          is_logged_in: false,
          tokenExpired: true,
        }

        return loggedOutStatus
      } else {
        // Network error or other issues, keep user logged in with old token
        console.log('Network error during token refresh, keeping user logged in with existing token')
        const authStatus = {
          status: 'logged_in' as const,
          is_logged_in: true,
          user_info: JSON.parse(userInfo),
        }
        return authStatus
      }
    }
  }

  const loggedOutStatus = {
    status: 'logged_out' as const,
    is_logged_in: false,
  }
  console.log('Returning logged out status:', loggedOutStatus)
  return loggedOutStatus
}

export async function logout(): Promise<{ status: string; message: string }> {
  // Clear local storage
  localStorage.removeItem('jaaz_access_token')
  localStorage.removeItem('jaaz_user_info')

  // Clear jaaz provider api_key
  await clearJaazApiKey()

  return {
    status: 'success',
    message: i18n.t('common:auth.logoutSuccessMessage'),
  }
}

export async function getUserProfile(): Promise<UserInfo> {
  const userInfo = localStorage.getItem('jaaz_user_info')
  if (!userInfo) {
    throw new Error(i18n.t('common:auth.notLoggedIn'))
  }

  return JSON.parse(userInfo)
}

// Helper function to save auth data to local storage
export function saveAuthData(token: string, userInfo: UserInfo) {
  localStorage.setItem('jaaz_access_token', token)
  localStorage.setItem('jaaz_user_info', JSON.stringify(userInfo))
}

// Helper function to get access token
export function getAccessToken(): string | null {
  return localStorage.getItem('jaaz_access_token')
}

// Helper function to make authenticated API calls
export async function authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  // This function is now just a wrapper around apiClient.request, but keeping it for backward compatibility
  // though apiClient already handles the token from cookie, not localStorage 'jaaz_access_token'.
  // Wait, the user requirement is about 'ai_mark_token' from cookie.
  // The existing code uses 'jaaz_access_token' from localStorage.
  // I should respect the user requirement to use the new token logic.
  // But 'authenticatedFetch' explicitly adds 'Authorization' with Bearer token from localStorage.
  // If I replace fetch with apiClient.request, it will use the cookie token.
  // The user said "add Authorization Header... value is token from this function".
  // The function provided gets 'ai_mark_token' from cookie.
  // So I should prioritize that.

  // However, authenticatedFetch adds Bearer token.
  // apiClient adds the token directly (user code: return tokenCookie.split('=')[1].trim(); header: headers.set('Authorization', `${token}`))
  // The user didn't say "Bearer ". Just "value as the token".
  // But usually it is Bearer.
  // Let's look at the user request again: "值为我这个函数获取的token" (Value is the token obtained by this function).
  // It doesn't explicitly say "Bearer".
  // But wait, the existing code has `headers['Authorization'] = Bearer ${token}`.
  // If I change it to `apiClient.request`, it will use the cookie token without "Bearer" prefix if I strictly follow my `apiClient` implementation.
  // My `apiClient` implementation: `headers.set('Authorization', ${token})`.
  // If the backend expects "Bearer", this might break.
  // But the user strictly asked to use the token from the function as the value.
  // I will assume the user knows what they are doing or the token itself includes "Bearer" (unlikely for a cookie value usually, but possible).
  // OR, the backend just expects the raw token.
  // Given the explicit instruction, I will stick to what I implemented in apiClient.

  return apiClient.request(url, options)
}

// 刷新token
export async function refreshToken(currentToken: string) {
  const response = await apiClient.get(`${BASE_API_URL}/api/device/refresh-token`, {
    headers: {
      Authorization: `Bearer ${currentToken}`,
    },
  })

  if (response.status === 200) {
    const data = await response.json()
    return data.new_token
  } else if (response.status === 401) {
    // Token 真正过期，需要重新登录
    throw new Error('TOKEN_EXPIRED')
  } else {
    // 其他错误（网络错误、服务器错误等），不强制重新登录
    throw new Error(`NETWORK_ERROR: ${response.status}`)
  }
}

