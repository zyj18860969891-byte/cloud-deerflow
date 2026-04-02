"use client"

import { useRouter, usePathname } from 'next/navigation'
import { useLocale } from 'next-intl'
import { useTranslations } from "next-intl"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const languages = [
  { value: 'en', label: 'English' },
  { value: 'zh', label: '中文' }
]

export function LanguageSwitcher() {
  const t = useTranslations('settings')
  const router = useRouter()
  const pathname = usePathname()
  const locale = useLocale()

  const handleLanguageChange = (newLocale: string) => {
    // Remove the locale from pathname if it exists
    const pathWithoutLocale = pathname.replace(/^\/[a-z]{2}/, '')
    router.push(`/${newLocale}${pathWithoutLocale}`)
  }

  return (
    <Select value={locale} onValueChange={handleLanguageChange}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder={t('language')} />
      </SelectTrigger>
      <SelectContent>
        {languages.map((lang) => (
          <SelectItem key={lang.value} value={lang.value}>
            {lang.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}