import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "OptiFlow — Workflow Orchestrator",
  description: "Intelligent Workflow Orchestration & Self-Optimizing System",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">{children}</body>
    </html>
  )
}
