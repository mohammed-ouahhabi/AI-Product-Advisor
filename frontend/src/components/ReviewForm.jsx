import { useState } from 'react'

export function ReviewForm({ onCreate }) {
  const [text, setText] = useState('')
  const [rating, setRating] = useState(3)

  const submit = async (e) => {
    e.preventDefault()
    if (!text) return
    await onCreate({ text, rating: Number(rating) })
    setText('')
    setRating(3)
  }

  return (
    <form onSubmit={submit} className="card grid gap-3">
      <h3 className="font-semibold">Ajouter un avis client</h3>
      <textarea
        className="input min-h-24"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ex: Produit confortable mais batterie trop faible"
      />
      <select className="input" value={rating} onChange={(e) => setRating(e.target.value)}>
        {[1, 2, 3, 4, 5].map((v) => (
          <option key={v} value={v}>
            Note {v}
          </option>
        ))}
      </select>
      <button className="btn bg-emerald-600 hover:bg-emerald-500 text-white">Analyser et enregistrer</button>
    </form>
  )
}
