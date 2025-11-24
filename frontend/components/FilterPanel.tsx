import Link from 'next/link'

interface FilterPanelProps {
  categories: string[]
}

export default function FilterPanel({ categories }: FilterPanelProps) {
  const rendered = categories.length ? categories : ['科技', 'AI', '安全']
  return (
    <div className="rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-800">分类筛选</h3>
      <div className="mt-3 flex flex-wrap gap-2">
        {rendered.map((cat) => (
          <Link
            key={cat}
            href={`/search?category=${encodeURIComponent(cat)}`}
            className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700 transition hover:bg-teal-100"
          >
            {cat}
          </Link>
        ))}
      </div>
      <div className="mt-4 text-xs text-slate-500">
        点击分类跳转搜索，支持与关键词组合查询。
      </div>
    </div>
  )
}
