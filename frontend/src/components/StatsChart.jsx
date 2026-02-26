import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function StatsChart({ stats }) {
  const data = [
    { name: 'Positif', value: stats.sentiment_distribution.positive },
    { name: 'Neutre', value: stats.sentiment_distribution.neutral },
    { name: 'Négatif', value: stats.sentiment_distribution.negative },
  ]

  return (
    <div className="card h-72">
      <h3 className="mb-3 font-semibold">Répartition des sentiments</h3>
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="name" stroke="#cbd5e1" />
          <YAxis allowDecimals={false} stroke="#cbd5e1" />
          <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
          <Bar dataKey="value" fill="#38bdf8" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
