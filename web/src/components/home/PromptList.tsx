import { useInfiniteQuery } from "@tanstack/react-query"
import { listPrompts } from "@/api/prompt"
import { PromptCard } from "./PromptCard"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

export function PromptList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
  } = useInfiniteQuery({
    queryKey: ['prompts'],
    queryFn: ({ pageParam = 0 }) => listPrompts(pageParam, 20),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.length === 20 ? allPages.length * 20 : undefined
    },
  })

  if (status === 'pending') {
    return <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin" /></div>
  }

  if (status === 'error') {
    return <div className="text-center py-8 text-red-500">Error loading prompts</div>
  }

  return (
    <section className="w-full max-w-7xl mx-auto py-8 md:py-10 px-4">
      <div className="columns-1 sm:columns-2 md:columns-4 gap-6 space-y-6">
        {data.pages.map((page) =>
          page.map((prompt) => (
            <div key={prompt.id} className="break-inside-avoid">
              <PromptCard prompt={prompt} />
            </div>
          ))
        )}
      </div>
      {hasNextPage && (
        <div className="flex justify-center mt-8">
          <Button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            variant="outline"
          >
            {isFetchingNextPage ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              'Load More'
            )}
          </Button>
        </div>
      )}
    </section>
  )
}
