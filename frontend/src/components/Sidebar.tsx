import { useState } from 'react'
import './Sidebar.css'

interface SidebarProps {
  schema: string
  onSchemaChange: (s: string) => void
}

export default function Sidebar({ schema, onSchemaChange }: SidebarProps) {
  const schemas = ['public', 'sales', 'analytics']

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-icon">🤖</span>
        <span className="logo-text">AI Analyst</span>
      </div>
      <div className="sidebar-section">
        <p className="sidebar-label">Schema</p>
        {schemas.map(s => (
          <button
            key={s}
            className={`schema-btn ${schema === s ? 'active' : ''}`}
            onClick={() => onSchemaChange(s)}
          >
            📁 {s}
          </button>
        ))}
      </div>
    </aside>
  )
}
