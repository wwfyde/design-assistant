import { saveCanvas } from '@/api/canvas'
import { useCanvas } from '@/contexts/canvas'
import useDebounce from '@/hooks/use-debounce'
import { useTheme } from '@/hooks/use-theme'
import { eventBus } from '@/lib/event'
import * as ISocket from '@/types/socket'
import { CanvasData } from '@/types/types'
import { convertToExcalidrawElements, Excalidraw } from '@excalidraw/excalidraw'
import {
  ExcalidrawEmbeddableElement,
  ExcalidrawImageElement,
  NonDeleted,
  OrderedExcalidrawElement,
  Theme,
} from '@excalidraw/excalidraw/element/types'
import '@excalidraw/excalidraw/index.css'
import { AppState, BinaryFileData, BinaryFiles, ExcalidrawInitialDataState } from '@excalidraw/excalidraw/types'
import { nanoid } from 'nanoid'
import { useCallback, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { VideoElement } from './VideoElement'

import '@/assets/style/canvas.css'
import { apiClient } from '@/lib/api-client.ts'

type LastImagePosition = {
  x: number
  y: number
  width: number
  height: number
  col: number // col index
}

type CanvasExcaliProps = {
  canvasId: string
  initialData?: ExcalidrawInitialDataState
}

const CanvasExcali: React.FC<CanvasExcaliProps> = ({ canvasId, initialData }) => {
  const { excalidrawAPI, setExcalidrawAPI } = useCanvas()

  const { i18n } = useTranslation()

  // Immediate handler for UI updates (no debounce)
  const handleSelectionChange = (elements: Readonly<OrderedExcalidrawElement[]>, appState: AppState) => {
    if (!appState) return

    // Check if any selected element is embeddable type
    const selectedElements = elements.filter((element) => appState.selectedElementIds[element.id])
    const hasEmbeddableSelected = selectedElements.some((element) => element.type === 'embeddable')

    // Toggle CSS class to hide/show left panel immediately
    const excalidrawContainer = document.querySelector('.excalidraw')
    if (excalidrawContainer) {
      if (hasEmbeddableSelected) {
        excalidrawContainer.classList.add('hide-left-panel')
      } else {
        excalidrawContainer.classList.remove('hide-left-panel')
      }
    }
  }

  // Debounced handler for saving (performance optimization)
  const handleSave = useDebounce(
    (elements: Readonly<OrderedExcalidrawElement[]>, appState: AppState, files: BinaryFiles) => {
      if (elements.length === 0 || !appState) {
        return
      }

      const data: CanvasData = {
        elements,
        appState: {
          ...appState,
          collaborators: undefined!,
        },
        files,
      }

      let thumbnail = ''
      const latestImage = elements
        .filter((element) => element.type === 'image')
        .sort((a, b) => b.updated - a.updated)[0]
      if (latestImage) {
        const file = files[latestImage.fileId!]
        if (file) {
          thumbnail = file.dataURL
        }
      }

      saveCanvas(canvasId, { data, thumbnail })
    },
    5000, // 5000
  )

  // Combined handler that calls both immediate and debounced functions
  const handleChange = (elements: Readonly<OrderedExcalidrawElement[]>, appState: AppState, files: BinaryFiles) => {
    // Immediate UI updates
    handleSelectionChange(elements, appState)
    // Debounced save operation
    handleSave(elements, appState, files)
  }

  const lastImagePosition = useRef<LastImagePosition | null>(
    localStorage.getItem('excalidraw-last-image-position')
      ? JSON.parse(localStorage.getItem('excalidraw-last-image-position')!)
      : null,
  )
  const { theme } = useTheme()

  // 添加自定义类名以便应用我们的CSS修复
  const excalidrawClassName = `excalidraw-custom ${theme === 'dark' ? 'excalidraw-dark-fix-wm76394yjopk' : 'excalidraw-wm76394yjopk'}`

  // 在深色模式下使用自定义主题设置，避免使用默认的滤镜
  // 这样可以确保颜色在深色模式下正确显示
  const customTheme = theme === 'dark' ? 'light' : theme

  // 在组件挂载和主题变化时设置深色模式下的背景色
  useEffect(() => {
    if (excalidrawAPI && theme === 'dark') {
      // 设置深色背景，但保持light主题以避免颜色反转
      excalidrawAPI.updateScene({
        appState: {
          viewBackgroundColor: '#121212',
          // gridColor: 'rgba(255, 255, 255, 0.1)',
        },
      })
    } else if (excalidrawAPI && theme === 'light') {
      // 恢复浅色背景
      excalidrawAPI.updateScene({
        appState: {
          viewBackgroundColor: '#ffffff',
          // gridColor: 'rgba(0, 0, 0, 0.1)',
        },
      })
    }
  }, [excalidrawAPI, theme])

  const addImageToExcalidraw = useCallback(
    async (imageElement: ExcalidrawImageElement, imageUrl: string) => {
      if (!excalidrawAPI) return

      try {
        // Fetch the image
        // Use native fetch to avoid adding Authorization headers from apiClient to external URLs
        // which can cause CORS issues
        const response = await fetch(imageUrl)
        const blob = await response.blob()

        // Convert to data URL
        const reader = new FileReader()
        reader.readAsDataURL(blob)
        reader.onloadend = async () => {
          const base64data = reader.result as string

          // Create file object
          // Use existing fileId from element if available, otherwise generate new one
          const fileId = (imageElement.fileId as string) || (nanoid() as string)

          const file: BinaryFileData = {
            id: fileId as any, // Cast to any to avoid FileId type error
            dataURL: base64data as any,
            mimeType: blob.type as any,
            created: Date.now(),
            lastRetrieved: Date.now(),
          }

          // Get image dimensions if not provided or 0
          let width = imageElement.width
          let height = imageElement.height

          if (!width || !height) {
            const img = new Image()
            img.src = base64data
            await new Promise((resolve) => {
              img.onload = resolve
            })
            width = img.width
            height = img.height

            // Scale down if too large (max 1000px)
            const MAX_DIMENSION = 1000
            if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
              const ratio = Math.min(MAX_DIMENSION / width, MAX_DIMENSION / height)
              width *= ratio
              height *= ratio
            }
          }

          // Calculate position based on last image
          let x = imageElement.x
          let y = imageElement.y

          if (lastImagePosition.current) {
            const GAP = 20
            x = lastImagePosition.current.x + lastImagePosition.current.width + GAP
            y = lastImagePosition.current.y
          }

          // Ensure image is not locked and can be manipulated
          const unlockedImageElement = {
            ...imageElement,
            fileId: fileId as any,
            x,
            y,
            width,
            height,
            locked: false,
            groupIds: [],
            isDeleted: false,
          }

          // Get current elements
          const currentElements = excalidrawAPI.getSceneElements()

          // Add file to Excalidraw
          excalidrawAPI.addFiles([file])

          console.log('👇 Adding new image element to canvas:', unlockedImageElement.id)

          // Place new image at the beginning (bottom) of the stack to avoid obscuring existing elements
          excalidrawAPI.updateScene({
            elements: [...(currentElements || []), unlockedImageElement],
          })

          // Update last image position
          lastImagePosition.current = {
            x,
            y,
            width,
            height,
            col: 0, // Not strictly used here but required by type
          }

          localStorage.setItem('excalidraw-last-image-position', JSON.stringify(lastImagePosition.current))
        }
      } catch (error) {
        console.error('Failed to add image to canvas:', error)
      }
    },
    [excalidrawAPI],
  )

  const addVideoEmbed = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async (elementData: any, videoSrc: string) => {
      if (!excalidrawAPI) return

      // Function to create video element with given dimensions
      const createVideoElement = (finalWidth: number, finalHeight: number) => {
        console.log('👇 Video element properties:', {
          id: elementData.id,
          type: elementData.type,
          locked: elementData.locked,
          groupIds: elementData.groupIds,
          isDeleted: elementData.isDeleted,
          x: elementData.x,
          y: elementData.y,
          width: elementData.width,
          height: elementData.height,
        })

        const videoElements = convertToExcalidrawElements([
          {
            type: 'embeddable',
            id: elementData.id,
            x: elementData.x,
            y: elementData.y,
            width: elementData.width,
            height: elementData.height,
            link: videoSrc,
            // 添加必需的基本样式属性
            strokeColor: '#000000',
            backgroundColor: 'transparent',
            fillStyle: 'solid',
            strokeWidth: 1,
            strokeStyle: 'solid',
            roundness: null,
            roughness: 1,
            opacity: 100,
            // 添加必需的变换属性
            angle: 0,
            seed: Math.random(),
            version: 1,
            versionNonce: Math.random(),
            // 添加必需的状态属性
            locked: false,
            isDeleted: false,
            groupIds: [],
            // 添加绑定框属性
            boundElements: [],
            updated: Date.now(),
            // 添加必需的索引和帧ID属性
            frameId: null,
            index: null, // 添加缺失的index属性
            // 添加自定义数据属性
            customData: {},
          },
        ])

        console.log('👇 Converted video elements:', videoElements)

        const currentElements = excalidrawAPI.getSceneElements()
        const newElements = [...currentElements, ...videoElements]

        console.log('👇 Updating scene with elements count:', newElements.length)

        excalidrawAPI.updateScene({
          elements: newElements,
        })

        console.log('👇 Added video embed element:', videoSrc, `${elementData.width}x${elementData.height}`)
      }

      // If dimensions are provided, use them directly
      if (elementData.width && elementData.height) {
        createVideoElement(elementData.width, elementData.height)
        return
      }

      // Otherwise, try to get video's natural dimensions
      const video = document.createElement('video')
      video.crossOrigin = 'anonymous'

      video.onloadedmetadata = () => {
        const videoWidth = video.videoWidth
        const videoHeight = video.videoHeight

        if (videoWidth && videoHeight) {
          // Scale down if video is too large (max 800px width)
          const maxWidth = 800
          let finalWidth = videoWidth
          let finalHeight = videoHeight

          if (videoWidth > maxWidth) {
            const scale = maxWidth / videoWidth
            finalWidth = maxWidth
            finalHeight = videoHeight * scale
          }

          createVideoElement(finalWidth, finalHeight)
        } else {
          // Fallback to default dimensions
          createVideoElement(320, 180)
        }
      }

      video.onerror = () => {
        console.warn('Could not load video metadata, using default dimensions')
        createVideoElement(320, 180)
      }

      video.src = videoSrc
    },
    [excalidrawAPI],
  )

  const renderEmbeddable = useCallback((element: NonDeleted<ExcalidrawEmbeddableElement>, appState: AppState) => {
    const { link } = element

    // Check if this is a video URL
    if (
      link &&
      (link.includes('.mp4') ||
        link.includes('.webm') ||
        link.includes('.ogg') ||
        link.startsWith('blob:') ||
        link.includes('video'))
    ) {
      // Return the VideoPlayer component
      return <VideoElement src={link} width={element.width} height={element.height} />
    }

    console.log('👇 Not a video URL, returning null for:', link)
    // Return null for non-video embeds to use default rendering
    return null
  }, [])

  const handleImageGenerated = useCallback(
    (imageData: ISocket.SessionImageGeneratedEvent) => {
      console.log('👇 CanvasExcali received image_generated:', imageData)

      // Only handle if it's for this canvas
      if (imageData.canvas_id !== canvasId) {
        console.log('👇 Image not for this canvas, ignoring')
        return
      }

      // Check if this is actually a video generation event that got mislabeled
      if (imageData.file?.mimeType?.startsWith('video/')) {
        console.log('👇 This appears to be a video, not an image. Ignoring in image handler.')
        return
      }

      let imageElement = imageData.element

      // If element is missing or invalid (e.g. empty string from backend), create a default one
      if (!imageElement || typeof imageElement !== 'object') {
        console.log('👇 Image element missing or invalid, creating default')
        imageElement = {
          type: 'image',
          fileId: null,
          status: 'saved',
          x: lastImagePosition.current?.x || 0,
          y: lastImagePosition.current?.y || 0,
          width: 0, // Will be updated in addImageToExcalidraw
          height: 0, // Will be updated in addImageToExcalidraw
          angle: 0,
          strokeColor: 'transparent',
          backgroundColor: 'transparent',
          fillStyle: 'hachure',
          strokeWidth: 1,
          strokeStyle: 'solid',
          roughness: 1,
          opacity: 100,
          groupIds: [],
          roundness: null,
          seed: Math.random(),
          version: 1,
          versionNonce: Math.random(),
          isDeleted: false,
          boundElements: null,
          updated: Date.now(),
          link: null,
          locked: false,
          customData: {},
          frameId: null,
          scale: [1, 1],
          index: null,
          id: nanoid(),
          crop: null,
        } as ExcalidrawImageElement
      }

      addImageToExcalidraw(imageElement, imageData.image_url)
    },
    [addImageToExcalidraw, canvasId],
  )

  const handleVideoGenerated = useCallback(
    (videoData: ISocket.SessionVideoGeneratedEvent) => {
      console.log('👇 CanvasExcali received video_generated:', videoData)

      // Only handle if it's for this canvas
      if (videoData.canvas_id !== canvasId) {
        console.log('👇 Video not for this canvas, ignoring')
        return
      }

      // Create video embed element using the video URL
      addVideoEmbed(videoData.element, videoData.video_url)
    },
    [addVideoEmbed, canvasId],
  )

  const handleAddImageToCanvas = useCallback(
    async (data: { url: string }) => {
      console.log('👇 CanvasExcali received add_image_to_canvas:', data)

      // Create image element structure
      // We don't have dimensions yet, addImageToExcalidraw will handle it
      const imageElement: ExcalidrawImageElement = {
        type: 'image',
        fileId: null,
        status: 'saved',
        x: lastImagePosition.current?.x || 0,
        y: lastImagePosition.current?.y || 0,
        width: 0, // Will be updated in addImageToExcalidraw
        height: 0, // Will be updated in addImageToExcalidraw
        angle: 0,
        strokeColor: 'transparent',
        backgroundColor: 'transparent',
        fillStyle: 'hachure',
        strokeWidth: 1,
        strokeStyle: 'solid',
        roughness: 1,
        opacity: 100,
        groupIds: [],
        roundness: null,
        seed: Math.random(),
        version: 1,
        versionNonce: Math.random(),
        isDeleted: false,
        boundElements: null,
        updated: Date.now(),
        link: null,
        locked: false,
        customData: {},
        frameId: null,
        scale: [1, 1],
        index: null,
        id: nanoid(),
        crop: null,
      }

      addImageToExcalidraw(imageElement, data.url)
    },
    [addImageToExcalidraw],
  )

  useEffect(() => {
    eventBus.on('Socket::Session::ImageGenerated', handleImageGenerated)
    eventBus.on('Socket::Session::VideoGenerated', handleVideoGenerated)
    eventBus.on('Chat::AddImageToCanvas', handleAddImageToCanvas)
    return () => {
      eventBus.off('Socket::Session::ImageGenerated', handleImageGenerated)
      eventBus.off('Socket::Session::VideoGenerated', handleVideoGenerated)
      eventBus.off('Chat::AddImageToCanvas', handleAddImageToCanvas)
    }
  }, [handleImageGenerated, handleVideoGenerated, handleAddImageToCanvas])

  return (
    <div className={excalidrawClassName} style={{ width: '100%', height: '100%' }}>
      <Excalidraw
        theme={customTheme as Theme}
        langCode={i18n.language}
        excalidrawAPI={(api) => {
          setExcalidrawAPI(api)
        }}
        onChange={handleChange}
        initialData={() => {
          const data = initialData
          console.log('👇initialData', data)
          if (data?.appState) {
            data.appState = {
              ...data.appState,
              collaborators: undefined!,
              // Reset critical state properties to ensure canvas is usable
              activeTool: {
                type: 'selection',
                customType: null,
                locked: false,
                lastActiveTool: null,
              },
              viewModeEnabled: false,
              zenModeEnabled: false,
              isLoading: false,
              errorMessage: null,
              selectedElementIds: {}, // Clear selection to avoid UI side effects
            }
          }
          return data || null
        }}
        renderEmbeddable={renderEmbeddable}
        // Allow all URLs for embeddable content
        validateEmbeddable={(url: string) => {
          console.log('👇 Validating embeddable URL:', url)
          // Allow all URLs - return true for everything
          return true
        }}
        // Ensure interactive mode is enabled
        viewModeEnabled={false}
        zenModeEnabled={false}
        // Allow element manipulation
        onPointerUpdate={(payload) => {
          // Minimal logging - only log significant pointer events
          if (payload.button === 'down' && Math.random() < 0.05) {
            // console.log('👇 Pointer down on:', payload.pointer.x, payload.pointer.y)
          }
        }}
      />
    </div>
  )
}

export { CanvasExcali }
export default CanvasExcali
