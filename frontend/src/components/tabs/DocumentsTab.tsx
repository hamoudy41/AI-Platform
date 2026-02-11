import { useState } from 'react'
import { createDocument, getDocument } from '../../api'
import type { DocumentRead } from '../../api'
import { DocumentResult } from '../ResultPreview'

export function DocumentsTab() {
  const [docId, setDocId] = useState('')
  const [docTitle, setDocTitle] = useState('')
  const [docText, setDocText] = useState('')
  const [doc, setDoc] = useState<DocumentRead | null>(null)
  const [error, setError] = useState('')

  const handleCreate = async () => {
    setError('')
    setDoc(null)
    try {
      const created = await createDocument({ id: docId, title: docTitle, text: docText })
      setDoc(created)
    } catch (e) {
      setError(String(e))
    }
  }

  const handleGet = async () => {
    setError('')
    setDoc(null)
    try {
      const d = await getDocument(docId)
      setDoc(d)
    } catch (e) {
      setError(String(e))
    }
  }

  return (
    <section>
      <h2 className="mb-4 text-xl font-medium text-slate-800 dark:text-slate-200">Documents</h2>
      <div className="flex flex-col gap-3">
        <input
          placeholder="Document ID"
          value={docId}
          onChange={(e) => setDocId(e.target.value)}
          className="rounded border border-slate-300 px-3 py-2 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
        <input
          placeholder="Title"
          value={docTitle}
          onChange={(e) => setDocTitle(e.target.value)}
          className="rounded border border-slate-300 px-3 py-2 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
        <textarea
          placeholder="Text"
          value={docText}
          onChange={(e) => setDocText(e.target.value)}
          rows={4}
          className="rounded border border-slate-300 px-3 py-2 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleCreate}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Create
          </button>
          <button
            type="button"
            onClick={handleGet}
            className="rounded-md bg-slate-600 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
          >
            Get by ID
          </button>
        </div>
      </div>
      {error && <p className="mt-2 text-sm text-red-600 dark:text-red-400">{error}</p>}
      {doc && <DocumentResult data={doc} />}
    </section>
  )
}
