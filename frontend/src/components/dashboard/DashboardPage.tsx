"use client"

import { useEffect, useState } from "react"

import { Card } from "@/components/ui/card"
import { authClient, type Session } from "@/server/better-auth/client"

import { AdminDashboard } from "./AdminDashboard"
import { UserDashboard } from "./UserDashboard"

export default function DashboardPage() {
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSession = async () => {
      try {
        setLoading(true)
        const response = await authClient.getSession()
        setSession(response.data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        setLoading(false)
      }
    }

    void fetchSession()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-48 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error || !session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="p-8 bg-red-50 border border-red-200">
          <h1 className="text-lg font-semibold text-red-700 mb-2">Error Loading Dashboard</h1>
          <p className="text-red-600">{error ?? "Not authenticated"}</p>
        </Card>
      </div>
    )
  }

  const isAdmin = "role" in session.user && (session.user.role as string) === "admin"

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {isAdmin ? "Admin Dashboard" : "Dashboard"}
          </h1>
          <p className="text-gray-600 mt-2">
            Welcome back, {session.user.name}
          </p>
        </div>

        {isAdmin ? <AdminDashboard /> : <UserDashboard />}
      </div>
    </div>
  )
}
