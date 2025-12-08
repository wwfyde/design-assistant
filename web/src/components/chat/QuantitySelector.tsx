import { Button } from '@/components/ui/button'
import { ChevronDown, Hash } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'

interface QuantitySelectorProps {
  value: number
  onChange: (value: number) => void
  max?: number
}

const QuantitySelector: React.FC<QuantitySelectorProps> = ({ value, onChange, max = 30 }) => {
  const { t } = useTranslation()
  const quantitySliderRef = useRef<HTMLDivElement>(null)
  const [showQuantitySlider, setShowQuantitySlider] = useState(false)

  // Close quantity slider when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (quantitySliderRef.current && !quantitySliderRef.current.contains(event.target as Node)) {
        setShowQuantitySlider(false)
      }
    }

    if (showQuantitySlider) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showQuantitySlider])

  return (
    <div className='relative' ref={quantitySliderRef}>
      <Button
        variant='outline'
        className='flex items-center gap-1'
        onClick={() => setShowQuantitySlider(!showQuantitySlider)}
        size={'sm'}
      >
        <Hash className='size-4' />
        <span className='text-sm'>{value}</span>
        <ChevronDown className='size-3 opacity-50' />
      </Button>

      {/* Quantity Slider */}
      <AnimatePresence>
        {showQuantitySlider && (
          <motion.div
            className='absolute bottom-full mb-2 left-0  bg-background border border-border rounded-lg p-4 shadow-lg min-w-48'
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
          >
            <div className='flex flex-col gap-3'>
              <div className='flex items-center justify-between'>
                <span className='text-sm font-medium'>{t('chat:textarea.quantity', 'Image Quantity')}</span>
                <span className='text-sm text-muted-foreground'>{value}</span>
              </div>
              <div className='flex items-center gap-3'>
                <span className='text-xs text-muted-foreground'>1</span>
                <input
                  type='range'
                  min='1'
                  max={max}
                  value={value}
                  onChange={(e) => onChange(Number(e.target.value))}
                  className='flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer
                                  [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                                  [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary
                                  [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-sm
                                  [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full
                                  [&::-moz-range-thumb]:bg-primary [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:border-0'
                />
                <span className='text-xs text-muted-foreground'>{max}</span>
              </div>
            </div>
            {/* Arrow pointing down */}
            <div className='absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-border'></div>
            <div className='absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-background translate-y-[-1px]'></div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default QuantitySelector
