import { searchArticles, getAllArticles } from '@/lib/markdown'
import { ArticleMetadata } from '@/lib/types'
import ArticleCard from '@/components/ArticleCard'
import Pagination from '@/components/Pagination'

const PAGE_SIZE = 12

export default async function SearchPage({ searchParams }: { searchParams: { q?: string; category?: string; page?: string } }) {
  const query = searchParams.q?.trim() || ''
  const category = searchParams.category?.trim()
  const page = Number(searchParams.page || '1') || 1

  let results: ArticleMetadata[] = []
  if (query) {
    results = await searchArticles(query)
  } else {
    results = await getAllArticles()
  }

  if (category) {
    results = results.filter((item) => item.category === category)
  }

  const total = results.length
  const paged = results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <div className="space-y-6 py-6">
      <header className="rounded-3xl border border-slate-200 bg-white/80 px-5 py-4 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-900">搜索结果</h1>
        <p className="text-sm text-slate-600">
          关键词：{query || '（未输入，显示全部）'}
          {category ? ` · 分类：${category}` : ''} · 共 {total} 篇
        </p>
      </header>

      {paged.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 bg-white/80 p-6 text-slate-600">
          暂无匹配结果。
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {paged.map((article) => (
            <ArticleCard key={article.slug} article={article} />
          ))}
        </div>
      )}

      <Pagination current={page} total={total} pageSize={PAGE_SIZE} basePath={`/search${buildQuery(query, category)}`} />
    </div>
  )
}

function buildQuery(q: string, category?: string) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (category) params.set('category', category)
  const prefix = params.toString()
  return prefix ? `?${prefix}` : ''
}
