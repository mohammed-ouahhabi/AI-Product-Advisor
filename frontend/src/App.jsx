import { useEffect, useState } from 'react'

import { api } from './api'
import { ProductForm } from './components/ProductForm'
import { ReviewForm } from './components/ReviewForm'
import { StatsChart } from './components/StatsChart'

const emptyStats = { total_reviews: 0, average_rating: 0, sentiment_distribution: { positive: 0, neutral: 0, negative: 0 } }

function App() {
  const [token, setToken] = useState(localStorage.getItem('auth_token'))
  const [user, setUser] = useState(null)
  const [mode, setMode] = useState('login')
  const [auth, setAuth] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const [products, setProducts] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [reviews, setReviews] = useState([])
  const [stats, setStats] = useState(emptyStats)
  const [recommendations, setRecommendations] = useState({ negative_summary: '', weak_points: [], recommendations: [] })

  const loadProducts = async () => {
    const { data } = await api.get('/products')
    setProducts(data)
    if (!selectedId && data.length) setSelectedId(data[0].id)
  }

  const loadProductData = async (productId) => {
    if (!productId) return
    const [reviewsRes, statsRes, recoRes] = await Promise.all([
      api.get(`/products/${productId}/reviews`),
      api.get(`/products/${productId}/stats`),
      api.get(`/products/${productId}/recommendations`),
    ])
    setReviews(reviewsRes.data)
    setStats(statsRes.data)
    setRecommendations(recoRes.data)
  }

  const getMe = async () => {
    if (!localStorage.getItem('auth_token')) return
    const { data } = await api.get('/auth/me')
    setUser(data)
  }

  useEffect(() => {
    if (token) {
      getMe().then(loadProducts).catch(() => {
        localStorage.removeItem('auth_token')
        setToken(null)
      })
    }
  }, [token])

  useEffect(() => {
    if (token) loadProductData(selectedId)
  }, [selectedId, token])

  const submitAuth = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register'
      const { data } = await api.post(endpoint, auth)
      localStorage.setItem('auth_token', data.token)
      setToken(data.token)
      setUser(data.user)
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur d’authentification')
    }
  }

  if (!token) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-4 text-slate-100">
        <section className="mx-auto mt-20 max-w-md card">
          <h1 className="text-2xl font-bold">AI Product Advisor</h1>
          <p className="mt-2 text-sm text-slate-300">Connectez-vous pour gérer les produits, les avis et les analyses IA.</p>
          <form className="mt-6 grid gap-3" onSubmit={submitAuth}>
            <input className="input" type="email" required placeholder="Email" value={auth.email} onChange={(e) => setAuth({ ...auth, email: e.target.value })} />
            <input className="input" type="password" required placeholder="Mot de passe" value={auth.password} onChange={(e) => setAuth({ ...auth, password: e.target.value })} />
            {error && <p className="text-sm text-rose-400">{error}</p>}
            <button className="btn bg-blue-600 hover:bg-blue-500 text-white">{mode === 'login' ? 'Se connecter' : 'Créer un compte'}</button>
          </form>
          <button className="mt-3 text-sm text-sky-400 hover:text-sky-300" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
            {mode === 'login' ? 'Pas de compte ? Inscription' : 'Déjà inscrit ? Connexion'}
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-4 text-slate-100">
      <header className="mx-auto mb-4 flex max-w-7xl items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3">
        <div>
          <h1 className="text-xl font-bold">AI Product Advisor</h1>
          <p className="text-xs text-slate-400">Bienvenue {user?.email}</p>
        </div>
        <button className="btn bg-slate-800 hover:bg-slate-700" onClick={() => { localStorage.removeItem('auth_token'); setToken(null); setUser(null) }}>
          Déconnexion
        </button>
      </header>

      <section className="mx-auto grid max-w-7xl gap-4 md:grid-cols-3">
        <aside className="space-y-4 md:col-span-1">
          <ProductForm onCreate={async (payload) => { await api.post('/products', payload); await loadProducts() }} />
          <div className="card">
            <h2 className="mb-3 text-lg font-semibold">Produits</h2>
            <ul className="space-y-2">
              {products.map((p) => (
                <li key={p.id}>
                  <button
                    className={`w-full rounded-xl border px-3 py-2 text-left transition ${selectedId === p.id ? 'border-sky-500 bg-sky-500/10' : 'border-slate-700 bg-slate-950 hover:bg-slate-800'}`}
                    onClick={() => setSelectedId(p.id)}
                  >
                    <p className="font-medium">{p.name}</p>
                    <p className="text-xs text-slate-400">{p.category}</p>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        <section className="space-y-4 md:col-span-2">
          {selectedId ? (
            <>
              <ReviewForm onCreate={async (payload) => { await api.post(`/products/${selectedId}/reviews`, payload); await loadProductData(selectedId) }} />
              <div className="grid gap-4 md:grid-cols-3">
                <div className="card"><p className="text-slate-400">Total avis</p><p className="text-2xl font-bold">{stats.total_reviews}</p></div>
                <div className="card"><p className="text-slate-400">Moyenne</p><p className="text-2xl font-bold">{stats.average_rating}/5</p></div>
                <div className="card"><p className="text-slate-400">Négatifs</p><p className="text-2xl font-bold">{stats.sentiment_distribution.negative}</p></div>
              </div>
              <StatsChart stats={stats} />
              <div className="grid gap-4 md:grid-cols-2">
                <div className="card">
                  <h3 className="font-semibold">Derniers avis</h3>
                  <ul className="mt-3 space-y-2 text-sm">
                    {reviews.map((r) => (
                      <li key={r.id} className="rounded-xl border border-slate-700 bg-slate-950 p-3">
                        <p>{r.text}</p>
                        <p className="mt-1 text-xs text-slate-400">Note {r.rating} • {r.sentiment} ({r.sentiment_score})</p>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="card">
                  <h3 className="font-semibold">Recommandations IA</h3>
                  <p className="mt-2 text-sm text-slate-300">{recommendations.negative_summary}</p>
                  <ul className="mt-3 list-disc space-y-1 pl-5 text-sm">
                    {recommendations.recommendations.map((item, idx) => <li key={idx}>{item}</li>)}
                  </ul>
                </div>
              </div>
            </>
          ) : (
            <div className="card">Créez un produit pour commencer.</div>
          )}
        </section>
      </section>
    </main>
  )
}

export default App
