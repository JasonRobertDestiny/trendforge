'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Search } from 'lucide-react'

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    router.push(`/search?q=${encodeURIComponent(query.trim())}`)
  }

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="搜索文章..."
        className="w-full rounded-xl border border-slate-200 bg-white/80 px-4 py-2 pl-10 shadow-sm focus:border-teal-400 focus:outline-none"
      />
      <Search size={18} className="absolute left-3 top-2.5 text-slate-400" />
      <button
        type="submit"
        className="absolute right-2 top-1.5 rounded-lg bg-gradient-to-r from-teal-500 to-accent px-3 py-1 text-sm font-semibold text-white shadow"
      >
        搜索
      </button>
    </form>
  )
}
