import { listPrompts } from '@/api/prompt'
import { Button } from '@/components/ui/button'
import { useInfiniteQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { motion } from 'motion/react'
import { PromptCard } from './PromptCard'

export function PromptList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, status } = useInfiniteQuery({
    queryKey: ['prompts'],
    queryFn: ({ pageParam = 0 }) => listPrompts(pageParam, 20),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      return lastPage.length === 20 ? allPages.length * 20 : undefined
    },
  })

  if (status === 'pending') {
    return (
      <div className='flex justify-center py-8'>
        <Loader2 className='h-8 w-8 animate-spin' />
      </div>
    )
  }

  if (status === 'error') {
    return <div className='text-center py-8 text-red-500'>Error loading prompts</div>
  }

  return (
    <section className='w-full max-w-5xl mx-auto py-8 md:py-10 px-4'>
      <motion.div
        className='text-2xl font-bold my-2'
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        Prompt库
      </motion.div>
      <div className='columns-1 sm:columns-2 md:columns-4 gap-8 space-y-8'>
        {data.pages.map((page) =>
          page.map((prompt) => (
            <div key={prompt.id} className='break-inside-avoid'>
              <PromptCard prompt={prompt} />
            </div>
          )),
        )}
      </div>
      {hasNextPage && (
        <div className='flex justify-center mt-8'>
          <Button onClick={() => fetchNextPage()} disabled={isFetchingNextPage} variant='outline'>
            {isFetchingNextPage ? (
              <>
                <Loader2 className='mr-2 h-4 w-4 animate-spin' />
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
