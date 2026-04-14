import { useState } from 'react'
import type { Message } from '../App'
import './ChatPanel.css'

interface Props {
  messages: Message[]
  onSend: (q: string) => void
  loading: boolean
  error: string | null
}

const EXAMPLE_QUESTIONS = [
  'What were our top 10 products last month?',
  'Show me the monthly sales trend',
  'How many new customers this week?',
]

export default function ChatPanel({ messages, onSend, loading, error }: Props) {
  const [input, setInput] = useState('')

  const submit = () => {
    const q = input.trim()
    if (!q || loading) return
    onSend(q)
    setInput('')
  }

  return (
    <div className="chat-panel">
      <div className="messages">
        {messages.length === 0 && (
          <div className="welcome">
            <p>👋 Ask your database anything in natural language</p>
            <div className="examples">
              {EXAMPLE_QUESTIONS.map(q => (
                <button key={q} className="example-btn" onClick={() => onSend(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map(m => (
          <div key={m.id} className={`message ${m.role}`}>
            <div className="bubble">
              <p>{m.content}</p>
              {m.sql && (
                <details className="sql-block">
                  <summary>Generated SQL</summary>
                  <pre>{m.sql}</pre>
                </details>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="bubble">
              <span className="typing">Thinking... ⏳</span>
            </div>
          </div>
        )}
        {error && <div className="error-msg">❌ {error}</div>}
      </div>
      <div className="input-row">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button onClick={submit} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}
