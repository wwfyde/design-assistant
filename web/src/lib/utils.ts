import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function dataURLToFile(dataURL: string, filename: string) {
  const arr = dataURL.split(',')
  const mime = arr[0].match(/:(.*?);/)?.[1]
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new File([u8arr], filename, { type: mime })
}

export function filterMessageContent(content: string) {
  return content
    .replace(/<aspect_ratio>.*?<\/aspect_ratio>/g, '')
    .replace(/<image_size>.*?<\/image_size>/g, '')
    .replace(/<quantity>.*?<\/quantity>/g, '')
    .replace(/<input_images[\s\S]*?<\/input_images>/g, '')
    .trim()
}
