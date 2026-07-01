"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

const links = [
  { href: "/predict", label: "Predict" },
  { href: "/fighters", label: "Fighters" },
]

export default function Header() {
  const pathname = usePathname()

  return (
    <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link
          href="/"
          className="text-xl font-bold text-foreground tracking-tight"
        >
          Fight<span className="text-primary">IQ</span>
        </Link>
        <nav className="flex gap-2">
          {links.map((link) => {
            const active = pathname.startsWith(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-5 py-2.5 rounded-full text-sm font-semibold border transition ${
                  active
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-card text-foreground border-border hover:bg-muted hover:border-foreground/20"
                }`}
              >
                {link.label}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
