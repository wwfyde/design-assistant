import { getHuabanCollectionItems, getHuabanCollections, HuabanCollection } from '@/api/huaban'
import { useQuery } from '@tanstack/react-query'
import { clsx } from 'clsx'
import { useState } from 'react'

export const HuabanList = () => {
    const [selectedBoardId, setSelectedBoardId] = useState<number | null>(null)

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
        enabled: !!activeBoardId,
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
        return `${minutes}分钟前`;
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
                                            <div key={board.board_id} className="group cursor-pointer">
                                                <div className="aspect-[3/2] rounded-lg overflow-hidden bg-muted mb-2 relative">
                                                    <div className="grid grid-cols-3 gap-0.5 h-full w-full">
                                                        {/* Left Large Cover */}
                                                        <div className="col-span-2 h-full relative bg-gray-200 dark:bg-gray-700">
                                                            {board.cover?.file?.key ? (
                                                                <img
                                                                    src={`/huaban-img/${board.cover.file.key}_sq235`}
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
