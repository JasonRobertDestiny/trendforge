export interface Article {
  slug: string
  title: string
  date: string
  time?: string
  source: string
  source_url: string
  category: string
  tags: string[]
  excerpt: string
  content: string
  engagement_score: number
}

export interface ArticleMetadata {
  slug: string
  title: string
  date: string
  category: string
  tags: string[]
  excerpt: string
  source: string
}
