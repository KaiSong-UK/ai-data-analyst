import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import ChartPanel from './components/ChartPanel'
import Sidebar from './components/Sidebar'
import './App.css'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sql?: string
  chartType?: string
  data?: any
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedChart, setSelectedChart] = useState<any>(null)
  const [schema, setSchema] = useState('public')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = async (question: string) => {
    setLoading(true)
    setError(null)
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
    }
    setMessages(prev => [...prev, userMsg])

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, schema }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Request failed')
      }
      const data = await res.json()
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.explanation || `Query returned ${data.data.row_count} rows`,
        sql: data.generated_sql,
        chartType: data.chart_type,
        data: data.data,
      }
      setMessages(prev => [...prev, assistantMsg])
      setSelectedChart(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <Sidebar schema={schema} onSchemaChange={setSchema} />
      <main className="main">
        <div className="chat-section">
          <ChatPanel
            messages={messages}
            onSend={sendMessage}
            loading={loading}
            error={error}
          />
        </div>
        {selectedChart && (
          <div className="chart-section">
            <ChartPanel data={selectedChart} />
          </div>
        )}
      </main>
    </div>
  )
}
