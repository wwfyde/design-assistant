import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import {
    ChevronDown,
    Link as LinkIcon,
    Monitor,
    SlashSquare,
    Smartphone,
    Square,
    SquareSquare,
    Unlink,
} from 'lucide-react'
import { useEffect, useState } from 'react'

export type ImageSize = '1K' | '2K' | '4K'
export type AspectRatio = '1:1' | '16:9' | '9:16' | '4:3' | '3:4' | '3:2' | '2:3' | '21:9' | 'Auto'

const ASPECT_RATIOS: { value: AspectRatio; label: string; icon: React.ForwardRefExoticComponent<any> }[] = [
    { value: 'Auto', label: 'Auto', icon: SlashSquare },
    { value: '1:1', label: '1:1', icon: Square },
    { value: '21:9', label: '21:9', icon: Monitor },
    { value: '16:9', label: '16:9', icon: Monitor }, // Approximate icon
    { value: '3:2', label: '3:2', icon: Monitor },
    { value: '4:3', label: '4:3', icon: Monitor },
    { value: '3:4', label: '3:4', icon: Smartphone },
    { value: '2:3', label: '2:3', icon: Smartphone },
    { value: '9:16', label: '9:16', icon: Smartphone },
]

interface ImageConfigSelectorProps {
    aspectRatio: AspectRatio
    imageSize: ImageSize
    width: number
    height: number
    lock: boolean
    onChange: (config: {
        aspectRatio: AspectRatio
        imageSize: ImageSize
        width: number
        height: number
        lock: boolean
    }) => void
}

export function calculateDimensions(aspectRatio: string | null, imageSize: string): { width: number; height: number } {
    let base = 2
    switch (imageSize) {
        case '1K':
            base = 1
            break
        case '2K':
            base = 2
            break
        case '4K':
            base = 4
            break
        default:
            base = 2
    }

    let width = 1024 * base
    let height = 1024 * base

    if (aspectRatio) {
        const parts = aspectRatio.replace(':', '×').split('×')
        if (parts.length === 2) {
            const w = parseInt(parts[0])
            const h = parseInt(parts[1])

            if (w === 1 && h === 1) {
                width = 1024 * base
                height = 1024 * base
            } else if (w === 16 && h === 9) {
                width = 1280 * base
                height = 720 * base
            } else if (w === 9 && h === 16) {
                width = 720 * base
                height = 1280 * base
            } else if (w === 4 && h === 3) {
                width = 1125 * base
                height = 864 * base
            } else if (w === 3 && h === 4) {
                width = 864 * base
                height = 1125 * base
            } else if (w === 3 && h === 2) {
                width = 1248 * base
                height = 832 * base
            } else if (w === 2 && h === 3) {
                width = 832 * base
                height = 1248 * base
            } else if (w === 21 && h === 9) {
                width = 1512 * base
                height = 648 * base
            } else {
                // Default / Fallback logic if needed, or if custom ratio passed
                width = w * 100 * base // Simplified fallback
                height = h * 100 * base
            }
        } else {
            width = 1024 * base
            height = 1024 * base
        }
    } else {
        width = 2048
        height = 2048
    }

    // Cap at 4096
    if (width > 4096) width = 4096
    if (height > 4096) height = 4096

    return { width, height }
}

export default function ImageConfigSelector({
    aspectRatio,
    imageSize,
    width,
    height,
    lock,
    onChange,
}: ImageConfigSelectorProps) {
    const [isOpen, setIsOpen] = useState(false)
    const [localWidth, setLocalWidth] = useState<number | string>(width)
    const [localHeight, setLocalHeight] = useState<number | string>(height)

    // Sync props to local state when not manual
    useEffect(() => {
        if (lock) {
            setLocalWidth(width)
            setLocalHeight(height)
        }
    }, [width, height, lock])

    const handleRatioChange = (val: string) => {
        if (!val) return
        const newRatio = val as AspectRatio
        const { width: w, height: h } = calculateDimensions(newRatio, imageSize)
        onChange({ aspectRatio: newRatio, imageSize, width: w, height: h, lock: true })
    }

    const handleSizeChange = (val: string) => {
        if (!val) return
        const newSize = val as ImageSize
        const { width: w, height: h } = calculateDimensions(aspectRatio, newSize)
        onChange({ aspectRatio, imageSize: newSize, width: w, height: h, lock: true })
    }

    const handleManualDimensionChange = (dim: 'width' | 'height', val: string) => {
        if (val === '') {
            if (dim === 'width') setLocalWidth('')
            else setLocalHeight('')
            return
        }

        const num = parseInt(val)
        if (isNaN(num)) return

        if (dim === 'width') {
            setLocalWidth(num)
            onChange({ aspectRatio, imageSize, width: num, height: typeof localHeight === 'number' ? localHeight : height, lock: false })
        } else {
            setLocalHeight(num)
            onChange({ aspectRatio, imageSize, width: typeof localWidth === 'number' ? localWidth : width, height: num, lock: false })
        }
    }

    const handleInputConfirm = () => {
        let w = localWidth
        let h = localHeight

        if (typeof w !== 'number' || isNaN(w)) {
            w = width
            setLocalWidth(w)
        }
        if (typeof h !== 'number' || isNaN(h)) {
            h = height
            setLocalHeight(h)
        }
    }

    const toggleManual = () => {
        onChange({ aspectRatio, imageSize, width: typeof localWidth === 'number' ? localWidth : width, height: typeof localHeight === 'number' ? localHeight : height, lock: !lock })
    }

    return (
        <Popover open={isOpen} onOpenChange={setIsOpen}>
            <PopoverTrigger asChild>
                <Button variant='outline' className='h-8 gap-2 bg-muted/50 px-3'>
                    {!lock ? <SquareSquare className='h-4 w-4' /> : <Square className='h-4 w-4' />}
                    {!lock ? (
                        <span>
                            {localWidth}:{localHeight}
                        </span>
                    ) : (
                        <span>{aspectRatio}</span>
                    )}
                    <span className='text-muted-foreground'>|</span>
                    <span>{imageSize}</span>
                    <ChevronDown className='h-4 w-4 opacity-50' />
                </Button>
            </PopoverTrigger>
            <PopoverContent
                className='w-60 p-4'
                align='start'
                onOpenAutoFocus={(e) => e.preventDefault()}
                onCloseAutoFocus={(e) => e.preventDefault()}
                onClick={(e) => e.stopPropagation()}
            >
                <div className='space-y-4'>
                    <div className='space-y-2'>
                        <Label className='text-xs text-muted-foreground'>分辨率</Label>
                        <ToggleGroup type='single' value={imageSize} onValueChange={handleSizeChange} className='flex w-full gap-2'>
                            {['1K', '2K', '4K'].map((size) => (
                                <ToggleGroupItem
                                    key={size}
                                    value={size}
                                    className='flex-1 h-6 data-[state=on]:bg-primary/10 data-[state=on]:text-primary border border-transparent data-[state=on]:border-primary/20'
                                >
                                    {size == '1K' && '1K'}
                                    {size == '2K' && '2K'}
                                    {size == '4K' && '4K'}
                                </ToggleGroupItem>
                            ))}
                        </ToggleGroup>
                    </div>

                    <div className='space-y-2'>
                        <Label className='text-xs text-muted-foreground'>图片比例</Label>
                        <ToggleGroup
                            type='single'
                            value={aspectRatio}
                            onValueChange={handleRatioChange}
                            className='grid grid-cols-5 gap-2'
                        >
                            {ASPECT_RATIOS.map((ratio) => (
                                <ToggleGroupItem
                                    key={ratio.value}
                                    value={ratio.value}
                                    className='flex flex-col h-auto py-2 px-1 w-full gap-1 data-[state=on]:bg-primary/10 data-[state=on]:text-primary border border-transparent data-[state=on]:border-primary/20'
                                >
                                    <ratio.icon className='h-4 w-4' />
                                    <span className='text-[10px]'>{ratio.label}</span>
                                </ToggleGroupItem>
                            ))}
                        </ToggleGroup>
                    </div>

                    <div className='space-y-2'>
                        <Label className='text-xs text-muted-foreground'>图片尺寸</Label>
                        <div className='flex items-center gap-2'>
                            <div className='relative flex-1'>
                                <span className='absolute left-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground'>W</span>
                                <Input
                                    className='pl-8 text-center h-8 text-xs'
                                    value={localWidth}
                                    onChange={(e) => handleManualDimensionChange('width', e.target.value)}
                                    onBlur={handleInputConfirm}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            handleInputConfirm()
                                            e.currentTarget.blur()
                                        }
                                    }}
                                    disabled={lock}
                                />
                            </div>

                            <Button
                                variant='ghost'
                                size='icon'
                                className='h-8 shrink-0 text-muted-foreground hover:text-foreground'
                                onClick={toggleManual}
                            >
                                {!lock ? <Unlink className='h-4 w-4' /> : <LinkIcon className='h-4 w-4' />}
                            </Button>

                            <div className='relative flex-1'>
                                <span className='absolute left-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground'>H</span>
                                <Input
                                    className='pl-8 text-center h-8 text-xs'
                                    value={localHeight}
                                    onChange={(e) => handleManualDimensionChange('height', e.target.value)}
                                    onBlur={handleInputConfirm}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            handleInputConfirm()
                                            e.currentTarget.blur()
                                        }
                                    }}
                                    disabled={lock}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </PopoverContent>
        </Popover>
    )
}
