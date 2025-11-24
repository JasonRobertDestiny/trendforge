'use client'

import { useEffect, useState } from 'react'
import { ChevronRight } from 'lucide-react'

interface TocItem {
  id: string
  text: string
  level: number
}

export default function TableOfContents() {
  const [headings, setHeadings] = useState<TocItem[]>([])
  const [activeId, setActiveId] = useState<string>('')

  useEffect(() => {
    // 获取所有标题
    const elements = document.querySelectorAll('.prose h2, .prose h3, .prose h4')
    const items: TocItem[] = []

    elements.forEach((elem) => {
      const id = elem.id || elem.textContent?.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '') || ''
      if (!elem.id) {
        elem.id = id
      }

      items.push({
        id,
        text: elem.textContent || '',
        level: parseInt(elem.tagName[1]),
      })
    })

    setHeadings(items)

    // 监听滚动更新当前激活的标题
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
          }
        })
      },
      {
        rootMargin: '-20% 0% -70% 0%',
      }
    )

    elements.forEach((elem) => observer.observe(elem))

    return () => {
      elements.forEach((elem) => observer.unobserve(elem))
    }
  }, [])

  const scrollToHeading = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      const offset = 80 // 顶部留出空间
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.scrollY - offset

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      })
    }
  }

  if (headings.length === 0) {
    return null
  }

  return (
    <nav className="sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto">
      <div className="rounded-2xl glass p-6">
        <h3 className="mb-4 text-sm font-bold text-slate-900">目录导航</h3>
        <ul className="space-y-2 text-sm">
          {headings.map((heading) => (
            <li
              key={heading.id}
              style={{ paddingLeft: `${(heading.level - 2) * 12}px` }}
            >
              <button
                onClick={() => scrollToHeading(heading.id)}
                className={`group flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left transition-all duration-200 hover:bg-teal-50 ${
                  activeId === heading.id
                    ? 'bg-gradient-to-r from-teal-50 to-blue-50 text-teal-700 font-medium'
                    : 'text-slate-600'
                }`}
              >
                <ChevronRight
                  size={12}
                  className={`transition-transform duration-200 ${
                    activeId === heading.id ? 'rotate-90' : ''
                  }`}
                />
                <span className="line-clamp-2">{heading.text}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* 快捷操作 */}
      <div className="mt-6 rounded-2xl glass p-6">
        <h3 className="mb-4 text-sm font-bold text-slate-900">快捷操作</h3>
        <div className="space-y-2">
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="w-full rounded-lg bg-gradient-to-r from-slate-100 to-zinc-100 px-3 py-2 text-sm text-slate-700 transition-all hover:from-teal-100 hover:to-blue-100"
          >
            回到顶部
          </button>
          <button
            onClick={() => window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' })}
            className="w-full rounded-lg bg-gradient-to-r from-slate-100 to-zinc-100 px-3 py-2 text-sm text-slate-700 transition-all hover:from-teal-100 hover:to-blue-100"
          >
            跳到底部
          </button>
        </div>
      </div>
    </nav>
  )
}