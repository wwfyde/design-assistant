import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { useLanguage } from '@/hooks/use-language'
import { Languages } from 'lucide-react'
import { useTranslation } from 'react-i18next'

const LanguageSwitcher = () => {
  const { changeLanguage, currentLanguage } = useLanguage()
  const { t } = useTranslation()

  const languages = [
    { code: 'en', name: t('common:languages.en') },
    { code: 'zh-CN', name: t('common:languages.zh-CN') },
  ]

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button size={'sm'} variant={'ghost'}>
          <Languages size={30} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align='end'>
        {languages.map((language) => (
          <DropdownMenuItem
            key={language.code}
            onClick={() => changeLanguage(language.code)}
            className={currentLanguage === language.code ? 'bg-accent' : ''}
          >
            {language.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default LanguageSwitcher
