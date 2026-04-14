import ReactECharts from 'echarts-for-react'
import './ChartPanel.css'

interface Props {
  data: {
    data: {
      columns: string[]
      rows: Record<string, any>[]
      row_count: number
    }
    chart_type: string
    question: string
  }
}

function buildOption(data: Props['data']) {
  const { columns, rows } = data.data
  if (!rows.length || !columns.length) return {}

  const xKey = columns[0]
  const yKey = columns[1]
  const xData = rows.map(r => r[xKey])
  const yData = rows.map(r => Number(r[yKey]) || 0)

  const chartType = data.chart_type || 'bar'

  if (chartType === 'line') {
    return {
      title: { text: data.question, textStyle: { color: '#e2e8f0', fontSize: 13 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: xData, axisLabel: { color: '#94a3b8' } },
      yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
      series: [{ data: yData, type: 'line', smooth: true, areaStyle: {} }],
      backgroundColor: 'transparent',
    }
  }

  if (chartType === 'bar') {
    return {
      title: { text: data.question, textStyle: { color: '#e2e8f0', fontSize: 13 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: xData, axisLabel: { color: '#94a3b8', rotate: 30 } },
      yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
      series: [{ data: yData, type: 'bar' }],
      backgroundColor: 'transparent',
    }
  }

  // table fallback
  return {}
}

export default function ChartPanel({ data }: Props) {
  const { columns, rows, row_count } = data.data
  const option = buildOption(data)

  return (
    <div className="chart-panel">
      <h3>📊 {data.chart_type === 'line' ? 'Trend' : data.chart_type === 'bar' ? 'Ranking' : 'Table'}</h3>
      {option.title ? (
        <ReactECharts option={option} style={{ height: 300 }} />
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>{columns.map(c => <th key={c}>{c}</th>)}</tr>
            </thead>
            <tbody>
              {rows.slice(0, 20).map((row, i) => (
                <tr key={i}>
                  {columns.map(c => <td key={c}>{String(row[c])}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
          {row_count > 20 && <p className="table-note">Showing 20 of {row_count} rows</p>}
        </div>
      )}
    </div>
  )
}
