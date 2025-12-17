import { getCanvas, renameCanvas } from '@/api/canvas'
import CanvasExcali from '@/components/canvas/CanvasExcali'
import CanvasHeader from '@/components/canvas/CanvasHeader'
import CanvasMenu from '@/components/canvas/menu'
import CanvasPopbarWrapper from '@/components/canvas/pop-bar'
// VideoCanvasOverlay removed - using native Excalidraw embeddable elements instead
import ChatInterface from '@/components/chat/Chat'
import { Button } from '@/components/ui/button'
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable'
import { CanvasProvider } from '@/contexts/canvas'
import { Session } from '@/types/types'
import { createFileRoute, useParams, useSearch } from '@tanstack/react-router'
import { Loader2, MessageSquare } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { ImperativePanelHandle } from 'react-resizable-panels'

export const Route = createFileRoute('/canvas/$id')({
  component: Canvas,
  validateSearch: (search: Record<string, unknown>): { sessionId?: string; returnTab?: string } => {
    return {
      sessionId: search.sessionId as string | undefined,
      returnTab: search.returnTab as string | undefined,
    }
  },
})

function Canvas() {
  const { id } = useParams({ from: '/canvas/$id' })
  const [canvas, setCanvas] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [canvasName, setCanvasName] = useState('')
  const [sessionList, setSessionList] = useState<Session[]>([])
  const chatPanelRef = useRef<ImperativePanelHandle>(null)
  const [isChatOpen, setIsChatOpen] = useState(true)
  // initialVideos removed - using native Excalidraw embeddable elements instead
  const search = useSearch({ from: '/canvas/$id' })
  const searchSessionId = search?.sessionId || ''
  const returnTab = search?.returnTab
  useEffect(() => {
    let mounted = true

    const fetchCanvas = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await getCanvas(id)
        if (mounted) {
          console.log('👇 Fetched canvas data:', data)
          // Parse data if it's a string (which might happen if backend stores it as string)
          if (data.data && typeof data.data === 'string') {
            try {
              data.data = JSON.parse(data.data)
            } catch (e) {
              console.error('Failed to parse canvas data:', e)
            }
          }
          setCanvas(data)
          setCanvasName(data.name)
          setSessionList(data.sessions)
          // Video elements now handled by native Excalidraw embeddable elements
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err : new Error('Failed to fetch canvas data'))
          console.error('Failed to fetch canvas data:', err)
        }
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    fetchCanvas()

    return () => {
      mounted = false
    }
  }, [id])

  const handleNameSave = async () => {
    await renameCanvas(id, canvasName)
  }

  return (
    <CanvasProvider>
      <div className='flex flex-col w-screen h-screen relative'>
        <CanvasHeader
          canvasName={canvasName}
          canvasId={id}
          onNameChange={setCanvasName}
          onNameSave={handleNameSave}
          returnTab={returnTab}
        />
        <ResizablePanelGroup direction='horizontal' className='w-screen h-screen' autoSaveId='jaaz-chat-panel'>
          <ResizablePanel className='relative' defaultSize={75}>
            <div className='w-full h-full'>
              {isLoading ? (
                <div className='flex-1 flex-grow px-4 bg-accent w-[24%] absolute right-0'>
                  <div className='flex items-center justify-center h-full'>
                    <Loader2 className='w-4 h-4 animate-spin' />
                  </div>
                </div>
              ) : (
                <div className='relative w-full h-full'>
                  <CanvasExcali canvasId={id} initialData={canvas?.data} />
                  <CanvasMenu />
                  <CanvasPopbarWrapper />
                </div>
              )}
            </div>
          </ResizablePanel>

          <ResizableHandle />

          <ResizablePanel
            ref={chatPanelRef}
            defaultSize={25}
            collapsible={true}
            minSize={25}
            onCollapse={() => setIsChatOpen(false)}
            onExpand={() => setIsChatOpen(true)}
          >
            <div className='flex-1 flex-grow bg-accent/50 w-full'>
              <ChatInterface
                canvasId={id}
                sessionList={sessionList}
                setSessionList={setSessionList}
                sessionId={searchSessionId}
                onCollapse={() => chatPanelRef.current?.collapse()}
              />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
        {!isChatOpen && (
          <div className='absolute bottom-4 right-4 z-50'>
            <Button
              size='icon'
              className='rounded-full h-12 w-12 shadow-lg'
              onClick={() => chatPanelRef.current?.resize(25)}
            >
              <MessageSquare className='h-6 w-6' />
            </Button>
          </div>
        )}
      </div>
    </CanvasProvider>
  )
}
