"use client"

import { useState } from "react"
import FighterSearch from "./FighterSearch"
import ResultCard from "./ResultCard"
import { predictFight } from "@/lib/api"
import type { FighterSearchResult, PredictResponse } from "@/lib/types"
import { Button } from "@/components/ui/button"

export default function PredictionForm() {
  const [fighterA, setFighterA] = useState<FighterSearchResult | null>(null)
  const [fighterB, setFighterB] = useState<FighterSearchResult | null>(null)
  const [result, setResult] = useState<PredictResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [formKey, setFormKey] = useState(0)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!fighterA || !fighterB) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await predictFight(fighterA.name, fighterB.name)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed")
    } finally {
      setLoading(false)
    }
  }

  function handleClear() {
    setFormKey((k) => k + 1)
    setFighterA(null)
    setFighterB(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8" key={formKey}>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FighterSearch label="Fighter A" placeholder="e.g. Jon Jones" onChange={setFighterA} />
          <FighterSearch label="Fighter B" placeholder="e.g. Daniel Cormier" onChange={setFighterB} />
        </div>
        <div className="flex gap-3 justify-center">
          <Button type="submit" size="lg" className="h-12 px-8 text-base" disabled={!fighterA || !fighterB || loading}>
            {loading ? "Predicting..." : "Predict Winner"}
          </Button>
          {result && (
            <Button type="button" variant="ghost" onClick={handleClear}>
              Clear
            </Button>
          )}
        </div>
      </form>

      {error && (
        <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-xl text-destructive text-center">
          {error}
        </div>
      )}

      {result && <ResultCard result={result} />}
    </div>
  )
}
