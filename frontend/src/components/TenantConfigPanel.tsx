"use client"

import { AlertCircle, CheckCircle, Loader2, Save } from "lucide-react"
import { useEffect, useState } from "react"

import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useCurrentTenant, tenantAPI } from "@/core/api/tenants"

/**
 * 租户配置面板组件
 *
 * 功能：
 * - 显示当前租户的配置信息
 * - 允许编辑租户名称和描述
 * - 管理租户设置和偏好
 * - 保存配置更改
 */
export function TenantConfigPanel() {
  const { currentTenant, isLoading: isLoadingTenant } = useCurrentTenant()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // 表单状态
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  })

  // 初始化表单数据
  useEffect(() => {
    if (currentTenant) {
      setFormData({
        name: currentTenant.name,
        description: currentTenant.description ?? "",
      })
    }
  }, [currentTenant])

  /**
   * 处理输入变化
   */
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  /**
   * 保存配置
   */
  const handleSave = async () => {
    if (!currentTenant) {
      setError("未选择租户")
      return
    }

    try {
      setIsSaving(true)
      setError(null)
      setSuccess(false)

      // 调用 API 更新租户
      await tenantAPI.updateTenant(currentTenant.id, {
        name: formData.name,
        description: formData.description,
      })

      setSuccess(true)
      setIsEditing(false)

      // 3 秒后清除成功消息
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "保存配置失败"
      setError(errorMessage)
      console.error("Error saving tenant config:", err)
    } finally {
      setIsSaving(false)
    }
  }

  /**
   * 取消编辑
   */
  const handleCancel = () => {
    // 恢复原始值
    if (currentTenant) {
      setFormData({
        name: currentTenant.name,
        description: currentTenant.description ?? "",
      })
    }
    setIsEditing(false)
  }

  if (isLoadingTenant) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-white p-8">
        <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
        <span className="ml-2 text-sm text-gray-600">加载租户配置中...</span>
      </div>
    )
  }

  if (!currentTenant) {
    return (
      <Alert className="rounded-lg border-yellow-200 bg-yellow-50">
        <AlertCircle className="h-4 w-4 text-yellow-600" />
        <AlertDescription className="text-yellow-800">
          未找到当前租户，请先选择租户
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="w-full rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {/* 标题 */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">租户配置</h2>
        <p className="mt-1 text-sm text-gray-600">
          管理 {currentTenant.name} 的设置和偏好
        </p>
      </div>

      {/* 成功消息 */}
      {success && (
        <Alert className="mb-4 border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            配置已成功保存
          </AlertDescription>
        </Alert>
      )}

      {/* 错误消息 */}
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 配置表单 */}
      <div className="space-y-6">
        {/* 租户ID（只读） */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            租户ID
          </label>
          <Input
            type="text"
            value={currentTenant.id}
            disabled
            className="mt-1 bg-gray-50 text-gray-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            唯一标识符，无法修改
          </p>
        </div>

        {/* 租户名称 */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            租户名称 *
          </label>
          <Input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            disabled={!isEditing}
            placeholder="输入租户名称"
            className="mt-1"
          />
          <p className="mt-1 text-xs text-gray-500">
            租户的显示名称
          </p>
        </div>

        {/* 租户描述 */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            描述
          </label>
          <Textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            disabled={!isEditing}
            placeholder="输入租户描述（可选）"
            rows={4}
            className="mt-1"
          />
          <p className="mt-1 text-xs text-gray-500">
            关于此租户的更多信息
          </p>
        </div>

        {/* 租户状态 */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            状态
          </label>
          <div className="mt-1 flex items-center space-x-3">
            <div
              className={`h-3 w-3 rounded-full ${
                currentTenant.status === "active"
                  ? "bg-green-500"
                  : "bg-gray-400"
              }`}
            />
            <span className="text-sm text-gray-700">
              {currentTenant.status === "active" ? "活跃" : "非活跃"}
            </span>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            当前租户的运营状态
          </p>
        </div>

        {/* 创建时间 */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            创建时间
          </label>
          <Input
            type="text"
            value={new Date(currentTenant.createdAt).toLocaleString()}
            disabled
            className="mt-1 bg-gray-50 text-gray-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            租户创建的时间
          </p>
        </div>

        {/* 操作按钮 */}
        <div className="flex justify-end space-x-3 border-t border-gray-200 pt-6">
          {!isEditing ? (
            <Button
              onClick={() => setIsEditing(true)}
              variant="default"
              className="bg-blue-600 text-white hover:bg-blue-700"
            >
              编辑配置
            </Button>
          ) : (
            <>
              <Button
                onClick={handleCancel}
                variant="outline"
                className="border-gray-300"
              >
                取消
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving}
                className="bg-green-600 text-white hover:bg-green-700"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    保存配置
                  </>
                )}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* 附加信息 */}
      <div className="mt-8 rounded-lg bg-blue-50 p-4">
        <h3 className="mb-2 text-sm font-semibold text-blue-900">提示</h3>
        <ul className="space-y-1 text-xs text-blue-800">
          <li>• 租户ID 是唯一的，无法修改</li>
          <li>• 修改租户配置后，需要重新加载应用以应用更改</li>
          <li>• 租户的状态只能由管理员修改</li>
        </ul>
      </div>
    </div>
  )
}
