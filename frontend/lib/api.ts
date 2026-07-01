import type { FighterSearchResult, PredictResponse, FighterDetail, FighterFight } from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function searchFighters(query: string): Promise<FighterSearchResult[]> {
  if (query.length < 2) return []
  const res = await fetch(`${API_URL}/fighters?q=${encodeURIComponent(query)}`)
  if (!res.ok) {
    if (res.status === 404) return []
    throw new Error("Failed to search fighters")
  }
  return res.json()
}

export async function predictFight(
  fighterA: string,
  fighterB: string
): Promise<PredictResponse> {
  const res = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fighter_a: fighterA, fighter_b: fighterB }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Prediction failed" }))
    throw new Error(err.detail)
  }
  return res.json()
}

export async function getFighterFights(id: string): Promise<FighterFight[]> {
  const res = await fetch(`${API_URL}/fighters/${encodeURIComponent(id)}/fights`)
  if (!res.ok) {
    throw new Error("Failed to load fight history")
  }
  return res.json()
}

export async function getFighter(id: string): Promise<FighterDetail> {
  const res = await fetch(`${API_URL}/fighters/${encodeURIComponent(id)}`)
  if (!res.ok) {
    throw new Error("Fighter not found")
  }
  return res.json()
}
