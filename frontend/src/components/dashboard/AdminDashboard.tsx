"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

import { useAdminDashboard } from "./hooks"

export function AdminDashboard({ className }: { className?: string }) {
  const { data: metrics, isLoading, error } = useAdminDashboard()

  if (isLoading) {
    return (
      <div className={`p-6 bg-gray-50 rounded-lg ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error || !metrics) {
    return (
      <div className={`p-6 bg-red-50 rounded-lg border border-red-200 ${className}`}>
        <p className="text-red-700 font-semibold">Error loading dashboard</p>
        <p className="text-red-600 text-sm">{error instanceof Error ? error.message : "Unknown error"}</p>
      </div>
    )
  }

  // Now metrics is guaranteed to be defined
  const m = metrics

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{m.total_users}</div>
            <p className="text-xs text-gray-500 mt-1">Active Sessions: {m.active_users}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">API Calls Today</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{m.api_calls_today}</div>
            <p className="text-xs text-gray-500 mt-1">Error: {(m.error_rate * 100).toFixed(2)}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Cache Hit Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{(m.cache_hit_rate * 100).toFixed(1)}%</div>
            <p className="text-xs text-gray-500 mt-1">Avg Response: {m.avg_response_time}ms</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Cost</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">${m.total_cost.toFixed(2)}</div>
            <p className="text-xs text-gray-500 mt-1">Monthly estimate</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">System Overview</TabsTrigger>
          <TabsTrigger value="topUsers">Top Users</TabsTrigger>
          <TabsTrigger value="systemMetrics">System Metrics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle>System Overview</CardTitle>
              <CardDescription>Overall system performance indicators</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Error Rate</span>
                  <div className="flex items-center">
                    <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${Math.min(m.error_rate * 100, 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold">{(m.error_rate * 100).toFixed(2)}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Cache Hit Rate</span>
                  <div className="flex items-center">
                    <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${m.cache_hit_rate * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold">{(m.cache_hit_rate * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="topUsers">
          <Card>
            <CardHeader>
              <CardTitle>Top Users</CardTitle>
              <CardDescription>Users with highest API usage</CardDescription>
            </CardHeader>
            <CardContent>
              {m.top_users && m.top_users.length > 0 ? (
                <div className="space-y-4">
                  {m.top_users.map((user, idx) => (
                    <div key={user.id} className="flex items-center justify-between border-b pb-4 last:border-b-0">
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-sm font-semibold">
                          #{idx + 1}
                        </div>
                        <div>
                          <p className="font-medium">{user.name ?? user.id}</p>
                          <p className="text-sm text-gray-500">{user.id}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{user.api_calls}</p>
                        <p className="text-sm text-gray-500">Cost: ${user.cost?.toFixed(2) ?? "0.00"}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="systemMetrics">
          <Card>
            <CardHeader>
              <CardTitle>System Metrics</CardTitle>
              <CardDescription>Detailed system performance metrics</CardDescription>
            </CardHeader>
            <CardContent>
              {m.system_metrics && m.system_metrics.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {m.system_metrics.map((metric) => (
                    <div key={metric.name} className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-2">{metric.name}</p>
                      <p className="text-2xl font-bold">
                        {metric.value.toFixed(2)} <span className="text-sm text-gray-500">{metric.status ? `(${metric.status})` : ""}</span>
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No metrics available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
