// Chat Components
export { default as ChatInterface } from './components/chat/Chat'
export { default as ChatHistory } from './components/chat/ChatHistory'
export { default as ChatMagicGenerator } from './components/chat/ChatMagicGenerator'
export { default as ChatTextarea } from './components/chat/ChatTextarea'
// export { default as ModelSelector } from './components/chat/ModelSelector'
export { default as ModelSelectorV2 } from './components/chat/ModelSelectorV2'
export { default as SessionSelector } from './components/chat/SessionSelector'
export { default as ChatSpinner } from './components/chat/Spinner'

// UI Components
export { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar'
export { Badge } from './components/ui/badge'
export { Button, buttonVariants } from './components/ui/button'
export { Card, CardAction, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './components/ui/card'
export { Input } from './components/ui/input'
export { ResizableHandle, ResizablePanel, ResizablePanelGroup } from './components/ui/resizable'
export { ScrollArea } from './components/ui/scroll-area'
export { Separator } from './components/ui/separator'
export { default as ShinyText } from './components/ui/shiny-text'
export { Skeleton } from './components/ui/skeleton'
export { Switch } from './components/ui/switch'
export { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './components/ui/tooltip'

// Dialog Components
export {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogOverlay,
  DialogPortal,
  DialogTitle,
  DialogTrigger,
} from './components/ui/dialog'

// Dropdown Components
export {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from './components/ui/dropdown-menu'

// Select Components
export {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectScrollDownButton,
  SelectScrollUpButton,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from './components/ui/select'

// Context Menu Components
export {
  ContextMenu,
  ContextMenuCheckboxItem,
  ContextMenuContent,
  ContextMenuGroup,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuPortal,
  ContextMenuRadioGroup,
  ContextMenuRadioItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from './components/ui/context-menu'

// Sheet Components
export {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from './components/ui/sheet'

// Sidebar Components
export {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupAction,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInput,
  SidebarInset,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSkeleton,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarProvider,
  SidebarRail,
  SidebarSeparator,
  SidebarTrigger,
  useSidebar,
} from './components/ui/sidebar'

// Auth Components
export { LoginDialog } from './components/auth/LoginDialog'
export { UserMenu } from './components/auth/UserMenu'

// Common Components
export { default as Blur } from './components/common/Blur'
export { default as ErrorBoundary } from './components/common/ErrorBoundary'

// Theme Components
export { default as ThemeButton } from './components/theme/ThemeButton'
export { ThemeProvider } from './components/theme/ThemeProvider'

// Types
export type { AssistantMessage, ChatSession, Message, MessageContent, Model, PendingType, Session } from './types/types'

// Contexts
export { AuthProvider, useAuth } from './contexts/AuthContext'
export { CanvasProvider, useCanvas } from './contexts/canvas'
export { ConfigsProvider, useConfigs } from './contexts/configs'

// Hooks
export { useBalance } from './hooks/use-balance'
export { default as useDebounce } from './hooks/use-debounce'
export { useLanguage } from './hooks/use-language'
export { useTheme } from './hooks/use-theme'

// Utils
export { eventBus } from './lib/event'
export { cn } from './lib/utils'
export { formatDate } from './utils/formatDate'
export { compressImageFile, processImageFiles } from './utils/imageUtils'
export { isPNGFile, readPNGMetadata } from './utils/pngMetadata'

// API
export { createCanvas, getCanvas, renameCanvas } from './api/canvas'
export { sendMessages } from './api/chat'
export { listModels } from './api/model'
export type { ModelInfo, ToolInfo } from './api/model'
export { uploadImage } from './api/upload'
