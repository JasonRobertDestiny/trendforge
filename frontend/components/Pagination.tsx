import Link from 'next/link'

interface Props {
  current: number
  total: number
  pageSize: number
  basePath: string
}

export default function Pagination({ current, total, pageSize, basePath }: Props) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  if (totalPages <= 1) return null

  const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1)

  const separator = basePath.includes('?') ? '&' : '?'

  return (
    <div className="mt-6 flex flex-wrap items-center gap-2 text-sm">
      {pageNumbers.map((page) => (
        <Link
          key={page}
          href={`${basePath}${separator}page=${page}`}
          className={`rounded-lg px-3 py-1 ${
            page === current
              ? 'bg-teal-600 text-white'
              : 'bg-slate-100 text-slate-700 hover:bg-teal-100'
          }`}
        >
          {page}
        </Link>
      ))}
    </div>
  )
}
