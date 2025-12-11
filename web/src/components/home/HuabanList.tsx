import { getHuabanCollectionItems, getHuabanCollections, getHuabanBoardDetail, HuabanCollection, HuabanBoardDetailResponse, HuabanPin } from '@/api/huaban'
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { clsx } from 'clsx'
import { useState } from 'react'
import { ArrowLeft, Image as ImageIcon, Sparkles } from 'lucide-react'
import { eventBus } from '@/lib/event'

const PinItem = ({ pin }: { pin: HuabanPin }) => {
    const [isOpen, setIsOpen] = useState(false)
    const [copyState, setCopyState] = useState<string | null>(null)

    const handleCopy = (text: string, pId: number) => {
        console.log('pId', pId)
        navigator.clipboard.writeText(text)
        setCopyState('copied')
        setTimeout(() => setCopyState(null), 2000)
    }

    const handleUsePrompt = (text: string, pId: number) => {
        console.log('pId', pId)
        eventBus.emit('Chat::SetPrompt', { prompt: text })
        eventBus.emit('Chat::ScrollToTop')
        setIsOpen(false)
    }

    const handleUseImage = (url: string, pId: number, text?: string) => {
        console.log('pId', pId)
        eventBus.emit('Chat::Clear')
        eventBus.emit('Chat::AddImageFromUrl', { url })
        if (text) {
            eventBus.emit('Chat::SetPrompt', { prompt: text })
        }
        eventBus.emit('Chat::ScrollToTop')
        setIsOpen(false)
    }

    const imageUrl = `https://gd-hbimg.huaban.com/${pin.file.key}_fw658`

    return (
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <div
                className="break-inside-avoid relative rounded-lg overflow-hidden bg-secondary mb-4 group hover:shadow-lg transition-all duration-300"
                style={{ aspectRatio: `${pin.file.width} / ${pin.file.height}` }}
            >
                <img
                    src={`/huaban-img/${pin.file.key}_fw240webp`}
                    srcSet={`/huaban-img/${pin.file.key}_fw240webp 1x, /huaban-img/${pin.file.key}_fw480webp 2x`}
                    alt={pin.raw_text}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                    onError={(e) => {
                        (e.target as HTMLImageElement).src = `https://gd-hbimg.huaban.com/${pin.file.key}_fw240webp`
                    }}
                />

                <div className='absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center'>
                    <DialogTrigger asChild>
                        <Button
                            variant='secondary'
                            className='rounded-full px-6 font-semibold bg-white text-black hover:bg-white/90 shadow-lg transform translate-y-4 group-hover:translate-y-0 transition-all duration-300'
                        >
                            View Details
                        </Button>
                    </DialogTrigger>
                </div>

                {pin.raw_text && (
                    <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/60 to-transparent text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                        <p className="truncate">{pin.raw_text}</p>
                    </div>
                )}
            </div>

            <DialogContent className='max-w-5xl p-0 overflow-hidden gap-0 sm:rounded-3xl border-none bg-background'>
                <div className='grid md:grid-cols-2 h-[80vh] md:h-[600px] m-1'>
                    <div className='h-full bg-muted relative overflow-hidden flex items-center justify-center p-4 bg-black/5'>
                        <img
                            src={`/huaban-img/${pin.file.key}_fw658`}
                            onError={(e) => {
                                (e.target as HTMLImageElement).src = imageUrl
                            }}
                            alt={pin.raw_text}
                            className='w-full h-full object-contain'
                        />
                    </div>
                    <div className='flex flex-col h-full overflow-hidden'>
                        <div className='p-8 md:p-10 flex-1 overflow-y-auto'>
                            <div className='mb-8'>
                                <DialogTitle className='text-xl font-bold mb-6 leading-relaxed line-clamp-2'>{pin.raw_text || 'No Title'}</DialogTitle>

                                <div className='flex flex-col gap-4'>
                                    <div className='flex items-center justify-between'>
                                        <span className='text-xs font-bold text-muted-foreground tracking-wider uppercase'>
                                            Actions
                                        </span>
                                        <div className='flex gap-2 flex-wrap justify-end'>
                                            <Button
                                                variant='outline'
                                                size='sm'
                                                className='h-8 rounded-full text-xs px-3 gap-1.5 hover:bg-primary hover:text-primary-foreground transition-colors'
                                                onClick={() => handleUsePrompt(pin.raw_text, pin.pin_id)}
                                            >
                                                <Sparkles className='w-3.5 h-3.5' />
                                                做同款
                                            </Button>
                                            <Button
                                                variant='outline'
                                                size='sm'
                                                className='h-8 rounded-full text-xs px-3 gap-1.5 hover:bg-primary hover:text-primary-foreground transition-colors'
                                                onClick={() => handleUseImage(imageUrl, pin.pin_id, pin.raw_text)}
                                            >
                                                <ImageIcon className='w-3.5 h-3.5' />
                                                参考作图
                                            </Button>
                                            <Button
                                                variant='outline'
                                                size='sm'
                                                className='h-8 rounded-full text-xs px-4'
                                                onClick={() => handleCopy(pin.raw_text, pin.pin_id)}
                                            >
                                                {copyState === 'copied' ? 'Copied!' : 'Copy'}
                                            </Button>
                                        </div>
                                    </div>
                                    <div className='text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap bg-muted/50 p-4 rounded-lg border'>
                                        {pin.raw_text || 'No description available'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}

const BoardDetailView = ({ boardId, onBack }: { boardId: number, onBack: () => void }) => {
    const {
        data,
        isLoading,
        error,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage
    } = useInfiniteQuery<HuabanBoardDetailResponse>({
        queryKey: ['huaban-board-detail', boardId],
        queryFn: ({ pageParam }) => getHuabanBoardDetail(boardId, pageParam as number | undefined),
        initialPageParam: undefined,
        getNextPageParam: (lastPage) => {
            try {
                const pins = lastPage?.pins;
                if (!pins || !Array.isArray(pins) || pins.length === 0) return undefined;
                return pins[pins.length - 1]?.pin_id;
            } catch (e) {
                console.error("getNextPageParam error:", e);
                return undefined;
            }
        },
        staleTime: 60000,
    })

    if (isLoading) return <div className="p-4">加载中...</div>
    if (error) return <div className="p-4 text-red-500">Error: {(error as Error).message}</div>
    if (!data) return <div className="p-4">No data found</div>

    const board = data?.pages?.[0]?.board;
    const allPins = data?.pages?.flatMap(page => (page?.pins && Array.isArray(page.pins)) ? page.pins : []) || [];

    return (
        <div className="flex flex-col h-full">
            <div className="sticky top-0 z-10 bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 py-1 border-b flex items-center gap-2">
                <button
                    onClick={onBack}
                    className="p-1.5 -ml-1.5 hover:bg-secondary rounded-full transition-colors"
                    title="Back to Collections"
                >
                    <ArrowLeft size={18} />
                </button>
                <div className="flex flex-col">
                    <h6 className="text-base font-semibold text-foreground">{board?.title}</h6>
                    <span className="text-[10px] text-muted-foreground">{board?.pin_count || 0} 采集</span>
                </div>
            </div>

            <div className="p-4">
                <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-6 gap-4 space-y-4">
                    {allPins.map((pin) => (
                        <PinItem key={pin.pin_id} pin={pin} />
                    ))}
                </div>

                <div className="flex items-center justify-center w-full mt-4 pb-8">
                    {hasNextPage ? (
                        <button
                            onClick={() => fetchNextPage()}
                            disabled={isFetchingNextPage}
                            className="px-6 py-2 bg-secondary hover:bg-secondary/80 rounded-full text-sm transition-colors cursor-pointer"
                        >
                            {isFetchingNextPage ? '加载中...' : '加载更多'}
                        </button>
                    ) : (
                        allPins.length > 0 && <div className="text-sm text-muted-foreground">没有更多信息啦!</div>
                    )}
                </div>
            </div>
        </div>
    )
}

export const HuabanList = () => {
    const [selectedBoardId, setSelectedBoardId] = useState<number | null>(null) // Collection ID
    const [viewBoardId, setViewBoardId] = useState<number | null>(null) // Board Detail ID

    const { data, isLoading, error } = useQuery({
        queryKey: ['huaban-collections'],
        queryFn: getHuabanCollections,
        staleTime: 60000,
    })

    const collections = data?.collections || []
    const activeBoardId = selectedBoardId ?? collections[0]?.collection_id

    const {
        data: pinsData,
        isLoading: pinsLoading,
        error: pinsError,
        isFetching: pinsFetching
    } = useQuery({
        queryKey: ['huaban-pins', activeBoardId],
        queryFn: () => getHuabanCollectionItems(activeBoardId as number),
        enabled: !!activeBoardId && !viewBoardId, // Disable queries if viewing detail
        staleTime: 60000,
    })

    const boards = pinsData?.user.boards || []

    const formatTimeAgo = (timestamp: number) => {
        const diff = Date.now() - timestamp * 1000;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const months = Math.floor(diff / (1000 * 60 * 60 * 24 * 30));
        const years = Math.floor(diff / (1000 * 60 * 60 * 24 * 365));
        if (years > 0) return `${years}年前`;
        if (months > 0) return `${months}月前`;
        if (days > 0) return `${days}天前`;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        if (hours > 0) return `${hours}小时前`;
        const minutes = Math.floor(diff / (1000 * 60));
        return minutes > 0 ? `${minutes}分钟前` : '刚刚';
    }

    if (viewBoardId) {
        return <BoardDetailView boardId={viewBoardId} onBack={() => setViewBoardId(null)} />
    }

    return (
        <div className="flex flex-col gap-4 p-4">
            {isLoading && <div>Loading collections...</div>}
            {error && <div className="text-red-500">Error loading collections: {(error as Error).message}</div>}
            {pinsError && <div className="text-red-500">Error loading items: {(pinsError as Error).message}</div>}

            {!isLoading && !error && (
                <>
                    <div className="moRN678s g2L3AgN7 flex flex-wrap gap-2" id="collection-list-left">
                        {collections.map((collection: HuabanCollection) => (
                            <div
                                key={collection.collection_id}
                                className={clsx("BF0paWp2 cursor-pointer px-3 py-1 rounded-md transition-colors", activeBoardId === collection.collection_id ? "wn9WOlYy bg-red-600 text-white font-medium shadow-sm" : "bg-secondary hover:bg-secondary/80")}
                                title={collection.title}
                                onClick={() => setSelectedBoardId(collection.collection_id)}
                            >
                                {collection.title}
                            </div>
                        ))}
                    </div>

                    <div className="mt-4">
                        {pinsLoading ? (
                            <div>Loading content...</div>
                        ) : (
                            <div className="flex flex-col gap-8">
                                {boards.length > 0 && (
                                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                                        {boards.map((board) => (
                                            <div key={board.board_id} className="group cursor-pointer" onClick={() => setViewBoardId(board.board_id)}>
                                                <div className="aspect-[3/2] rounded-lg overflow-hidden bg-muted mb-2 relative">
                                                    <div className="grid grid-cols-3 gap-0.5 h-full w-full">
                                                        {/* Left Large Cover */}
                                                        <div className="col-span-2 h-full relative bg-gray-200 dark:bg-gray-700">
                                                            {board.cover?.file?.key ? (
                                                                <img
                                                                    src={`/huaban-img/${board.cover.file.key}_sq235`}
                                                                    srcSet={`/huaban-img/${board.cover.file.key}_sq235 1x, /huaban-img/${board.cover.file.key}_sq235 2x`}
                                                                    alt={board.title}
                                                                    className="w-full h-full object-cover"
                                                                    onError={(e) => {
                                                                        (e.target as HTMLImageElement).src = `https://gd-hbimg.huaban.com/${board.cover.file.key}_sq235`
                                                                    }}
                                                                />
                                                            ) : (
                                                                <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                                                                    No Cover
                                                                </div>
                                                            )}
                                                        </div>

                                                        {/* Right Stacked Pins */}
                                                        <div className="col-span-1 flex flex-col gap-0.5 h-full">
                                                            {/* Top Pin */}
                                                            <div className="relative w-full h-full flex-1 bg-gray-200 dark:bg-gray-700">
                                                                {board.pins?.[0]?.file?.key && (
                                                                    <img
                                                                        src={`/huaban-img/${board.pins[0].file.key}_sq235`}
                                                                        alt=""
                                                                        className="w-full h-full object-cover"
                                                                        onError={(e) => {
                                                                            (e.target as HTMLImageElement).src = `https://gd-hbimg.huaban.com/${board.pins![0].file.key}_sq235`
                                                                        }}
                                                                    />
                                                                )}
                                                            </div>
                                                            {/* Bottom Pin */}
                                                            <div className="relative w-full h-full flex-1 bg-gray-200 dark:bg-gray-700">
                                                                {board.pins?.[1]?.file?.key && (
                                                                    <img
                                                                        src={`/huaban-img/${board.pins[1].file.key}_sq235`}
                                                                        alt=""
                                                                        className="w-full h-full object-cover"
                                                                        onError={(e) => {
                                                                            (e.target as HTMLImageElement).src = `https://gd-hbimg.huaban.com/${board.pins![1].file.key}_sq235`
                                                                        }}
                                                                    />
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex items-center justify-between gap-2 mt-2">
                                                    <div className="font-medium truncate text-sm flex-1" title={board.title}>{board.title}</div>
                                                    <div className="text-xs text-muted-foreground whitespace-nowrap">
                                                        {board.pin_count} 采集 · {formatTimeAgo(board.updated_at)}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {boards.length === 0 && (
                                    <div className="text-center text-muted-foreground py-10">No content found.</div>
                                )}
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    )
}
