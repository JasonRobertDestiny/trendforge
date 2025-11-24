import { ArticleMetadata } from './types'
import { getAllArticles } from './markdown'

export async function getCategories(): Promise<string[]> {
  const articles = await getAllArticles()
  return Array.from(new Set(articles.map((a) => a.category))).filter(Boolean)
}

export function paginate<T>(list: T[], page: number, pageSize: number): T[] {
  const start = (page - 1) * pageSize
  return list.slice(start, start + pageSize)
}
