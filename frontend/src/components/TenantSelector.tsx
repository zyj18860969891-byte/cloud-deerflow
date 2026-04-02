"use client"

import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react"
import { useState } from "react"

import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useTenants, useCurrentTenant, tenantAPI } from "@/core/api/tenants"

/**
 * 租户选择器组件
 * 
 * 功能：
 * - 显示当前租户信息
 * - 列出所有可用的租户
 * - 允许用户切换租户
 * - 显示租户状态和详细信息
 * 
 * 使用 React Hooks 和自定义 API 钩子
 */
export function TenantSelector() {
  const { tenants, isLoading, error, refetch } = useTenants()
  const { currentTenant } = useCurrentTenant()
  const [isSwitching, setIsSwitching] = useState(false)
  const [switchError, setSwitchError] = useState<string | null>(null)

  /**
   * 切换租户
   */
  const handleSwitchTenant = async (tenantId: string) => {
    try {
      setIsSwitching(true)
      setSwitchError(null)

      // 使用 API 客户端切换租户
      const result = await tenantAPI.switchTenant(tenantId)

      // 重新获取租户列表以更新状态
      await refetch()

      // 可选：显示成功消息
      console.log(`成功切换到租户: ${result.name}`)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "租户切换失败"
      setSwitchError(errorMessage)
      console.error("Error switching tenant:", err)
    } finally {
      setIsSwitching(false)
    }
  }

  return (
    <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      {/* 标题 */}
      <h2 className="mb-4 text-lg font-semibold text-gray-900">租户选择</h2>

      {/* 错误消息 */}
      {(error ?? switchError) && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error instanceof Error ? error.message : String(error ?? switchError)}
          </AlertDescription>
        </Alert>
      )}

      {/* 加载状态 */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
          <span className="ml-2 text-sm text-gray-600">加载租户列表中...</span>
        </div>
      )}

      {/* 租户列表 */}
      {!isLoading && tenants.length > 0 && (
        <>
          {/* 当前租户信息 */}
          {currentTenant && (
            <div className="mb-4 rounded-lg bg-blue-50 p-3">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-600">当前租户</p>
                  <p className="mt-1 font-semibold text-blue-900">
                    {currentTenant.name}
                  </p>
                  {currentTenant.description && (
                    <p className="mt-1 text-xs text-gray-700">
                      {currentTenant.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center">
                  {currentTenant.status === "active" ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-600" />
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 租户选择下拉菜单 */}
          <div className="mb-4">
            <label className="block text-xs font-medium text-gray-700">
              切换租户
            </label>
            <Select value={currentTenant?.id ?? ""} disabled={isSwitching}>
              <SelectTrigger className="mt-2">
                <SelectValue placeholder="选择租户..." />
              </SelectTrigger>
              <SelectContent>
                {tenants.map((tenant) => (
                  <SelectItem key={tenant.id} value={tenant.id}>
                    {tenant.name}{" "}
                    {tenant.status === "active" ? "✓" : "(停用)"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 租户列表 */}
          <div className="mb-4">
            <p className="mb-2 text-xs font-medium text-gray-700">
              所有租户 ({tenants.length})
            </p>
            <div className="space-y-2">
              {tenants.map((tenant) => (
                <div
                  key={tenant.id}
                  className={`flex items-center justify-between rounded-lg border p-2 transition-colors ${
                    currentTenant?.id === tenant.id
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {tenant.name}
                    </p>
                    <p className="text-xs text-gray-500">ID: {tenant.id}</p>
                  </div>
                  <Button
                    variant={
                      currentTenant?.id === tenant.id ? "default" : "outline"
                    }
                    size="sm"
                    onClick={() => handleSwitchTenant(tenant.id)}
                    disabled={isSwitching || tenant.status === "inactive"}
                  >
                    {currentTenant?.id === tenant.id ? "当前" : "切换"}
                  </Button>
                </div>
              ))}
            </div>
          </div>

          {/* 租户统计信息 */}
          <div className="border-t pt-3">
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="rounded bg-gray-50 p-2">
                <p className="text-gray-600">活跃租户</p>
                  <p className="mt-1 text-lg font-bold text-gray-900">
                  {tenants.filter((t) => t.status === "active").length ?? 0}
                </p>
              </div>
              <div className="rounded bg-gray-50 p-2">
                <p className="text-gray-600">停用租户</p>
                <p className="mt-1 text-lg font-bold text-gray-900">
                  {tenants.filter((t) => t.status === "inactive").length}
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* 空状态 */}
      {!isLoading && tenants.length === 0 && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            暂无可用的租户。请联系管理员。
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
