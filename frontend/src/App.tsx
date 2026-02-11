import { useState } from 'react'
import {
  AskTab,
  ClassifyTab,
  DocumentsTab,
  HealthTab,
  Layout,
  NotaryTab,
} from './components'

export default function App() {
  const [tab, setTab] = useState<'health' | 'documents' | 'classify' | 'notary' | 'ask'>('health')

  return (
    <Layout tab={tab} onTabChange={setTab}>
      {tab === 'health' && <HealthTab />}
      {tab === 'documents' && <DocumentsTab />}
      {tab === 'classify' && <ClassifyTab />}
      {tab === 'notary' && <NotaryTab />}
      {tab === 'ask' && <AskTab />}
    </Layout>
  )
}
