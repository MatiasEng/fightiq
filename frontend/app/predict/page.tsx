"use client"

import PredictionForm from "@/components/PredictionForm"

export default function PredictPage() {
  return (
    <div className="flex-1 w-full max-w-6xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-white">Predict a Fight</h1>
        <p className="text-zinc-400 mt-2">
          Select two fighters to see who the model predicts will win
        </p>
      </div>
      <PredictionForm />
    </div>
  )
}
