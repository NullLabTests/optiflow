import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDuration(ms: number | null | undefined): string {
  if (ms == null) return "—"
  if (ms < 1000) return `${ms.toFixed(0)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

export function formatBytes(bytes: number | null | undefined): string {
  if (bytes == null) return "—"
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / 1048576).toFixed(1)}MB`
}

export function statusColor(status: string): string {
  switch (status) {
    case "completed": return "text-green-600 bg-green-50 border-green-200"
    case "failed": return "text-red-600 bg-red-50 border-red-200"
    case "running": return "text-blue-600 bg-blue-50 border-blue-200"
    case "pending": return "text-yellow-600 bg-yellow-50 border-yellow-200"
    case "cancelled": return "text-gray-600 bg-gray-50 border-gray-200"
    default: return "text-gray-600 bg-gray-50 border-gray-200"
  }
}
