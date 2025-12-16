import { listCanvases } from '@/api/canvas'
import CanvasCard from '@/components/home/CanvasCard'
import { useQuery } from '@tanstack/react-query'
import { useLocation, useNavigate } from '@tanstack/react-router'
import { AnimatePresence, motion } from 'motion/react'
import { memo } from 'react'
import { useTranslation } from 'react-i18next'

const CanvasList: React.FC = () => {
  const { t } = useTranslation()
  const location = useLocation()
  const isHomePage = location.pathname === '/'

  const { data: canvases, refetch } = useQuery({
    queryKey: ['canvases'],
    queryFn: listCanvases,
    enabled: isHomePage, // 每次进入首页时都重新查询
    refetchOnMount: 'always',
  })

  const navigate = useNavigate()
  const handleCanvasClick = (id: string) => {
    navigate({ to: '/canvas/$id', params: { id }, search: { returnTab: 'history' } })
  }

  return (
    <div className='flex flex-col px-4 mt-10 gap-4'>
      {canvases && canvases.length > 0 && (
        <motion.span
          className='text-2xl font-bold '
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {t('home:allProjects')}
        </motion.span>
      )}

      <AnimatePresence>
        <div className='grid grid-cols-5 gap-4 w-full pb-4'>
          {canvases && canvases?.map((canvas, index) => (
            <CanvasCard
              key={canvas.id}
              index={index}
              canvas={canvas}
              handleCanvasClick={handleCanvasClick}
              handleDeleteCanvas={() => refetch()}
            />
          ))}
        </div>
      </AnimatePresence>
    </div>
  )
}

export default memo(CanvasList)
