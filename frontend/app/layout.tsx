import type { Metadata } from 'next'
import { Noto_Sans_SC, Manrope } from 'next/font/google'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import './globals.css'

const noto = Noto_Sans_SC({ subsets: ['latin'] })
const manrope = Manrope({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TrendForge - AI驱动的素材库',
  description: '每日自动更新的深度科技分析文章',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className={`${noto.className} ${manrope.className} bg-sand text-slate-900`}>
        <Navigation />
        <main className="mx-auto min-h-screen max-w-6xl px-4 pb-12">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
