"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Workflow, BarChart3, Lightbulb, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/workflows", label: "Workflows", icon: Workflow },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/optimizations", label: "Optimizations", icon: Lightbulb },
]

export default function DashboardLayout({ children, onLogout }: { children: React.ReactNode; onLogout: () => void }) {
  const pathname = usePathname()

  return (
    <div className="flex h-screen">
      <aside className="w-56 border-r bg-white p-4 flex flex-col">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-indigo-600">OptiFlow</h1>
          <p className="text-xs text-gray-400">Workflow Orchestrator</p>
        </div>
        <nav className="flex-1 space-y-1">
          {navItems.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition",
                pathname === item.href
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
        <button
          onClick={onLogout}
          className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-gray-500 hover:bg-gray-50 transition"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  )
}
