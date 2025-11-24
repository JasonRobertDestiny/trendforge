import { getAllArticles } from '@/lib/markdown'
import { getCategories } from '@/lib/articles'
import ArticleCard from '@/components/ArticleCard'
import FilterPanel from '@/components/FilterPanel'

export default async function HomePage() {
  const articles = await getAllArticles()
  const categories = await getCategories()
  const recent = articles.slice(0, 12)
  const lastUpdated = articles[0]?.date || new Date().toISOString()

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-br from-teal-500/15 via-white to-amber-100 px-6 py-10 shadow-sm">
        <div className="max-w-3xl space-y-3">
          <p className="text-sm font-semibold text-teal-700">每日深度素材</p>
          <h1 className="text-3xl font-bold text-slate-900 md:text-4xl">TrendForge 素材库</h1>
          <p className="text-lg text-slate-700">自动抓取热点 + DR 深研，供运营与写作团队快速选用。</p>
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <span className="rounded-full bg-white/70 px-3 py-1 shadow">总计 {articles.length} 篇</span>
            <span className="text-slate-500">最后更新：{new Date(lastUpdated).toLocaleDateString('zh-CN')}</span>
          </div>
        </div>
        <div className="pointer-events-none absolute -right-10 -top-10 h-48 w-48 rounded-full bg-gradient-to-br from-teal-300/40 to-amber-200/60 blur-3xl" />
      </section>

      <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
        <FilterPanel categories={categories} />

        <div className="space-y-4">
          <div className="flex items-baseline justify-between">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">最新文章</h2>
              <p className="text-sm text-slate-600">精选最近 12 篇深度内容</p>
            </div>
          </div>

          {recent.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-200 bg-white/80 p-6 text-slate-600">
              暂无文章，等待后端生成内容。
            </div>
          ) : (
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              {recent.map((article) => (
                <ArticleCard key={article.slug} article={article} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
