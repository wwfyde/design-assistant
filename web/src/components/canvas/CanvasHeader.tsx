import { Input } from '@/components/ui/input'
import { useNavigate } from '@tanstack/react-router'
import { ArrowLeft } from 'lucide-react'
import TopMenu from '../TopMenu'
import CanvasExport from './CanvasExport'

type CanvasHeaderProps = {
  canvasName: string
  canvasId: string
  onNameChange: (name: string) => void
  onNameSave: () => void
}

const CanvasHeader: React.FC<CanvasHeaderProps & { returnTab?: string }> = ({
  canvasName,
  canvasId,
  onNameChange,
  onNameSave,
  returnTab,
}) => {
  const navigate = useNavigate()
  const BackButton = (
    <button
      onClick={() => navigate({ to: '/', search: returnTab ? { tab: returnTab } : undefined })}
      className='p-1.5 -ml-1.5 hover:bg-secondary rounded-full transition-colors flex items-center justify-center'
      title='Back to Home'
    >
      <ArrowLeft size={18} />
    </button>
  )

  return (
    <TopMenu
      left={BackButton}
      middle={
        <Input
          className='text-sm text-muted-foreground text-center bg-transparent border-none shadow-none w-fit h-7 hover:bg-primary-foreground transition-all'
          value={canvasName}
          onChange={(e) => onNameChange(e.target.value)}
          onBlur={onNameSave}
        />
      }
      right={<CanvasExport />}
    />
  )
}

export default CanvasHeader
