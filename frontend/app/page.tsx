import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center flex-1 px-4">
      <div className="max-w-2xl mx-auto text-center space-y-8">
        <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-foreground">
          Fight<span className="text-primary">IQ</span>
        </h1>
        <p className="text-lg text-muted-foreground">
          Predict UFC fight outcomes with machine learning. Enter two fighters
          and get a data-driven prediction.
        </p>
        <Link href="/predict">
          <Button size="lg" className="text-base px-8 py-6">
            Start Predicting
          </Button>
        </Link>
        <div className="pt-12 grid grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-2xl font-bold text-foreground">
              ML-Powered
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              Trained on historical UFC data
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-foreground">
              Live Stats
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              Real fighter statistics
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-foreground">
              Accurate
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              65%+ prediction accuracy
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
