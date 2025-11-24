import Link from 'next/link'
import SearchBar from './SearchBar'

export default function Navigation() {
  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center space-x-2">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-teal-500 via-accent to-amber-400 shadow" />
          <span className="text-lg font-semibold text-slate-900">TrendForge</span>
        </Link>
        <div className="mx-6 hidden w-2/5 md:block">
          <SearchBar />
        </div>
        <div className="text-xs text-slate-600">
          今日更新 <span className="font-semibold text-slate-900">素材库</span>
        </div>
      </div>
    </nav>
  )
}
