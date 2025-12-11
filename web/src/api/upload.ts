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
  const response = await apiClient.post('/api/upload_image_from_url', { url })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to upload image from URL')
  }

  return await response.json()
}
