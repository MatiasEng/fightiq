"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { getFighter, getFighterFights } from "@/lib/api"
import type { FighterDetail, FighterFight } from "@/lib/types"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"

export default function FighterPage() {
  const { id } = useParams<{ id: string }>()
  const [fighter, setFighter] = useState<FighterDetail | null>(null)
  const [fights, setFights] = useState<FighterFight[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    setError(null)
    Promise.all([getFighter(id), getFighterFights(id)])
      .then(([fighterData, fightsData]) => {
        setFighter(fighterData)
        setFights(fightsData)
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="flex-1 w-full max-w-6xl mx-auto px-4 py-12 space-y-4">
        <Skeleton className="h-9 w-32" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    )
  }

  if (error || !fighter) {
    return (
      <div className="flex-1 max-w-6xl mx-auto px-4 py-12 text-center">
        <p className="text-destructive">{error || "Fighter not found"}</p>
        <Link href="/predict" className="text-muted-foreground hover:text-foreground mt-4 inline-block transition">
          ← Back to predict
        </Link>
      </div>
    )
  }

  return (
    <div className="flex-1 w-full max-w-6xl mx-auto px-4 py-12">

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
        <Card>
          <CardHeader className="text-center pb-0">
            <h1 className="text-4xl font-bold text-foreground">{fighter.name}</h1>
            <div className="flex items-center justify-center gap-2 mt-2">
              <Badge variant="secondary" className="text-base px-3 py-1">
                {fighter.wins}-{fighter.losses}-{fighter.draws}
              </Badge>
              <Badge variant="outline" className="text-xs">
                {fighter.stance || "Unknown"}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-6 space-y-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
              <div className="space-y-8">
                <StatSection title="Physical">
                  <StatRow
                    label="Height"
                    value={fighter.height_cm ? `${fighter.height_cm} cm` : "N/A"}
                  />
                  <StatRow
                    label="Reach"
                    value={fighter.reach_cm ? `${fighter.reach_cm} cm` : "N/A"}
                  />
                  <StatRow
                    label="Age"
                    value={fighter.age != null ? `${fighter.age}` : "N/A"}
                  />
                </StatSection>

                <StatSection title="Striking">
                  <StatRow
                    label="Sig. Str. Acc."
                    value={
                      fighter.sig_str_acc != null
                        ? `${(fighter.sig_str_acc * 100).toFixed(1)}%`
                        : "N/A"
                    }
                  />
                  <StatRow
                    label="Sig. Str. Def."
                    value={
                      fighter.sig_str_def != null
                        ? `${(fighter.sig_str_def * 100).toFixed(1)}%`
                        : "N/A"
                    }
                  />
                </StatSection>
              </div>

              <div className="space-y-8">
                <StatSection title="Wrestling">
                  <StatRow
                    label="TD Acc."
                    value={
                      fighter.td_acc != null
                        ? `${(fighter.td_acc * 100).toFixed(1)}%`
                        : "N/A"
                    }
                  />
                  <StatRow
                    label="TD Def."
                    value={
                      fighter.td_def != null
                        ? `${(fighter.td_def * 100).toFixed(1)}%`
                        : "N/A"
                    }
                  />
                </StatSection>

                <StatSection title="Career">
                  <StatRow
                    label="Finish Rate"
                    value={
                      fighter.finish_rate != null
                        ? `${(fighter.finish_rate * 100).toFixed(0)}%`
                        : "N/A"
                    }
                  />
                  <StatRow label="KO Wins" value={String(fighter.kos)} />
                  <StatRow label="Sub. Wins" value={String(fighter.submissions)} />
                  <StatRow label="UFC Fights" value={String(fighter.total_fights)} />
                  <StatRow
                    label="UFC Streak"
                    value={formatStreak(fighter.streak)}
                  />

                </StatSection>
              </div>

              <div className="sm:col-span-2">
                <div className="bg-muted/30 rounded-xl p-4 border border-border">
                  <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-2">
                    Abbreviations
                  </p>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-muted-foreground">
                    <span>
                      <span className="text-foreground">Sig. Str. Acc.</span>{" "}
                      Significant Strike Accuracy
                    </span>
                    <span>
                      <span className="text-foreground">Sig. Str. Def.</span>{" "}
                      Significant Strike Defense
                    </span>
                    <span>
                      <span className="text-foreground">TD Acc.</span> Takedown
                      Accuracy
                    </span>
                    <span>
                      <span className="text-foreground">TD Def.</span> Takedown
                      Defense
                    </span>
                    <span>
                      <span className="text-foreground">Sub. Wins</span> Wins by
                      Submission
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {fights.length > 0 && (
          <Card>
            <CardContent className="pt-6">
              <StatSection title={`Fight History (${fights.length})`}>
                {fights.map((fight) => (
                  <FightRow key={fight.id} fight={fight} />
                ))}
              </StatSection>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

function StatSection({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
        {title}
      </h3>
      <div className="space-y-0">{children}</div>
    </div>
  )
}

function StatRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <span className="text-muted-foreground text-sm">{label}</span>
      <span className="text-foreground text-sm font-medium">{value}</span>
    </div>
  )
}

function FightRow({ fight }: { fight: FighterFight }) {
  const isWin = fight.result === "Win"
  return (
    <div className="flex items-center justify-between py-3 border-b border-border last:border-0 gap-4">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <span
          className={`shrink-0 w-14 text-center text-xs font-bold px-2 py-1 rounded-full ${
            isWin
              ? "bg-green-500/20 text-green-500"
              : "bg-destructive/20 text-destructive"
          }`}
        >
          {fight.result}
        </span>
        <Link
          href={`/fighters/${fight.opponent_id}`}
          className="text-foreground text-sm font-medium hover:text-primary truncate"
        >
          {fight.opponent_name}
        </Link>
      </div>
      <div className="text-right text-xs text-muted-foreground shrink-0 hidden sm:block">
        {fight.method}{fight.round ? ` R${fight.round}` : ""}
      </div>
      <div className="text-right text-xs text-muted-foreground shrink-0 hidden md:block">
        {fight.date ? fight.date : ""}
      </div>
    </div>
  )
}

function formatStreak(streak: number): string {
  if (streak > 0) return `${streak}W`
  if (streak < 0) return `${Math.abs(streak)}L`
  return "0"
}
