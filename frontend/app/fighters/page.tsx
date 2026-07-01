"use client"

import { useRouter } from "next/navigation"
import FighterSearch from "@/components/FighterSearch"
import type { FighterSearchResult } from "@/lib/types"

export default function FightersPage() {
  const router = useRouter()

  function handleSelect(fighter: FighterSearchResult | null) {
    if (fighter) {
      router.push(`/fighters/${fighter.id}`)
    }
  }

  return (
    <div className="flex-1 w-full max-w-xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-foreground">Find a Fighter</h1>
        <p className="text-muted-foreground mt-2">
          Search for a fighter to view their stats
        </p>
      </div>
      <FighterSearch label="Fighter Name" onChange={handleSelect} />
    </div>
  )
}
