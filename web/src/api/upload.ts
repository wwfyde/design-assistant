import { apiClient } from '@/lib/api-client'
import { compressImageFile } from '@/utils/imageUtils'

export async function uploadImage(
  file: File,
): Promise<{ file_id: string; width: number; height: number; url: string }> {
  // Compress image before upload
  const compressedFile = await compressImageFile(file)

  const formData = new FormData()
  formData.append('file', compressedFile)
  const response = await apiClient.post('/api/upload_image', formData)
  return await response.json()
}

export async function uploadImageFromUrl(
  url: string,
): Promise<{ file_id: string; width: number; height: number; url: string }> {
  try {
    // 1. Try to fetch the image from client side to avoid backend network issues
    // Use simple fetch to avoid auth headers being sent to external URLs (CORS)
    const res = await fetch(url)

    if (!res.ok) {
      throw new Error(`Failed to fetch image: ${res.statusText}`)
    }

    const blob = await res.blob()

    // Convert to base64
    const base64_image = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })

    // Send base64 to backend
    const response = await apiClient.post('/api/upload_image_from_url', { base64_image })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to upload image from URL')
    }

    return await response.json()
  } catch (error) {
    console.warn('Client-side fetch failed (likely CORS), falling back to server-side fetch:', error)

    // 2. Fallback: Failover to server-side fetch
    const response = await apiClient.post('/api/upload_image_from_url', { url })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to upload image from URL (fallback)')
    }

    return await response.json()
  }
}
