/**
 * React Query hooks for Dashboard data fetching with caching
 */

import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useCallback } from "react"

// API endpoints
const ADMIN_DASHBOARD_ENDPOINT = "/api/dashboard/admin"
const USER_DASHBOARD_ENDPOINT = "/api/dashboard/user"

// Query keys
export const dashboardQueryKeys = {
  admin: ["dashboard", "admin"] as const,
  user: ["dashboard", "user"] as const,
}

// Types matching backend responses
export interface AdminDashboardData {
  total_users: number
  active_users: number
  api_calls_today: number
  error_rate: number
  system_health: number
  cache_hit_rate: number
  total_cost: number
  avg_response_time: number
  system_metrics: Array<{
    name: string
    value: number
    status?: string
  }>
  recent_errors: Array<{
    type: string
    count: number
    last_seen: string
  }>
  top_users: Array<{
    id: string
    name?: string
    api_calls: number
    cost: number
  }>
}

export interface UserDashboardData {
  tool_executions: number
  success_rate: number
  cache_hit_rate: number
  storage_used: number
  storage_quota: number
  api_quota: number
  api_used: number
  avg_response_time: number
  api_usage: Array<{
    period: string
    used: number
    quota: number
  }>
  top_tools: Array<{
    tool_name: string
    execution_count: number
    success_rate: number
    avg_time: number
  }>
  recent_activity: Array<{
    id: string
    action: string
    tool_name?: string
    status: string
    created_at: string
  }>
}

// Fetch functions
async function fetchAdminDashboard(): Promise<AdminDashboardData> {
  const response = await fetch(ADMIN_DASHBOARD_ENDPOINT, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch admin dashboard: ${response.statusText}`)
  }

  return response.json()
}

async function fetchUserDashboard(): Promise<UserDashboardData> {
  const response = await fetch(USER_DASHBOARD_ENDPOINT, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch user dashboard: ${response.statusText}`)
  }

  return response.json()
}

// Hook for admin dashboard with caching
export function useAdminDashboard(options: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: dashboardQueryKeys.admin,
    queryFn: fetchAdminDashboard,
    enabled: options.enabled ?? true,
    staleTime: 30_000, // 30 seconds
    gcTime: 5 * 60_000, // 5 minutes (cacheTime in v4, gcTime in v5)
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 1,
  })
}

// Hook for user dashboard with caching
export function useUserDashboard(options: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: dashboardQueryKeys.user,
    queryFn: fetchUserDashboard,
    enabled: options.enabled ?? true,
    staleTime: 30_000, // 30 seconds
    gcTime: 5 * 60_000, // 5 minutes (cacheTime in v4, gcTime in v5)
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 1,
  })
}

// Hook to manually refresh dashboard data
export function useRefreshDashboard() {
  const queryClient = useQueryClient()

  return useCallback(() => {
    void Promise.all([
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.admin }),
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.user }),
    ])
  }, [queryClient])
}

// Hook to prefetch dashboard data (useful for navigation)
export function usePrefetchDashboard() {
  const queryClient = useQueryClient()

  return {
    prefetchAdmin: useCallback(() => {
      void queryClient.prefetchQuery({
        queryKey: dashboardQueryKeys.admin,
        queryFn: fetchAdminDashboard,
      })
    }, [queryClient]),
    prefetchUser: useCallback(() => {
      void queryClient.prefetchQuery({
        queryKey: dashboardQueryKeys.user,
        queryFn: fetchUserDashboard,
      })
    }, [queryClient]),
  }
}
