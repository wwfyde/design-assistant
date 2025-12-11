import { createCanvas } from '@/api/canvas'
import ChatTextarea from '@/components/chat/ChatTextarea'
import CanvasList from '@/components/home/CanvasList'
import { HuabanList } from '@/components/home/HuabanList'
import { PromptList } from '@/components/home/PromptList'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DEFAULT_SYSTEM_PROMPT } from '@/constants'
import { useConfigs } from '@/contexts/configs'
import { eventBus } from '@/lib/event'
import { useMutation } from '@tanstack/react-query'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
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
    <div className='flex flex-col h-screen'>
      <Tabs defaultValue='huaban' className='flex flex-col flex-1 overflow-hidden'>
        <div className='px-4 pt-2 shrink-0'>
          <TabsList className='grid w-full grid-cols-3'>
            <TabsTrigger value='huaban'>外部图像库</TabsTrigger>
            <TabsTrigger value='prompt'>Prompt库</TabsTrigger>
            <TabsTrigger value='history'>历史记录</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent
          value='prompt'
          className='flex-1 overflow-hidden mt-2 border-none p-0 outline-none data-[state=inactive]:hidden'
        >
          <ScrollArea className='h-full'>
            <PromptList />
          </ScrollArea>
        </TabsContent>

        <TabsContent
          value='huaban'
          className='flex-1 overflow-hidden mt-2 border-none p-0 outline-none data-[state=inactive]:hidden'
        >
          <ScrollArea className='h-full'>
            <HuabanList />
          </ScrollArea>
        </TabsContent>

        <TabsContent
          value='history'
          className='flex-1 overflow-hidden mt-2 border-none p-0 outline-none data-[state=inactive]:hidden'
        >
          <ScrollArea className='h-full'>
            <CanvasList />
          </ScrollArea>
        </TabsContent>
      </Tabs>

      <div className='w-full flex flex-col items-center justify-center p-4 bg-background sticky bottom-0 z-50 mt-auto'>
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
