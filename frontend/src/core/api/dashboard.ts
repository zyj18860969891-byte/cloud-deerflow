/**
 * 仪表板相关的 API 钩子和工具函数
 */

import { useCallback, useEffect, useState } from "react"

// 仪表板数据接口
export interface AdminDashboardData {
  total_users: number
  active_users: number
  api_calls_today: number
  error_rate: number
  system_health: number
  cache_hit_rate: number
  total_cost: number
  avg_response_time: number
  system_metrics: {
    name: string
    value: number
    status: "healthy" | "warning" | "critical"
  }[]
  recent_errors: {
    type: string
    count: number
    last_seen: string
  }[]
  top_users: {
    id: string
    name: string
    api_calls: number
    cost: number
  }[]
}

export interface UserDashboardData {
  tool_executions: number
  cache_hit_rate: number
  storage_used: number
  storage_quota: number
  api_quota: number
  api_used: number
  avg_response_time: number
  success_rate: number
  api_usage: {
    period: string
    used: number
    quota: number
  }[]
  top_tools: {
    name: string
    executions: number
    success_rate: number
  }[]
  recent_activity: {
    id: string
    action: string
    tool: string
    time: string
    status: "success" | "warning" | "error"
  }[]
}

// API 基础 URL
const DASHBOARD_API_BASE = "/api/dashboard"

/**
 * 获取管理员仪表板数据
 */
export async function fetchAdminDashboard(): Promise<AdminDashboardData> {
  const response = await fetch(`${DASHBOARD_API_BASE}/admin`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch admin dashboard: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 获取用户仪表板数据
 */
export async function fetchUserDashboard(): Promise<UserDashboardData> {
  const response = await fetch(`${DASHBOARD_API_BASE}/user`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch user dashboard: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 管理员仪表板数据钩子
 */
export function useAdminDashboard() {
  const [data, setData] = useState<AdminDashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const result = await fetchAdminDashboard()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchData()
  }, [fetchData])

  return {
    data,
    isLoading,
    error,
    refetch: fetchData,
  }
}

/**
 * 用户仪表板数据钩子
 */
export function useUserDashboard() {
  const [data, setData] = useState<UserDashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const result = await fetchUserDashboard()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchData()
  }, [fetchData])

  return {
    data,
    isLoading,
    error,
    refetch: fetchData,
  }
}

/**
 * 导出仪表板数据 (CSV)
 */
export async function exportDashboardData(type: "admin" | "user"): Promise<void> {
  const response = await fetch(`${DASHBOARD_API_BASE}/export/${type}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to export dashboard data: ${response.statusText}`)
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `dashboard-${type}-${new Date().toISOString().split("T")[0]}.csv`
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}