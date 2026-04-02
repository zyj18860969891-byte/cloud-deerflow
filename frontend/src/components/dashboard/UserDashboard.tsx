"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

import { useUserDashboard } from "./hooks"

export function UserDashboard({ className }: { className?: string }) {
  const { data: metrics, isLoading, error } = useUserDashboard()

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

  const storagePercentage = (m.storage_used / m.storage_quota) * 100
  const quotaPercentage = (m.api_used / m.api_quota) * 100
  const successRate = m.success_rate

  const getStorageColor = (percentage: number) => {
    if (percentage >= 90) return "bg-red-500"
    if (percentage >= 75) return "bg-yellow-500"
    return "bg-green-500"
  }

  const getQuotaColor = (percentage: number) => {
    if (percentage >= 90) return "bg-red-500"
    if (percentage >= 75) return "bg-yellow-500"
    return "bg-green-500"
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Executions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{m.tool_executions}</div>
            <p className="text-xs text-gray-500 mt-1">Cache Hit Rate: {(m.success_rate * 100).toFixed(1)}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Cache Hit Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{m.cache_hit_rate.toFixed(1)}%</div>
            <p className="text-xs text-gray-500 mt-1">Hit Rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Storage Used</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{(m.storage_used / 1024 / 1024).toFixed(1)} MB</div>
            <p className="text-xs text-gray-500 mt-1">of {(m.storage_quota / 1024 / 1024 / 1024).toFixed(1)} GB</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Avg Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{m.avg_response_time} ms</div>
            <p className="text-xs text-gray-500 mt-1">Success Rate: {successRate.toFixed(1)}%</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">API Quota</CardTitle>
            <CardDescription>Your API usage and limits</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">{m.api_used}</span>
                <span className="text-sm text-gray-500">{m.api_quota}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`${getQuotaColor(quotaPercentage)} h-3 rounded-full transition-all`}
                  style={{ width: `${Math.min(quotaPercentage, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">{quotaPercentage.toFixed(1)}% used</p>
            </div>
            {quotaPercentage >= 80 && (
              <Button className="w-full" variant="outline" size="sm">
                Upgrade Quota
              </Button>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Storage Quota</CardTitle>
            <CardDescription>Your storage usage and limits</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">{(m.storage_used / 1024 / 1024).toFixed(1)} MB</span>
                <span className="text-sm text-gray-500">{(m.storage_quota / 1024 / 1024 / 1024).toFixed(1)} GB</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`${getStorageColor(storagePercentage)} h-3 rounded-full transition-all`}
                  style={{ width: `${Math.min(storagePercentage, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">{storagePercentage.toFixed(1)}% used</p>
            </div>
            {storagePercentage >= 80 && (
              <Button className="w-full" variant="outline" size="sm">
                Upgrade Storage
              </Button>
            )}
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="usage" className="w-full">
        <TabsList>
          <TabsTrigger value="usage">Usage by Period</TabsTrigger>
          <TabsTrigger value="topTools">Top Tools Used</TabsTrigger>
        </TabsList>

        <TabsContent value="usage">
          <Card>
            <CardHeader>
              <CardTitle>Usage History</CardTitle>
              <CardDescription>Your API usage over time</CardDescription>
            </CardHeader>
            <CardContent>
              {m.api_usage && m.api_usage.length > 0 ? (
                <div className="space-y-4">
                  {m.api_usage.map((period, idx) => (
                    <div key={idx} className="flex items-center justify-between border-b pb-4 last:border-b-0">
                      <div>
                        <p className="font-medium">{period.period}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600">{period.used} executions</p>
                        <p className="font-semibold">Quota: {period.quota}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No usage data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="topTools">
          <Card>
            <CardHeader>
              <CardTitle>Most Used Tools</CardTitle>
              <CardDescription>Your most frequently used tools</CardDescription>
            </CardHeader>
            <CardContent>
              {m.top_tools && m.top_tools.length > 0 ? (
                <div className="space-y-4">
                  {m.top_tools.map((tool, idx) => (
                    <div key={tool.tool_name} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-xs font-semibold text-blue-600">
                            {idx + 1}
                          </div>
                          <div>
                            <p className="font-semibold">{tool.tool_name}</p>
                            <p className="text-xs text-gray-500">{tool.execution_count} executions</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold">{(tool.success_rate * 100).toFixed(1)}%</p>
                          <p className="text-xs text-gray-500">success</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">Avg time: {tool.avg_time.toFixed(0)}ms</span>
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${tool.success_rate * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No tool data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
