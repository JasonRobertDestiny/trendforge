import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { remark } from 'remark'
import html from 'remark-html'
import { Article, ArticleMetadata } from './types'

const articlesDirectory = path.join(process.cwd(), '../content/blog')

/**
 * 读取单篇文章并转成 HTML。
 */
export async function getArticleBySlug(slug: string): Promise<Article | null> {
  try {
    const fullPath = path.join(articlesDirectory, `${slug}.md`)
    const fileContents = fs.readFileSync(fullPath, 'utf8')
    const { data, content } = matter(fileContents)

    const processedContent = await remark().use(html).process(content)

    return {
      slug,
      content: processedContent.toString(),
      title: data.title,
      date: data.date,
      time: data.time,
      source: data.source,
      source_url: data.source_url,
      category: data.category || '科技',
      tags: data.tags || [],
      excerpt: data.excerpt || content.slice(0, 120),
      engagement_score: data.engagement_score || 0,
    }
  } catch {
    return null
  }
}

/**
 * 返回所有文章的元数据（按日期降序）。
 */
export async function getAllArticles(): Promise<ArticleMetadata[]> {
  if (!fs.existsSync(articlesDirectory)) return []
  const fileNames = fs.readdirSync(articlesDirectory)

  const articles = fileNames
    .filter((fileName) => fileName.endsWith('.md'))
    .map((fileName) => {
      const slug = fileName.replace(/\.md$/, '')
      const fullPath = path.join(articlesDirectory, fileName)
      const fileContents = fs.readFileSync(fullPath, 'utf8')
      const { data } = matter(fileContents)

      return {
        slug,
        title: data.title,
        date: data.date,
        category: data.category || '科技',
        tags: data.tags || [],
        excerpt: data.excerpt || '',
        source: data.source,
      }
    })

  return articles.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

export async function searchArticles(query: string): Promise<ArticleMetadata[]> {
  const articles = await getAllArticles()
  const q = query.toLowerCase()
  return articles.filter(
    (article) =>
      article.title.toLowerCase().includes(q) ||
      (article.excerpt && article.excerpt.toLowerCase().includes(q)) ||
      article.tags.some((tag) => tag.toLowerCase().includes(q))
  )
}

export async function getArticlesByCategory(category: string): Promise<ArticleMetadata[]> {
  const articles = await getAllArticles()
  return articles.filter((article) => article.category === category)
}

export async function getAllSlugs(): Promise<string[]> {
  if (!fs.existsSync(articlesDirectory)) return []
  return fs
    .readdirSync(articlesDirectory)
    .filter((file) => file.endsWith('.md'))
    .map((file) => file.replace(/\.md$/, ''))
}
