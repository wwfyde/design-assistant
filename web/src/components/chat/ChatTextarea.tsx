import { cancelChat } from '@/api/chat'
import { cancelMagicGenerate } from '@/api/magic'
import { ToolInfo } from '@/api/model'
import { uploadImage, uploadImageFromUrl } from '@/api/upload'
import ImageConfigSelector, { AspectRatio, ImageSize } from '@/components/chat/ImageConfigSelector'
import { Button } from '@/components/ui/button'
import { useConfigs } from '@/contexts/configs'
import { eventBus, TCanvasAddImagesToChatEvent, TMaterialAddImagesToChatEvent } from '@/lib/event'
import { cn, dataURLToFile } from '@/lib/utils'
import { Message, MessageContent, Model } from '@/types/types'
import { useMutation } from '@tanstack/react-query'
import { useDrop } from 'ahooks'
import { produce } from 'immer'
import { ArrowUp, Check, ChevronDown, Loader2, PlusIcon, Square, XIcon } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import Textarea, { TextAreaRef } from 'rc-textarea'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { PhotoView } from 'react-photo-view'
import { toast } from 'sonner'
import { v7 as uuidv7 } from 'uuid'
// import { useAuth } from '@/contexts/AuthContext'
// import { useBalance } from '@/hooks/use-balance'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { BASE_API_URL, PROVIDER_NAME_MAPPING } from '@/constants'
import { apiClient } from '@/lib/api-client.ts'

type ChatTextareaProps = {
  pending: boolean
  className?: string
  messages: Message[]
  sessionId?: string
  onSendMessages: (
    data: Message[],
    configs: {
      textModel: Model
      toolList: ToolInfo[]
    },
  ) => void
  onCancelChat?: () => void
}

const ChatTextarea: React.FC<ChatTextareaProps> = ({
  pending,
  className,
  messages,
  sessionId,
  onSendMessages,
  onCancelChat,
}) => {
  const { t } = useTranslation()
  // const { authStatus } = useAuth()
  const is_logged_in = true
  const { textModel, setTextModel, textModels, selectedTools, setSelectedTools, allTools, setShowLoginDialog } =
    useConfigs()
  // const { balance } = useBalance()
  const [prompt, setPrompt] = useState('')
  const textareaRef = useRef<TextAreaRef>(null)
  const [images, setImages] = useState<
    {
      id: string
      width: number
      height: number
      url: string
    }[]
  >([])
  const [isFocused, setIsFocused] = useState(false)
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('Auto')
  const [lockRatio, setLockRatio] = useState(true)

  const [imageSize, setImageSize] = useState<ImageSize>('2K')
  const [imgWidth, setImgWidth] = useState(2048)
  const [imgHeight, setImgHeight] = useState(2048)
  const [quantity, setQuantity] = useState<number>(1)

  const imageInputRef = useRef<HTMLInputElement>(null)

  // 充值按钮组件
  const RechargeContent = useCallback(
    () => (
      <div className='flex items-center justify-between gap-3'>
        <span className='text-sm text-muted-foreground flex-1'>{t('chat:insufficientBalanceDescription')}</span>
        <Button
          size='sm'
          variant='outline'
          className='shrink-0'
          onClick={() => {
            const billingUrl = `${BASE_API_URL}/billing`
            if (window.electronAPI?.openBrowserUrl) {
              window.electronAPI.openBrowserUrl(billingUrl)
            } else {
              window.open(billingUrl, '_blank')
            }
          }}
        >
          {t('common:auth.recharge')}
        </Button>
      </div>
    ),
    [t],
  )

  const { mutate: uploadImageMutation } = useMutation({
    mutationFn: (file: File) => uploadImage(file),
    onSuccess: (data) => {
      console.log('🦄uploadImageMutation onSuccess', data)
      setImages((prev) => [
        ...prev,
        {
          id: data.id,
          width: data.width,
          height: data.height,
          url: data.url,
        },
      ])
    },
    onError: (error) => {
      console.error('🦄uploadImageMutation onError', error)
      toast.error('Failed to upload image', {
        description: <div>{error.toString()}</div>,
      })
    },
  })

  const handleImagesUpload = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files) {
        for (const file of files) {
          uploadImageMutation(file)
        }
      }
    },
    [uploadImageMutation],
  )

  const handleCancelChat = useCallback(async () => {
    if (sessionId) {
      // 同时取消普通聊天和魔法生成任务
      await Promise.all([cancelChat(sessionId), cancelMagicGenerate(sessionId)])
    }
    onCancelChat?.()
  }, [sessionId, onCancelChat])

  // Send Prompt
  const handleSendPrompt = useCallback(async () => {
    if (pending) return

    // 检查是否使用 Jaaz 服务
    const isUsingJaaz = textModel?.provider === 'jaaz' || selectedTools?.some((tool) => tool.provider === 'jaaz')
    // console.log('👀isUsingJaaz', textModel, selectedTools, isUsingJaaz)

    // 只有当使用 Jaaz 服务且余额为 0 时才提醒充值
    if (is_logged_in && isUsingJaaz) {
      toast.error(t('chat:insufficientBalance'), {
        description: <RechargeContent />,
        duration: 10000, // 10s，给用户更多时间操作
      })
      return
    }

    if (!textModel) {
      toast.error(t('chat:textarea.selectModel'))
      if (!is_logged_in) {
        setShowLoginDialog(true)
      }
      return
    }

    if (!selectedTools || selectedTools.length === 0) {
      toast.warning(t('chat:textarea.selectTool'))
    }

    let text_content: MessageContent[] | string = prompt
    if (prompt.length === 0 || prompt.trim() === '') {
      toast.error(t('chat:textarea.enterPrompt'))
      return
    }

    // Add aspect ratio and quantity information if not default values
    let additionalInfo = ''
    if (aspectRatio != 'Auto' && lockRatio) {
      additionalInfo += `<aspect_ratio>${aspectRatio}</aspect_ratio>\n`
    }
    if (imgWidth && imgHeight && !lockRatio) {
      additionalInfo += `<aspect_ratio>${imgWidth}:${imgHeight}</aspect_ratio>\n`
    }
    if (imageSize) {
      additionalInfo += `<image_size>${imageSize}</image_size>\n`
    }
    if (quantity !== 1) {
      additionalInfo += `<quantity>${quantity}</quantity>\n`
    }

    if (additionalInfo) {
      text_content = text_content + '\n\n' + additionalInfo
    }

    if (images.length > 0) {
      text_content += `\n\n<input_images count="${images.length}">`
      images.forEach((image, index) => {
        text_content += `\n<image index="${index + 1}" id="${image.id}" image_url="${image.url}" width="${image.width}" height="${image.height}" />`
      })
      text_content += `\n</input_images>`
    }

    const final_content = [
      {
        type: 'text',
        text: text_content as string,
      },
      ...images.map((image) => ({
        type: 'image_url',
        image_url: {
          url: image.url,
        },
      })),
    ] as MessageContent[]

    const newMessages = [
      {
        id: uuidv7(),
        role: 'user',
        content: final_content,
      },
    ] as Message[]

    setImages([])
    setPrompt('')

    onSendMessages(newMessages, {
      textModel: textModel,
      toolList: selectedTools && selectedTools.length > 0 ? selectedTools : [],
    })
  }, [
    pending,
    textModel,
    selectedTools,
    prompt,
    onSendMessages,
    images,
    messages,
    t,
    aspectRatio,
    imageSize,
    imgWidth,
    imgHeight,
    quantity,
    // authStatus.is_logged_in,
    setShowLoginDialog,
    // balance,
    RechargeContent,
  ])

  // Drop Area
  const dropAreaRef = useRef<HTMLDivElement>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const handleFilesDrop = useCallback(
    (files: File[]) => {
      for (const file of files) {
        uploadImageMutation(file)
      }
    },
    [uploadImageMutation],
  )

  useDrop(dropAreaRef, {
    onDragOver() {
      setIsDragOver(true)
    },
    onDragLeave() {
      setIsDragOver(false)
    },
    onDrop() {
      setIsDragOver(false)
    },
    onFiles: handleFilesDrop,
  })

  useEffect(() => {
    const handleAddImagesToChat = (data: TCanvasAddImagesToChatEvent) => {
      data.forEach(async (image) => {
        if (image.base64) {
          const file = dataURLToFile(image.base64, image.fileId)
          uploadImageMutation(file)
        } else {
          setImages(
            produce((prev) => {
              prev.push({
                id: image.fileId,
                width: image.width,
                height: image.height,
                url: image.url || `/api/file/${image.fileId}`, // Use provided URL or fallback to local file API
              })
            }),
          )
        }
      })

      textareaRef.current?.focus()
    }

    const handleMaterialAddImagesToChat = async (data: TMaterialAddImagesToChatEvent) => {
      data.forEach(async (image: TMaterialAddImagesToChatEvent[0]) => {
        // Convert file path to blob and upload
        try {
          const fileUrl = `/api/serve_file?file_path=${encodeURIComponent(image.filePath)}`
          const response = await apiClient.get(fileUrl)
          const blob = await response.blob()
          const file = new File([blob], image.fileName, {
            type: `image/${image.fileType}`,
          })
          uploadImageMutation(file)
        } catch (error) {
          console.error('Failed to load image from material:', error)
          toast.error('Failed to load image from material', {
            description: `${error}`,
          })
        }
      })

      textareaRef.current?.focus()
    }

    eventBus.on('Canvas::AddImagesToChat', handleAddImagesToChat)
    eventBus.on('Material::AddImagesToChat', handleMaterialAddImagesToChat)
    eventBus.on('Chat::SetPrompt', (data) => {
      console.log('Received Chat::SetPrompt', data)
      setPrompt(data.prompt)
      textareaRef.current?.focus()
    })
    eventBus.on('Chat::Clear', () => {
      setPrompt('')
      setImages([])
    })
    return () => {
      eventBus.off('Canvas::AddImagesToChat', handleAddImagesToChat)
      eventBus.off('Material::AddImagesToChat', handleMaterialAddImagesToChat)
      eventBus.off('Chat::SetPrompt')
      eventBus.off('Chat::Clear')
      eventBus.off('Chat::AddImageFromUrl')
    }
  }, [uploadImageMutation])

  useEffect(() => {
    const handleAddImageFromUrl = async (data: { url: string; name?: string }) => {
      try {
        const result = await uploadImageFromUrl(data.url)
        setImages((prev) => [
          ...prev,
          {
            id: result.id,
            width: result.width,
            height: result.height,
            url: result.url,
          },
        ])
        textareaRef.current?.focus()
      } catch (error) {
        console.error('Failed to add image from URL:', error)
        toast.error('Failed to add image', {
          description: String(error),
        })
      }
    }

    eventBus.on('Chat::AddImageFromUrl', handleAddImageFromUrl)
    return () => {
      eventBus.off('Chat::AddImageFromUrl', handleAddImageFromUrl)
    }
  }, [])

  return (
    <motion.div
      ref={dropAreaRef}
      className={cn(
        'w-full flex flex-col items-center border border-primary/20 rounded-2xl p-3 hover:border-primary/40 transition-all duration-300 cursor-text gap-5 bg-background/80 backdrop-blur-xl relative',
        isFocused && 'border-primary/40',
        className,
      )}
      style={{
        boxShadow: isFocused ? '0 0 0 4px color-mix(in oklab, var(--primary) 10%, transparent)' : 'none',
      }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3, ease: 'linear' }}
      onClick={() => textareaRef.current?.focus()}
    >
      <AnimatePresence>
        {isDragOver && (
          <motion.div
            className='absolute top-0 left-0 right-0 bottom-0 bg-background/50 backdrop-blur-xl rounded-2xl z-10'
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
          >
            <div className='flex items-center justify-center h-full'>
              <p className='text-sm text-muted-foreground'>Drop images here to upload</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {images.length > 0 && (
          <motion.div
            className='flex items-center gap-2 w-full'
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
          >
            {images.map((image) => (
              <motion.div
                key={image.id}
                className='relative size-10'
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2, ease: 'easeInOut' }}
              >
                <PhotoView src={image.url}>
                  <img
                    key={image.id}
                    src={image.url}
                    alt='Uploaded image'
                    className='w-full h-full object-cover rounded-md'
                    draggable={false}
                  />
                </PhotoView>
                <Button
                  variant='secondary'
                  size='icon'
                  className='absolute -top-1 -right-1 size-4'
                  onClick={() => setImages((prev) => prev.filter((i) => i.id !== image.id))}
                >
                  <XIcon className='size-3' />
                </Button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <Textarea
        ref={textareaRef}
        className='w-full h-full border-none outline-none resize-none text-sm'
        placeholder={t('chat:textarea.placeholder')}
        value={prompt}
        autoSize
        onChange={(e) => setPrompt(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSendPrompt()
          }
        }}
      />

      <div className='flex items-center justify-between gap-2 w-full'>
        <div className='flex items-center gap-2 max-w-[calc(100%-50px)] flex-wrap'>
          <input ref={imageInputRef} type='file' accept='image/*' multiple onChange={handleImagesUpload} hidden />
          <Button variant='outline' size='sm' onClick={() => imageInputRef.current?.click()}>
            <PlusIcon className='size-4' />
          </Button>

          {/* Text Model Selector */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant='outline' size='sm' className='flex items-center gap-1 hidden'>
                {textModel && PROVIDER_NAME_MAPPING[textModel.provider]?.icon && (
                  <img
                    src={PROVIDER_NAME_MAPPING[textModel.provider].icon}
                    alt={textModel.provider}
                    className='size-4 rounded-full'
                  />
                )}
                <span className='text-sm truncate max-w-[100px]'>
                  {textModel?.display_name || t('chat:modelSelector.selectModel')}
                </span>
                <ChevronDown className='size-3 opacity-50' />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='start' className='max-h-60 overflow-y-auto'>
              {textModels.map((model) => (
                <DropdownMenuItem
                  key={`${model.provider}:${model.model}`}
                  onClick={() => {
                    setTextModel(model)
                    localStorage.setItem('text_model', `${model.provider}:${model.model}`)
                  }}
                  className='flex items-center justify-between'
                >
                  <div className='flex items-center gap-2'>
                    {PROVIDER_NAME_MAPPING[model.provider]?.icon && (
                      <img
                        src={PROVIDER_NAME_MAPPING[model.provider].icon}
                        alt={model.provider}
                        className='size-4 rounded-full'
                      />
                    )}
                    <span>{model.display_name}</span>
                  </div>
                  {textModel?.provider === model.provider && textModel?.model === model.model && (
                    <Check className='size-4' />
                  )}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Image Model Selector */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant='outline' size='sm' className='flex items-center gap-1'>
                {(() => {
                  const selectedImageTool = selectedTools?.find((t) => t.type === 'image')
                  if (selectedImageTool) {
                    return (
                      <>
                        {PROVIDER_NAME_MAPPING[selectedImageTool.provider]?.icon && (
                          <img
                            src={PROVIDER_NAME_MAPPING[selectedImageTool.provider].icon}
                            alt={selectedImageTool.provider}
                            className='size-4 rounded-full'
                          />
                        )}
                        <span className='text-sm truncate max-w-[100px]'>
                          {selectedImageTool.display_name || selectedImageTool.id}
                        </span>
                      </>
                    )
                  }
                  return <span className='text-sm'>{t('chat:modelSelector.tabs.image')}</span>
                })()}
                <ChevronDown className='size-3 opacity-50' />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='start' className='max-h-60 overflow-y-auto'>
              {allTools
                .filter((t) => t.type === 'image')
                .map((tool) => {
                  const isSelected = selectedTools?.some((t) => t.id === tool.id)
                  return (
                    <DropdownMenuItem
                      key={`${tool.provider}:${tool.id}`}
                      onClick={() => {
                        const otherTools = selectedTools?.filter((t) => t.type !== 'image') || []
                        const newSelectedTools = [...otherTools, tool]

                        setSelectedTools(newSelectedTools)
                        localStorage.setItem(
                          'disabled_tool_ids',
                          JSON.stringify(allTools.filter((t) => !newSelectedTools.includes(t)).map((t) => t.id)),
                        )
                      }}
                      className='flex items-center justify-between'
                    >
                      <div className='flex items-center gap-2'>
                        {PROVIDER_NAME_MAPPING[tool.provider]?.icon && (
                          <img
                            src={PROVIDER_NAME_MAPPING[tool.provider].icon}
                            alt={tool.provider}
                            className='size-4 rounded-full'
                          />
                        )}
                        <span>{tool.display_name || tool.id}</span>
                      </div>
                      {isSelected && <Check className='size-4' />}
                    </DropdownMenuItem>
                  )
                })}
            </DropdownMenuContent>
          </DropdownMenu>

          {/*旧版模型选择器*/}
          {/*<ModelSelectorV3 />*/}

          {/* Image Config Selector */}
          <ImageConfigSelector
            aspectRatio={aspectRatio}
            imageSize={imageSize}
            width={imgWidth}
            height={imgHeight}
            lock={lockRatio}
            onChange={(config) => {
              setAspectRatio(config.aspectRatio)
              setImageSize(config.imageSize)
              setImgWidth(config.width)
              setImgHeight(config.height)
              setLockRatio(config.lock)
            }}
          />

          {/* Quantity Selector */}
          {/*<QuantitySelector value={quantity} onChange={setQuantity}/>*/}
        </div>

        {pending ? (
          <Button className='shrink-0 relative' variant='default' size='icon' onClick={handleCancelChat}>
            <Loader2 className='size-5.5 animate-spin absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2' />
            <Square className='size-2 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2' />
          </Button>
        ) : (
          <Button
            className='shrink-0'
            variant='default'
            size='icon'
            onClick={handleSendPrompt}
            disabled={!textModel || !selectedTools || prompt.length === 0}
          >
            <ArrowUp className='size-4' />
          </Button>
        )}
      </div>
    </motion.div>
  )
}

export default ChatTextarea
