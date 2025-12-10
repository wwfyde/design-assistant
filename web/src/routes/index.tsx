import { createCanvas } from '@/api/canvas'
import TopMenu from '@/components/TopMenu'
import ChatTextarea from '@/components/chat/ChatTextarea'
import CanvasList from '@/components/home/CanvasList'
import { PromptList } from '@/components/home/PromptList'
import { ScrollArea } from '@/components/ui/scroll-area'
import { DEFAULT_SYSTEM_PROMPT } from '@/constants'
import { useConfigs } from '@/contexts/configs'
import { eventBus } from '@/lib/event'
import { useMutation } from '@tanstack/react-query'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { motion } from 'motion/react'
import { nanoid } from 'nanoid'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { toast } from 'sonner'

export const Route = createFileRoute('/')({
  component: Home,
})

function Home() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { setInitCanvas } = useConfigs()

  const { mutate: createCanvasMutation, isPending } = useMutation({
    mutationFn: createCanvas,
    onSuccess: (data, variables) => {
      setInitCanvas(true)
      navigate({
        to: '/canvas/$id',
        params: { id: data.id },
        search: {
          sessionId: variables.session_id,
        },
      })
    },
    onError: (error) => {
      toast.error(t('common:messages.error'), {
        description: error.message,
      })
    },
  })

  useEffect(() => {
    const handleScrollToTop = () => {
      const viewport = document.querySelector('[data-radix-scroll-area-viewport]')
      if (viewport) {
        viewport.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    eventBus.on('Chat::ScrollToTop', handleScrollToTop)
    return () => {
      eventBus.off('Chat::ScrollToTop', handleScrollToTop)
    }
  }, [])

  return (
    // <div className='flex flex-col h-screen'>
    // <div className='flex flex-col h-[calc(100vh-56px)]'>
    <div className='flex flex-col h-screen'>
      <ScrollArea className='flex-1'>
        <PromptList />
        <CanvasList />
      </ScrollArea>
      <div className='w-full flex flex-col items-center justify-center p-4 bg-background sticky bottom-0 z-50'>
        <ChatTextarea
          className='w-full max-w-4xl max-h-60'
          messages={[]}
          onSendMessages={(messages, configs) => {
            createCanvasMutation({
              name: t('home:newCanvas'),
              canvas_id: nanoid(),
              messages: messages,
              session_id: nanoid(),
              text_model: configs.textModel,
              tool_list: configs.toolList,
              system_prompt: localStorage.getItem('system_prompt') || DEFAULT_SYSTEM_PROMPT,
            })
          }}
          pending={isPending}
        />
      </div>
    </div>
  )
}
