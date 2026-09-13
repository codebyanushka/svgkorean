import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { searchVocabulary } from '../../services/vocabLab'
import type { VocabSearchResult } from '../../types/vocabLab'
import { ApiError } from '../../services/api'
import { SearchIcon } from '../../components/icons/SimpleIcons'

function dictionaryUrl(korean: string): string {
  return `https://ko.dict.naver.com/#/search?query=${encodeURIComponent(korean)}`
}

export default function SearchPage() {
  const [searchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') ?? '')
  const [results, setResults] = useState<VocabSearchResult[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function runSearch(value: string) {
    const trimmed = value.trim()
    if (!trimmed) {
      setResults(null)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await searchVocabulary(trimmed)
      setResults(data)
    } catch (err: unknown) {
      setError(err instanceof ApiError ? err.message : 'Search failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const initial = searchParams.get('q')
    if (initial) void runSearch(initial)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function handleSearch(e?: React.FormEvent) {
    e?.preventDefault()
    void runSearch(query)
  }

  return (
    <div className="space-y-6 py-6">
      <div>
        <h1 className="text-2xl font-extrabold text-brand-navy">단어 검색</h1>
        <p className="text-sm text-brand-navy/50">Vocabulary Search</p>
        <p className="mt-2 text-xs text-brand-navy/40">
          한국어로 입력하면 한국어 단어를, English로 입력하면 영어 뜻을 검색해요.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <SearchIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-brand-navy/30" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="한국어 단어 또는 English meaning..."
            className="w-full rounded-2xl border border-brand-border bg-white/95 py-3.5 pl-12 pr-4 text-base focus:border-brand-purple focus:outline-none"
            autoFocus
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="shrink-0 rounded-2xl bg-brand-purple px-6 text-sm font-semibold text-white transition hover:bg-brand-purple-dark disabled:opacity-60"
        >
          검색
        </button>
      </form>

      {error && <p className="text-sm text-rose-600">{error}</p>}
      {loading && <p className="text-sm text-brand-navy/50">Searching...</p>}

      {results !== null && !loading && (
        <div>
          {results.length === 0 ? (
            <p className="text-sm text-brand-navy/60">No matching words found in our vocabulary database.</p>
          ) : (
            <div className="space-y-3">
              {results.map((word) => (
                <div key={word.id} className="rounded-2xl border border-brand-border bg-white/95 p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-2xl font-extrabold text-brand-navy">{word.korean}</p>
                        {word.is_teacher_added && (
                          <span className="rounded-full bg-brand-yellow/40 px-2 py-0.5 text-[11px] font-semibold text-brand-navy/70">
                            Added by Teacher
                          </span>
                        )}
                      </div>
                      {word.romanization && <p className="text-sm text-brand-navy/40">{word.romanization}</p>}
                      <p className="mt-1 text-lg font-semibold text-brand-purple">{word.english}</p>
                      {word.notes && <p className="mt-1 text-sm text-brand-navy/60">{word.notes}</p>}
                      <p className="mt-2 text-xs font-medium text-brand-navy/40">
                        Unit {word.unit_number} {word.unit_title_ko ? `· ${word.unit_title_ko}` : ''}
                      </p>
                    </div>
                    <div className="flex shrink-0 flex-col gap-2">
                      <Link
                        to={`/student/vocab/units/${word.unit_number}/words`}
                        className="rounded-xl bg-brand-purple px-4 py-2 text-center text-sm font-semibold text-white transition hover:bg-brand-purple-dark"
                      >
                        Practice
                      </Link>
                      <a
                        href={dictionaryUrl(word.korean)}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-xl border border-brand-border px-4 py-2 text-center text-sm font-medium text-brand-navy/60 transition hover:border-brand-purple hover:text-brand-purple"
                      >
                        Open Online Dictionary
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
