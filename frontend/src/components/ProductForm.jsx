import { useState } from 'react'

export function ProductForm({ onCreate }) {
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    if (!name || !category) return
    await onCreate({ name, category })
    setName('')
    setCategory('')
  }

  return (
    <form onSubmit={submit} className="card grid gap-3">
      <h2 className="text-lg font-semibold">Nouveau produit</h2>
      <input className="input" placeholder="Nom du produit" value={name} onChange={(e) => setName(e.target.value)} />
      <input className="input" placeholder="Catégorie" value={category} onChange={(e) => setCategory(e.target.value)} />
      <button className="btn bg-blue-600 hover:bg-blue-500 text-white">Ajouter</button>
    </form>
  )
}
