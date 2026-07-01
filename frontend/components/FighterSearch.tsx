"use client"

import { useState, useEffect, useRef } from "react"
import { searchFighters } from "@/lib/api"
import type { FighterSearchResult } from "@/lib/types"
import { Input } from "@/components/ui/input"

interface FighterSearchProps {
  label: string
  placeholder?: string
  onChange: (fighter: FighterSearchResult | null) => void
}

export default function FighterSearch({ label, placeholder, onChange }: FighterSearchProps) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<FighterSearchResult[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined)
  const wrapperRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  useEffect(() => {
    if (selected || query.length < 2) {
      setResults([])
      return
    }
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const data = await searchFighters(query)
        setResults(data)
        setIsOpen(true)
      } catch {
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)
    return () => clearTimeout(debounceRef.current)
  }, [query, selected])

  function handleSelect(fighter: FighterSearchResult) {
    setQuery(fighter.name)
    setSelected(true)
    setIsOpen(false)
    onChange(fighter)
  }

  function handleInput(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value)
    setSelected(false)
    onChange(null)
  }

  return (
    <div ref={wrapperRef} className="relative">
      <label className="block text-sm font-medium text-muted-foreground mb-1.5">
        {label}
      </label>
      <Input
        type="text"
        value={query}
        onChange={handleInput}
        onFocus={() => {
          if (results.length > 0) setIsOpen(true)
        }}
        placeholder={placeholder || "Search fighter..."}
        className="h-10"
      />
      {loading && (
        <div className="absolute right-3 top-10">
          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      {isOpen && results.length > 0 && (
        <ul className="absolute z-50 mt-1 w-full bg-popover border border-border rounded-xl shadow-xl max-h-60 overflow-auto">
          {results.map((f) => (
            <li
              key={f.id}
              onClick={() => handleSelect(f)}
              className="px-4 py-2.5 text-foreground hover:bg-muted cursor-pointer transition"
            >
              {f.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
