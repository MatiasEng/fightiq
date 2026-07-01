import Link from "next/link"
import type { PredictResponse } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ResultCardProps {
  result: PredictResponse
}

export default function ResultCard({ result }: ResultCardProps) {
  const {
    fighter_a,
    fighter_b,
    fighter_a_win_prob,
    fighter_b_win_prob,
    predicted_winner,
  } = result

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center">Prediction Result</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <ProbabilityRow
            name={fighter_a.name}
            prob={fighter_a_win_prob}
            color="bg-primary"
          />
          <ProbabilityRow
            name={fighter_b.name}
            prob={fighter_b_win_prob}
            color="bg-blue-600"
          />
        </div>

        <div className="text-center p-4 bg-muted rounded-xl">
          <p className="text-muted-foreground text-sm">Predicted Winner</p>
          <p className="text-2xl font-bold text-foreground mt-1">
            {predicted_winner}
          </p>
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">
            Stats Comparison
          </h3>
          <NameRow
            nameA={fighter_a.name}
            nameB={fighter_b.name}
            idA={fighter_a.id}
            idB={fighter_b.id}
          />
          <StatsRow
            label="Record"
            a={`${fighter_a.wins}-${fighter_a.losses}`}
            b={`${fighter_b.wins}-${fighter_b.losses}`}
          />
          <StatsRow
            label="Reach"
            a={fighter_a.reach_cm ? `${fighter_a.reach_cm} cm` : "N/A"}
            b={fighter_b.reach_cm ? `${fighter_b.reach_cm} cm` : "N/A"}
          />
          <StatsRow
            label="Stance"
            a={fighter_a.stance || "N/A"}
            b={fighter_b.stance || "N/A"}
          />
          <StatsRow
            label="Finish Rate"
            a={
              fighter_a.finish_rate != null
                ? `${(fighter_a.finish_rate * 100).toFixed(0)}%`
                : "N/A"
            }
            b={
              fighter_b.finish_rate != null
                ? `${(fighter_b.finish_rate * 100).toFixed(0)}%`
                : "N/A"
            }
          />
          <StatsRow
            label="UFC Streak"
            a={formatStreak(fighter_a.streak)}
            b={formatStreak(fighter_b.streak)}
          />
        </div>

        <div className="flex justify-center">
          <Badge variant="secondary" className="text-xs">
            Trained on historical UFC data
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}

function ProbabilityRow({
  name,
  prob,
  color,
}: {
  name: string
  prob: number
  color: string
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-foreground font-medium">{name}</span>
        <span className="text-foreground font-mono">
          {(prob * 100).toFixed(1)}%
        </span>
      </div>
      <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-700 ease-out`}
          style={{ width: `${prob * 100}%` }}
        />
      </div>
    </div>
  )
}

function NameRow({
  nameA,
  nameB,
  idA,
  idB,
}: {
  nameA: string
  nameB: string
  idA: string
  idB: string
}) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-border">
      <span className="text-muted-foreground text-sm w-24" />
      <Link
        href={`/fighters/${idA}`}
        className="text-foreground text-base font-bold uppercase tracking-wider text-right w-1/3 hover:text-primary transition-colors"
      >
        {nameA} details
      </Link>
      <span className="text-muted-foreground text-sm font-black w-8 text-center">
        VS
      </span>
      <Link
        href={`/fighters/${idB}`}
        className="text-foreground text-base font-bold uppercase tracking-wider w-1/3 hover:text-primary transition-colors"
      >
        {nameB} details
      </Link>
    </div>
  )
}

function StatsRow({
  label,
  a,
  b,
}: {
  label: string
  a: string
  b: string
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
      <span className="text-muted-foreground text-sm w-24">{label}</span>
      <span className="text-foreground text-sm text-right w-1/3">{a}</span>
      <span className="text-muted-foreground text-xs w-8 text-center">vs</span>
      <span className="text-foreground text-sm w-1/3">{b}</span>
    </div>
  )
}

function formatStreak(streak: number): string {
  if (streak > 0) return `${streak}W`
  if (streak < 0) return `${Math.abs(streak)}L`
  return "0"
}
