import type { HealthStatus, DocumentRead, ClassifyResponse, AskResponse, NotarySummarizeResponse } from '../api'

function SourceBadge({ source }: { source: string }) {
  const isLLM = source === 'llm'
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        isLLM
          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-400'
          : 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-400'
      }`}
    >
      {isLLM ? 'AI model' : 'Fallback'}
    </span>
  )
}

export function HealthResult({ data }: { data: HealthStatus }) {
  const dbOk = data.db_ok == null ? '—' : data.db_ok ? 'Connected' : 'Disconnected'
  const dbStatus = data.db_ok === true ? 'text-emerald-600 dark:text-emerald-400' : data.db_ok === false ? 'text-red-600 dark:text-red-400' : 'text-slate-500'
  const llmOk = data.llm_ok == null ? '—' : data.llm_ok ? 'Configured' : 'Not configured'
  const llmStatus = data.llm_ok === true ? 'text-emerald-600 dark:text-emerald-400' : data.llm_ok === false ? 'text-red-600 dark:text-red-400' : 'text-slate-500'
  const ts = data.timestamp ? new Date(data.timestamp).toLocaleString() : '—'

  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800/50">
      <div className="border-b border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800/80">
        <h3 className="font-medium text-slate-800 dark:text-slate-200">Health status</h3>
      </div>
      <dl className="divide-y divide-slate-200 dark:divide-slate-700">
        <div className="flex justify-between gap-4 px-4 py-3">
          <dt className="text-sm text-slate-500 dark:text-slate-400">Environment</dt>
          <dd className="text-sm font-medium text-slate-800 dark:text-slate-200">{data.environment || '—'}</dd>
        </div>
        <div className="flex justify-between gap-4 px-4 py-3">
          <dt className="text-sm text-slate-500 dark:text-slate-400">Database</dt>
          <dd className={`text-sm font-medium ${dbStatus}`}>{dbOk}</dd>
        </div>
        <div className="flex justify-between gap-4 px-4 py-3">
          <dt className="text-sm text-slate-500 dark:text-slate-400">LLM</dt>
          <dd className={`text-sm font-medium ${llmStatus}`}>{llmOk}</dd>
        </div>
        <div className="flex justify-between gap-4 px-4 py-3">
          <dt className="text-sm text-slate-500 dark:text-slate-400">Timestamp</dt>
          <dd className="text-sm text-slate-600 dark:text-slate-300">{ts}</dd>
        </div>
      </dl>
    </div>
  )
}

export function DocumentResult({ data }: { data: DocumentRead }) {
  const created = data.created_at ? new Date(data.created_at).toLocaleString() : '—'

  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800/50">
      <div className="border-b border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800/80">
        <h3 className="font-medium text-slate-800 dark:text-slate-200">{data.title || 'Untitled'}</h3>
        <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">ID: {data.id}</p>
      </div>
      <div className="px-4 py-3">
        <p className="mb-3 text-xs text-slate-500 dark:text-slate-400">Content</p>
        <p className="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">{data.text || '—'}</p>
      </div>
      <div className="border-t border-slate-200 px-4 py-2 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
        Created: {created}
      </div>
    </div>
  )
}

export function ClassifyResult({ data }: { data: ClassifyResponse }) {
  const confPercent = Math.round((data.confidence ?? 0) * 100)
  const isError = data.label === 'error' || data.source === 'fallback' && data.confidence === 0

  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800/50">
      <div className="border-b border-slate-200 px-4 py-4 dark:border-slate-700">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="text-sm text-slate-500 dark:text-slate-400">Classification</span>
          <SourceBadge source={data.source} />
        </div>
        <p className={`mt-2 text-2xl font-semibold ${isError ? 'text-red-600 dark:text-red-400' : 'text-slate-900 dark:text-slate-100'}`}>
          {data.label}
        </p>
        {!isError && (
          <div className="mt-2">
            <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>Confidence</span>
              <span>{confPercent}%</span>
            </div>
            <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all dark:bg-indigo-600"
                style={{ width: `${confPercent}%` }}
              />
            </div>
          </div>
        )}
      </div>
      <div className="flex items-center justify-between border-t border-slate-200 px-4 py-2 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
        <span>Model: {data.model}</span>
      </div>
    </div>
  )
}

export function AskResult({ data }: { data: AskResponse }) {
  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800/50">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-slate-50 px-4 py-2 dark:border-slate-700 dark:bg-slate-800/80">
        <span className="text-sm text-slate-500 dark:text-slate-400">Answer</span>
        <SourceBadge source={data.source} />
      </div>
      <div className="px-4 py-4">
        <p className="whitespace-pre-wrap text-slate-700 dark:text-slate-300">{data.answer}</p>
      </div>
      <div className="border-t border-slate-200 px-4 py-2 text-xs text-slate-500 dark:border-slate-700 dark:text-slate-400">
        Model: {data.model}
      </div>
    </div>
  )
}

export function NotaryResult({ data }: { data: NotarySummarizeResponse }) {
  const s = data.summary

  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800/50">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800/80">
        <h3 className="font-medium text-slate-800 dark:text-slate-200">{s.title}</h3>
        <SourceBadge source={data.source} />
      </div>
      <div className="divide-y divide-slate-200 dark:divide-slate-700">
        {s.key_points?.length > 0 && (
          <div className="px-4 py-3">
            <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Key points</h4>
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-700 dark:text-slate-300">
              {s.key_points.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        )}
        {s.parties_involved?.length > 0 && (
          <div className="px-4 py-3">
            <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Parties involved</h4>
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-700 dark:text-slate-300">
              {s.parties_involved.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        )}
        {s.risks_or_warnings?.length > 0 && (
          <div className="px-4 py-3">
            <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-amber-600 dark:text-amber-400">Risks & warnings</h4>
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-700 dark:text-slate-300">
              {s.risks_or_warnings.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}
        <div className="px-4 py-3">
          <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Summary</h4>
          <p className="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">{s.raw_summary || '—'}</p>
        </div>
      </div>
    </div>
  )
}

export function ResultPreview({ data }: { data: unknown }) {
  return (
    <pre className="mt-4 overflow-auto rounded-lg bg-slate-800 p-4 text-sm text-slate-100">
      {JSON.stringify(data, null, 2)}
    </pre>
  )
}
